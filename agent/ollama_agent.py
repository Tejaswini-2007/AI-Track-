"""
Ollama Agent
--------------
Sends the current world slice + objective to a local LLM (via Ollama) and
gets back a single action. Critically: NO conversation history is ever sent -
only the current slice, fresh each step. The agent is a pure function of
(objective, world_slice).
"""

import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

VALID_ACTIONS_HINT = (
    "Valid action formats: 'go <direction>', 'pick up key', 'unlock door', 'look'. "
    "Respond with ONLY the action, nothing else. No explanation."
)


def get_next_action(world_slice: str, objective: str) -> str:
    prompt = (
        f"You are an agent exploring a house. Your objective: {objective}.\n"
        f"Current situation: {world_slice}\n"
        f"Rules: If a door is locked and you are carrying a key, you must "
        f"'unlock door' BEFORE trying to go through it. If a door is locked "
        f"and you do NOT have a key, do not repeat the same blocked action - "
        f"instead explore a different direction to search for one. "
        f"ALWAYS prefer going through an exit marked UNEXPLORED over one marked "
        f"'already visited' - do not go back and forth between the same two rooms.\n"
        f"{VALID_ACTIONS_HINT}\n"
        f"Action:"
    )

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    })

    raw = response.json()["response"].strip()

    # Clean up: take just the first line, strip quotes/punctuation
    action = raw.split("\n")[0].strip()
    action = re.sub(r'^["\'>\-\s]+|["\'.\s]+$', "", action)
    action = action.lower()

    return action