import re

def extract_facts(observation_text, game):
    """
    Turn a raw observation string + current game state into a structured
    dictionary of facts. This is our 'Extractor' — no LLM needed here
    because our mini-engine's output is predictable.
    """
    current_room_name = game.current_room
    room_data = game.rooms[current_room_name]

    facts = {
        "room": current_room_name,
        "objects_in_room": list(room_data["objects"]),
        "exits": list(room_data["exits"].keys()),
        "inventory": list(game.inventory),
        "raw_text": observation_text,
    }
    return facts


if __name__ == "__main__":
    from game_engine import MiniWorld

    game = MiniWorld()
    obs = game.reset()
    facts = extract_facts(obs, game)
    print(facts)

    obs = game.step("take apple")
    facts = extract_facts(obs, game)
    print(facts)
    