"""Agent service for AI-powered text editing."""
import json
import os
from typing import AsyncIterator, Optional

AGENT_SYSTEM_PROMPT = """You are an expert writing editor. 
The user will give you a passage and an editing instruction.
Return ONLY the edited text, nothing else. No explanations, no markdown code blocks.
Preserve the original tone and style unless asked to change it."""

REVISE_SYSTEM_PROMPT = """You are an expert writing editor.
The user previously asked you to edit some text, and you provided a suggestion.
Now they want you to revise your suggestion based on additional feedback.
Return ONLY the revised text, nothing else. No explanations, no markdown code blocks."""


class PendingEdit:
    """Holds info about a pending edit."""
    def __init__(
        self,
        original_content: str,
        selection_start: int,
        selection_end: int,
        original_text: str,
        current_suggestion: str,
        prompt_history: list[str],
    ):
        self.original_content = original_content
        self.selection_start = selection_start
        self.selection_end = selection_end
        self.original_text = original_text
        self.current_suggestion = current_suggestion
        self.prompt_history = prompt_history


class AgentSession:
    """Holds the current editing session state."""
    
    def __init__(self):
        self.pending_edits: dict[str, PendingEdit] = {}
    
    def store_pending(self, session_id: str, edit: PendingEdit):
        self.pending_edits[session_id] = edit
    
    def get_pending(self, session_id: str) -> Optional[PendingEdit]:
        return self.pending_edits.get(session_id)
    
    def clear_pending(self, session_id: str):
        self.pending_edits.pop(session_id, None)


# Global session store
agent_sessions = AgentSession()


async def get_edit_suggestion(
    content: str,
    selection_start: int,
    selection_end: int,
    prompt: str,
    provider: str = "anthropic",
    book_slug: str = "",
    chapter_slug: str = "",
) -> AsyncIterator[str]:
    """
    Stream initial edit suggestion using Copilot CLI.
    """
    import uuid
    
    selected_text = content[selection_start:selection_end]
    session_id = str(uuid.uuid4())
    
    # Extract context: chapter title and current section
    context = _extract_context(content, selection_start, selection_end)
    
    replacement = ""
    
    # Always use Copilot CLI (no API keys needed)
    async for event, text in _stream_initial_edit(selected_text, prompt, provider, context):
        if text:
            replacement = text
        yield event
    
    # Store pending edit for approval or revision
    agent_sessions.store_pending(session_id, PendingEdit(
        original_content=content,
        selection_start=selection_start,
        selection_end=selection_end,
        original_text=selected_text,
        current_suggestion=replacement,
        prompt_history=[prompt],
    ))
    
    yield f"event: session\ndata: {json.dumps({'sessionId': session_id})}\n\n"


async def revise_suggestion(
    session_id: str,
    revision_prompt: str,
    provider: str = "anthropic",
) -> AsyncIterator[str]:
    """
    Revise an existing suggestion based on additional feedback.
    """
    pending = agent_sessions.get_pending(session_id)
    if not pending:
        yield f"event: error\ndata: {json.dumps({'error': 'Session not found'})}\n\n"
        return
    
    replacement = ""
    
    # Always use Copilot CLI
    async for event, text in _stream_revision(
        pending.original_text,
        pending.current_suggestion,
        pending.prompt_history,
        revision_prompt,
        provider,
    ):
        if text:
            replacement = text
        yield event
    
    # Update the pending edit
    pending.current_suggestion = replacement
    pending.prompt_history.append(revision_prompt)
    
    yield f"event: session\ndata: {json.dumps({'sessionId': session_id})}\n\n"


def apply_edit(session_id: str) -> Optional[str]:
    """
    Apply a pending edit and return the new full content.
    """
    pending = agent_sessions.get_pending(session_id)
    if not pending:
        return None
    
    # Apply the edit
    new_content = (
        pending.original_content[:pending.selection_start] +
        pending.current_suggestion +
        pending.original_content[pending.selection_end:]
    )
    
    # Clear the session
    agent_sessions.clear_pending(session_id)
    
    return new_content


def _extract_context(content: str, selection_start: int, selection_end: int) -> dict:
    """Extract contextual information around the selection."""
    lines = content[:selection_start].split('\n')
    
    chapter_title = ""
    section_heading = ""
    
    # Find chapter title (first # heading)
    for line in content.split('\n'):
        if line.startswith('# '):
            chapter_title = line[2:].strip()
            break
    
    # Find current section (nearest ## or ### heading before selection)
    for line in reversed(lines):
        if line.startswith('## ') or line.startswith('### '):
            section_heading = line.lstrip('#').strip()
            break
    
    # Get some surrounding context (200 chars before and after)
    context_start = max(0, selection_start - 200)
    context_end = min(len(content), selection_end + 200)
    surrounding_text = content[context_start:context_end]
    
    return {
        'chapter_title': chapter_title,
        'section_heading': section_heading,
        'surrounding_text': surrounding_text,
    }


