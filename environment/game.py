"""
Custom Text Adventure Environment
----------------------------------
A small, fixed 5-room game built for the World Modeling hackathon track.

Map:
    Entrance Hall --- Kitchen --- (locked door) --- Study
                          |
                       Cellar (has the key)
    Entrance Hall --- Garden   (dead end / distractor room)

Objective: reach the Study.
"""

class Game:
    def __init__(self):
        self.rooms = {
            "entrance_hall": {
                "description": "You are in the Entrance Hall. A dusty rug covers the floor.",
                "exits": {"north": "kitchen", "east": "garden"},
            },
            "kitchen": {
                "description": "You are in the Kitchen. Pots hang from the ceiling.",
                "exits": {"south": "entrance_hall", "down": "cellar", "east": "study"},
            },
            "cellar": {
                "description": "You are in the Cellar. It's dark and smells of earth.",
                "exits": {"up": "kitchen"},
            },
            "study": {
                "description": "You are in the Study. Bookshelves line the walls.",
                "exits": {"west": "kitchen"},
            },
            "garden": {
                "description": "You are in the Garden. Overgrown bushes surround a fountain.",
                "exits": {"west": "entrance_hall"},
            },
        }

        self.objects = {
            "brass_key": {"location": "cellar", "state": "on_floor"},
            "east_door": {"location": "kitchen", "state": "locked"},
        }

        self.inventory = []
        self.current_room = "entrance_hall"
        self.objective = "reach the study"
        self.done = False
        self.step_count = 0

    def look(self):
        room = self.rooms[self.current_room]
        text = room["description"]

        exit_desc = []
        for direction, dest in room["exits"].items():
            if self.current_room == "kitchen" and dest == "study":
                door_state = self.objects["east_door"]["state"]
                exit_desc.append(f"{direction} leads to a door that is {door_state}")
            else:
                exit_desc.append(f"{direction} leads to {dest.replace('_', ' ')}")
        if exit_desc:
            text += " Exits: " + "; ".join(exit_desc) + "."

        objs_here = [name for name, o in self.objects.items()
                     if o["location"] == self.current_room and o["state"] != "in_inventory"]
        if objs_here:
            readable = [o.replace("_", " ") for o in objs_here]
            text += " You see: " + ", ".join(readable) + "."

        return text

    def take_action(self, action_text: str) -> str:
        self.step_count += 1
        action = action_text.strip().lower()

        if action.startswith("go "):
            direction = action.replace("go ", "").strip()
            room = self.rooms[self.current_room]
            if direction not in room["exits"]:
                return f"You can't go {direction} from here."

            dest = room["exits"][direction]

            if self.current_room == "kitchen" and dest == "study":
                if self.objects["east_door"]["state"] == "locked":
                    return "The door to the east is locked. You can't go that way."

            self.current_room = dest
            if dest == "study":
                self.done = True
                return self.look() + " Objective complete! You have reached the Study."
            return self.look()

        if "key" in action and ("pick" in action or "take" in action):
            key = self.objects["brass_key"]
            if key["location"] == self.current_room and key["state"] == "on_floor":
                key["state"] = "in_inventory"
                key["location"] = "inventory"
                self.inventory.append("brass_key")
                return "You pick up the brass key."
            elif "brass_key" in self.inventory:
                return "You already have the brass key."
            else:
                return "There is no key here."

        if "unlock" in action:
            if self.current_room != "kitchen":
                return "There is no door to unlock here."
            if self.objects["east_door"]["state"] == "open":
                return "The door is already open."
            if "brass_key" not in self.inventory:
                return "The door is locked and you don't have a key."
            self.objects["east_door"]["state"] = "open"
            return "You unlock the door with the brass key. It creaks open. The door is no longer locked."

        if action == "look":
            return self.look()

        return "You're not sure how to do that."

    def is_done(self):
        return self.done