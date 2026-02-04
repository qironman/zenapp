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
) -> AsyncIterator[str]:
    """
    Stream initial edit suggestion using Copilot CLI.
    """
    import uuid
    
    selected_text = content[selection_start:selection_end]
    session_id = str(uuid.uuid4())
    
    replacement = ""
    
    # Always use Copilot CLI (no API keys needed)
    async for event, text in _stream_initial_edit(selected_text, prompt, provider):
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


async def _stream_initial_edit(
    selected_text: str,
    prompt: str,
    provider: str,
) -> AsyncIterator[tuple[str, Optional[str]]]:
    """Stream initial edit using Copilot CLI."""
    import asyncio
    
    # Use Copilot CLI instead of API keys
    model = "claude-sonnet-4.5" if provider == "anthropic" else "gpt-5.2-codex"
    
    # Construct the prompt for Copilot
    full_prompt = f'{AGENT_SYSTEM_PROMPT}\n\nEdit this text: "{selected_text}"\n\nInstruction: {prompt}'
    
    try:
        # Call copilot CLI in non-interactive mode
        process = await asyncio.create_subprocess_exec(
            'copilot',
            '-p', full_prompt,
            '--model', model,
            '--silent',
            '--allow-all',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        full_response = ""
        
        # Stream output
        if process.stdout:
            async for line in process.stdout:
                chunk = line.decode('utf-8')
                if chunk:
                    full_response += chunk
                    yield f"event: delta\ndata: {json.dumps({'text': chunk})}\n\n", None
        
        await process.wait()
        
        # Clean up response (remove trailing newlines)
        full_response = full_response.strip()
        
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
    """Stream revised suggestion using Copilot CLI."""
    import asyncio
    
    model = "claude-sonnet-4.5" if provider == "anthropic" else "gpt-5.2-codex"
    
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
            'copilot',
            '-p', full_prompt,
            '--model', model,
            '--silent',
            '--allow-all',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        full_response = ""
        
        if process.stdout:
            async for line in process.stdout:
                chunk = line.decode('utf-8')
                if chunk:
                    full_response += chunk
                    yield f"event: delta\ndata: {json.dumps({'text': chunk})}\n\n", None
        
        await process.wait()
        
        full_response = full_response.strip()
        
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