async def _stream_initial_edit(
    selected_text: str,
    prompt: str,
    provider: str,
    context: dict,
) -> AsyncIterator[tuple[str, Optional[str]]]:
    """Stream initial edit using Codex CLI."""
    import asyncio
    
    # Construct the prompt with context
    context_info = []
    if context.get('chapter_title'):
        context_info.append(f"Chapter: {context['chapter_title']}")
    if context.get('section_heading'):
        context_info.append(f"Section: {context['section_heading']}")
    
    context_str = "\n".join(context_info)
    
    full_prompt = f'''{AGENT_SYSTEM_PROMPT}

{context_str}

Edit this text: "{selected_text}"

Instruction: {prompt}'''
    
    try:
        # Call codex CLI in non-interactive mode (uses default gpt-5.2)
        process = await asyncio.create_subprocess_exec(
            'codex',
            'exec',
            '-',  # Read from stdin
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,  # Merge stderr into stdout
            stdin=asyncio.subprocess.PIPE,
        )
        
        # Send prompt to stdin
        if process.stdin:
            process.stdin.write(full_prompt.encode('utf-8'))
            await process.stdin.drain()
            process.stdin.close()
        
        full_response = ""
        all_output = []
        
        # Collect all output first
        if process.stdout:
            async for line in process.stdout:
                line_str = line.decode('utf-8', errors='ignore')
                all_output.append(line_str)
        
        await process.wait()
        
        # Parse output: find lines between "codex" and "tokens used"
        capturing = False
        for line_str in all_output:
            stripped = line_str.strip()
            
            if stripped == 'codex':
                capturing = True
                continue
            
            if 'tokens used' in stripped.lower():
                break
            
            if capturing and stripped:
                full_response += line_str
                yield f"event: delta\ndata: {json.dumps({'text': line_str})}\n\n", None
        
        # Clean up response
        full_response = full_response.strip()
        
        if not full_response:
            # Fallback: take last non-empty line before "tokens used"
            for line_str in reversed(all_output):
                stripped = line_str.strip()
                if stripped and 'tokens used' not in stripped.lower() and stripped != 'codex':
                    full_response = stripped
                    break
        
        yield f"event: done\ndata: {json.dumps({'replacement': full_response})}\n\n", full_response
        
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n", None


async def _stream_revision(
    original_text: str,
    current_suggestion: str,
    prompt_history: list[str],
    revision_prompt: str,
    provider: str,
) -> AsyncIterator[tuple[str, Optional[str]]]:
    """Stream revised suggestion using Codex CLI."""
    import asyncio
    
    # Build context with history
    history_text = "\n".join(f"- {p}" for p in prompt_history)
    
    full_prompt = f'''{REVISE_SYSTEM_PROMPT}

Original text: "{original_text}"

Previous instructions:
{history_text}

Your previous suggestion: "{current_suggestion}"

New feedback: {revision_prompt}

Please provide a revised version:'''
    
    try:
        process = await asyncio.create_subprocess_exec(
            'codex',
            'exec',
            '-',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            stdin=asyncio.subprocess.PIPE,
        )
        
        if process.stdin:
            process.stdin.write(full_prompt.encode('utf-8'))
            await process.stdin.drain()
            process.stdin.close()
        
        full_response = ""
        all_output = []
        
        if process.stdout:
            async for line in process.stdout:
                line_str = line.decode('utf-8', errors='ignore')
                all_output.append(line_str)
        
        await process.wait()
        
        # Parse output
        capturing = False
        for line_str in all_output:
            stripped = line_str.strip()
            
            if stripped == 'codex':
                capturing = True
                continue
            
            if 'tokens used' in stripped.lower():
                break
            
            if capturing and stripped:
                full_response += line_str
                yield f"event: delta\ndata: {json.dumps({'text': line_str})}\n\n", None
        
        full_response = full_response.strip()
        
        if not full_response:
            for line_str in reversed(all_output):
                stripped = line_str.strip()
                if stripped and 'tokens used' not in stripped.lower() and stripped != 'codex':
                    full_response = stripped
                    break
        
        yield f"event: done\ndata: {json.dumps({'replacement': full_response})}\n\n", full_response
        
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n", None


async def _mock_stream(selected_text: str, prompt: str) -> AsyncIterator[tuple[str, Optional[str]]]:
    """Mock streaming for development."""
    import asyncio
    
    prompt_lower = prompt.lower()
    
    if "concise" in prompt_lower or "shorter" in prompt_lower:
        words = selected_text.split()
        mock_response = " ".join(words[:max(len(words)//2, 3)])
    elif "expand" in prompt_lower or "longer" in prompt_lower:
        mock_response = selected_text + " Additionally, this point deserves further exploration."
    else:
        mock_response = f"[Edited] {selected_text}"
    
    words = mock_response.split()
    full_text = ""
    
    for i, word in enumerate(words):
        chunk = word + (" " if i < len(words) - 1 else "")
        full_text += chunk
        yield f"event: delta\ndata: {json.dumps({'text': chunk})}\n\n", None
        await asyncio.sleep(0.05)
    
    yield f"event: done\ndata: {json.dumps({'replacement': full_text})}\n\n", full_text


async def _mock_revision(
    original_text: str,
    current_suggestion: str,
    revision_prompt: str,
) -> AsyncIterator[tuple[str, Optional[str]]]:
    """Mock revision streaming for development."""
    import asyncio
    
    # Simple mock: modify the current suggestion based on revision
    prompt_lower = revision_prompt.lower()
    
    if "shorter" in prompt_lower:
        words = current_suggestion.split()
        mock_response = " ".join(words[:max(len(words)//2, 2)])
    elif "longer" in prompt_lower:
        mock_response = current_suggestion + " [expanded further]"
    else:
        mock_response = f"[Revised] {current_suggestion}"
    
    words = mock_response.split()
    full_text = ""
    
    for i, word in enumerate(words):
        chunk = word + (" " if i < len(words) - 1 else "")
        full_text += chunk
        yield f"event: delta\ndata: {json.dumps({'text': chunk})}\n\n", None
        await asyncio.sleep(0.05)
    
    yield f"event: done\ndata: {json.dumps({'replacement': full_text})}\n\n", full_text
