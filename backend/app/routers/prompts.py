# API router for prompt templates

from fastapi import APIRouter
from typing import List
import os

router = APIRouter()

PROMPTS_FILE = os.path.join(os.path.dirname(__file__), '../../data/prompts.md')

@router.get('/prompts', response_model=List[str])
async def get_prompts():
    """Get list of pre-defined prompts from prompts.md"""
    if not os.path.exists(PROMPTS_FILE):
        return []
    
    with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse prompts - each non-empty line that's not a heading is a prompt
    prompts = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            prompts.append(line)
    
    return prompts

@router.post('/prompts')
async def save_prompts(prompts: List[str]):
    """Save prompts to prompts.md"""
    # Write prompts as markdown list
    content = "# AI Edit Prompts\n\n"
    content += "\n\n".join(prompts)
    
    with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return {"status": "saved", "count": len(prompts)}
