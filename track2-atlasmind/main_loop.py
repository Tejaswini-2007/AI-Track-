import matplotlib.pyplot as plt
plt.ion()
import time
from game_engine import MiniWorld
from extractor import extract_facts
from world_model import WorldModel
from reasoning_agent import decide_action


def pick_fallback_action(facts):
    for obj in facts["objects_in_room"]:
        return f"take {obj}"
    if facts["exits"]:
        return f"go {facts['exits'][0]}"
    return "look"


def run(num_turns=10):
    game = MiniWorld()
    world = WorldModel()

    obs = game.reset()
    print(f"[TURN 0] {obs}\n")

    last_room = None
    last_inventory = None
    stall_count = 0

    for turn in range(1, num_turns + 1):
        facts = extract_facts(obs, game)
        world.update_from_facts(facts)
        world.draw_live(turn)

        action = decide_action(facts)

        if facts["room"] == last_room and facts["inventory"] == last_inventory:
            stall_count += 1
        else:
            stall_count = 0

        if stall_count >= 2:
            action = pick_fallback_action(facts)
            print(f"[TURN {turn}] (agent stalled, using fallback) -> '{action}'")
        else:
            print(f"[TURN {turn}] Agent thinks: '{action}'")

        last_room = facts["room"]
        last_inventory = list(facts["inventory"])

        obs = game.step(action)
        print(f"           Result: {obs}\n")

        time.sleep(0.5)

    print("=== FINAL WORLD MODEL ===")
    world.describe()
    plt.show()


if __name__ == "__main__":
    run()