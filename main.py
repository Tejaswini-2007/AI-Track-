"""
Main Agent Loop
------------------
Ties everything together: Game -> Extractor -> Updater -> World Model -> Query Layer -> Ollama Agent -> Game -> repeat.

Critically: the agent NEVER sees conversation history. Each step, it only
receives the current world slice + objective, fresh.
"""

from environment.game import Game
from agent.extractor import Extractor
from agent.updater import Updater
from agent.ollama_agent import get_next_action
from world_model.graph import WorldModel
from world_model.journal import ContradictionJournal
import json

MAX_STEPS = 20


def apply_safety_check(llm_action, wm, current_room):
    """
    Small models don't always follow instructions perfectly. This guardrail
    catches two specific failure patterns:
      1. There's a known, unclaimed item in the current room (e.g. a key on
         the floor) and the agent isn't trying to pick it up - prioritize that.
      2. The agent tries to move in a direction that either doesn't exist,
         or leads somewhere already visited, while a better option exists.
    """
    # --- Priority 1: pick up any known item sitting in this room ---
    for obj_name, obj_data in wm.objects.items():
        if obj_data["location"] == current_room and obj_data["state"] == "on_floor":
            if "pick up" not in llm_action and "take" not in llm_action:
                item_label = obj_name.replace("_", " ")
                print(f"  [safety check] Known item '{item_label}' is on the floor here "
                      f"and unclaimed - overriding to pick it up first.")
                return f"pick up {item_label}"

    # --- Priority 1.5: unlock a known locked door if we're carrying the key ---
    carrying_key = any(o["location"] == "inventory" for name, o in wm.objects.items() if "key" in name)
    for obj_name, obj_data in wm.objects.items():
        if "door" in obj_name and obj_data["location"] == current_room and obj_data["state"] == "locked":
            if carrying_key and "unlock" not in llm_action:
                print(f"  [safety check] Door here is locked and we have the key "
                      f"- overriding to unlock it first.")
                return "unlock door"

    # --- Priority 2: fix bad or suboptimal movement ---
    if llm_action.startswith("go "):
        room = wm.rooms.get(current_room)
        if not room:
            return llm_action

        connections = room["connections"]
        requested_direction = llm_action.replace("go ", "").strip()

        # Case A: direction doesn't exist at all from here
        if requested_direction not in connections:
            unexplored = [d for d, dest in connections.items() if dest not in wm.visited_rooms]
            if unexplored:
                chosen = unexplored[0]
                print(f"  [safety check] '{llm_action}' is not a valid exit here - "
                      f"redirecting to unexplored exit '{chosen}' instead.")
                return f"go {chosen}"
            elif connections:
                chosen = list(connections.keys())[0]
                print(f"  [safety check] '{llm_action}' is not a valid exit here - "
                      f"no unexplored options, backtracking via '{chosen}'.")
                return f"go {chosen}"

        # Case B: direction is valid but leads somewhere already visited,
        # while an unexplored option exists
        else:
            requested_dest = connections[requested_direction]
            if requested_dest in wm.visited_rooms:
                for direction, dest in connections.items():
                    if dest not in wm.visited_rooms:
                        print(f"  [safety check] LLM chose '{llm_action}' (already visited) "
                              f"- redirecting to unexplored exit '{direction}' instead.")
                        return f"go {direction}"

    return llm_action


def run():
    g = Game()
    ex = Extractor()
    wm = WorldModel()
    journal = ContradictionJournal()
    updater = Updater(wm, journal)

    objective = g.objective
    prev_room = g.current_room
    step = 0

    print("=== RUN START ===")
    print(f"Objective: {objective}\n")

    # Give the agent its very first look at the starting room
    initial_look = g.look()
    facts = ex.extract(initial_look, current_room=g.current_room,
                        previous_room=prev_room, action_taken="look")
    updater.apply_facts(facts, step)

    wm.mark_visited(g.current_room)
    trace = []  # records every step for the map replay viewer

    while not g.is_done() and step < MAX_STEPS:
        step += 1
        room_before = g.current_room
        contradictions_before = len(journal.entries)

        world_slice = wm.get_slice(g.current_room, objective_keywords=["door", "key", "study"])
        action = get_next_action(world_slice, objective)
        action = apply_safety_check(action, wm, g.current_room)

        print(f"--- Step {step} ---")
        print(f"World slice: {world_slice}")
        print(f"Agent action: {action}")

        result = g.take_action(action)
        print(f"Game response: {result}\n")

        facts = ex.extract(result, current_room=g.current_room, previous_room=prev_room, action_taken=action)
        updater.apply_facts(facts, step)
        wm.mark_visited(g.current_room)

        # record this step for the map replay viewer
        new_contradiction = journal.entries[-1] if len(journal.entries) > contradictions_before else None
        trace.append({
            "step": step,
            "room_before": room_before,
            "room_after": g.current_room,
            "action": action,
            "response": result,
            "contradiction": new_contradiction,
        })

        prev_room = g.current_room

    print("=== RUN COMPLETE ===")
    if g.is_done():
        print(f"Objective reached in {step} steps.")
    else:
        print(f"Step limit ({MAX_STEPS}) reached without completing objective.")

    print(journal.summary())

    wm.save("logs/world_model_final.json")
    journal.save("logs/contradiction_journal.json")

    with open("logs/run_trace.json", "w") as f:
        json.dump(trace, f, indent=2)

    # Also write the trace as a JS file the map viewer can load directly via
    # <script src="..."> - this works with a plain double-click (file://),
    # unlike fetch(), which browsers block for local files.
    with open("viewer/run_trace_data.js", "w") as f:
        f.write("const TRACE_DATA = ")
        json.dump(trace, f, indent=2)
        f.write(";")

    print("Saved world model, contradiction journal, and run trace to logs/ and viewer/.")


if __name__ == "__main__":
    run()