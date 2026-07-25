"""
Extractor
-----------
Turns the game's raw text response into structured facts the World Model can use.

Kept intentionally simple (keyword/pattern matching) - the brief says the
extractor doesn't need to be perfect. What matters is that whatever facts
DO get extracted are handled correctly downstream by the Updater.
"""

import re


class Extractor:
    def __init__(self):
        pass

    def _normalize(self, name):
        return name.strip().lower().replace(" ", "_")

    def extract(self, game_text: str, current_room: str, previous_room: str, action_taken: str):
        facts = []
        text = game_text.lower()

        # --- new/confirmed room ---
        facts.append({"type": "room", "name": current_room})

        # --- parse ALL exits mentioned in the room description ---
        # This is the key fix: previously we only recorded a connection when
        # the agent actually walked through a doorway. Now we record every
        # named exit the game describes, even ones not yet explored, so the
        # agent actually knows its options instead of repeatedly guessing.
        if "exits:" in text:
            exits_part = text.split("exits:")[-1]
            exits_part = exits_part.split("you see:")[0]
            exits_part = exits_part.split("objective complete")[0]
            segments = [s.strip().rstrip(".") for s in exits_part.split(";") if s.strip()]

            for seg in segments:
                door_match = re.match(r"(\w+) leads to a door that is (\w+)", seg)
                if door_match:
                    # Exit is a door - destination room name isn't known yet,
                    # but the door object itself is recorded separately below.
                    continue
                named_match = re.match(r"(\w+) leads to (.+)", seg)
                if named_match:
                    direction, dest = named_match.groups()
                    dest_norm = dest.strip().replace(" ", "_")
                    facts.append({
                        "type": "connection",
                        "from": current_room,
                        "direction": direction,
                        "to": dest_norm,
                    })

        # --- door state ---
        # IMPORTANT: check "open" signals BEFORE "locked", since text like
        # "no longer locked" contains the substring "locked" too.
        if "door" in text:
            if "no longer locked" in text or "creaks open" in text or "already open" in text:
                facts.append({"type": "object", "name": "east_door",
                              "location": current_room, "state": "open"})
                # Once the door is open, the room behind it becomes a real,
                # traversable connection - the agent needs this in its graph
                # or it will have nowhere left to go once everywhere else is visited.
                facts.append({"type": "connection",
                              "from": current_room, "direction": "east", "to": "study"})
            elif "locked" in text:
                facts.append({"type": "object", "name": "east_door",
                              "location": current_room, "state": "locked"})

        # --- key ---
        if "key" in text:
            if "you pick up the brass key" in text or "you already have the brass key" in text:
                # This is an EXPECTED transition - it's the direct, intended
                # result of the agent's own "pick up" action, not a case of
                # the agent discovering it held a wrong belief. So we apply it
                # silently, without logging it as a contradiction.
                facts.append({"type": "object", "name": "brass_key",
                              "location": "inventory", "state": "in_inventory",
                              "expected": True})
            elif "you see: " in text and "brass key" in text.split("you see:")[-1]:
                facts.append({"type": "object", "name": "brass_key",
                              "location": current_room, "state": "on_floor"})

        # --- objective completion ---
        if "objective complete" in text:
            facts.append({"type": "objective_complete"})

        return facts