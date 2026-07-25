"""
World Model - the Belief-Graph
--------------------------------
This is the agent's external memory. The agent itself has NO memory of its own -
it only ever receives a small "slice" of this graph, generated fresh each step.

Every fact (room, edge, object state) carries:
    confidence   -> how sure we are this is still true (0.0 - 1.0)
    last_updated -> the step number it was last confirmed
"""

import json


class WorldModel:
    def __init__(self):
        self.rooms = {}
        self.objects = {}
        self.current_room = None
        self.step = 0
        self.visited_rooms = set()

    def mark_visited(self, room_name):
        self.visited_rooms.add(room_name)

    # ---------- Room handling ----------

    def add_room(self, room_name, step):
        if room_name not in self.rooms:
            self.rooms[room_name] = {
                "connections": {},
                "confidence": 1.0,
                "last_updated": step,
            }
        else:
            self.rooms[room_name]["last_updated"] = step

    def add_connection(self, from_room, direction, to_room, step):
        self.add_room(from_room, step)
        self.add_room(to_room, step)
        self.rooms[from_room]["connections"][direction] = to_room
        self.rooms[from_room]["last_updated"] = step

    # ---------- Object handling (with contradiction detection) ----------

    def update_object(self, obj_name, location=None, state=None, step=0, journal=None, expected=False):
        if obj_name not in self.objects:
            self.objects[obj_name] = {
                "location": location,
                "state": state,
                "confidence": 1.0,
                "last_updated": step,
            }
            return

        existing = self.objects[obj_name]

        if state is not None and existing["state"] is not None and existing["state"] != state:
            if journal is not None and not expected:
                journal.log_contradiction(
                    node=obj_name,
                    field="state",
                    old_value=existing["state"],
                    new_value=state,
                    old_step=existing["last_updated"],
                    new_step=step,
                    reason="direct observation contradicted prior belief",
                )
            existing["state"] = state
            existing["confidence"] = 1.0
        elif state is not None:
            existing["state"] = state

        if location is not None and existing["location"] is not None and existing["location"] != location:
            if journal is not None and not expected:
                journal.log_contradiction(
                    node=obj_name,
                    field="location",
                    old_value=existing["location"],
                    new_value=location,
                    old_step=existing["last_updated"],
                    new_step=step,
                    reason="object observed in a new location",
                )
            existing["location"] = location
            existing["confidence"] = 1.0
        elif location is not None:
            existing["location"] = location

        existing["last_updated"] = step

    # ---------- Query slice (what the agent actually sees) ----------

    def get_slice(self, current_room, objective_keywords=None):
        lines = []
        room = self.rooms.get(current_room)
        if room:
            conns = room["connections"]
            if conns:
                conn_parts = []
                for d, r in conns.items():
                    tag = "already visited" if r in self.visited_rooms else "UNEXPLORED"
                    conn_parts.append(f"{d} -> {r} ({tag})")
                conn_desc = "; ".join(conn_parts)
                lines.append(f"You are in {current_room.replace('_', ' ')}. Exits: {conn_desc}.")
            else:
                lines.append(f"You are in {current_room.replace('_', ' ')}. No known exits yet.")

        local_objs = [name for name, o in self.objects.items() if o["location"] == current_room]
        if local_objs:
            desc = ", ".join(f"{n.replace('_',' ')} ({self.objects[n]['state']})" for n in local_objs)
            lines.append(f"Objects here: {desc}.")

        carried = [name for name, o in self.objects.items() if o["location"] == "inventory"]
        if carried:
            lines.append("You are carrying: " + ", ".join(c.replace("_", " ") for c in carried) + ".")

        if objective_keywords:
            for name, o in self.objects.items():
                if name in local_objs or o["location"] == "inventory":
                    continue
                if any(kw in name for kw in objective_keywords):
                    lines.append(f"You recall: {name.replace('_',' ')} is believed to be in {o['location']}.")

        return " ".join(lines)

    # ---------- Persistence ----------

    def save(self, path):
        with open(path, "w") as f:
            json.dump({"rooms": self.rooms, "objects": self.objects}, f, indent=2)

    def to_dict(self):
        return {"rooms": self.rooms, "objects": self.objects}