import requests


def build_context(facts):
    valid_actions = []
    for direction in facts['exits']:
        valid_actions.append(f"go {direction}")
    for obj in facts['objects_in_room']:
        valid_actions.append(f"take {obj}")
    valid_actions.append("look")

    context = f"""You are an agent exploring a text adventure game. Your goal is to EXPLORE new rooms and COLLECT objects. Avoid repeating "look" if other options exist.

Current room: {facts['room']}
Objects in this room: {', '.join(facts['objects_in_room']) if facts['objects_in_room'] else 'none'}
Your inventory: {', '.join(facts['inventory']) if facts['inventory'] else 'empty'}

Valid actions this turn (pick exactly ONE, copy it exactly):
{chr(10).join('- ' + a for a in valid_actions)}

Respond with ONLY the action text, nothing else."""
    return context


def decide_action(facts):
    prompt = build_context(facts)

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma2:2b",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()
    action = result["response"].strip().lower()
    return action


if __name__ == "__main__":
    from game_engine import MiniWorld
    from extractor import extract_facts

    game = MiniWorld()
    obs = game.reset()
    facts = extract_facts(obs, game)

    print("Context sent to LLM:\n")
    print(build_context(facts))

    print("\nLLM's chosen action:")
    action = decide_action(facts)
    print(action)