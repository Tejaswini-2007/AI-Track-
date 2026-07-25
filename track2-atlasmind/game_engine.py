import random

class MiniWorld:
    def __init__(self):
        self.rooms = {
            "kitchen": {"desc": "You are in a kitchen. There is an apple and a knife here.",
                        "objects": ["apple", "knife"], "exits": {"north": "hallway"}},
            "hallway": {"desc": "You are in a hallway. It connects several rooms.",
                        "objects": [], "exits": {"south": "kitchen", "east": "pantry", "north": "bedroom"}},
            "pantry": {"desc": "You are in a pantry. There is a key on the shelf.",
                       "objects": ["key"], "exits": {"west": "hallway"}},
            "bedroom": {"desc": "You are in a bedroom. There is a locked chest here.",
                        "objects": ["chest"], "exits": {"south": "hallway"}},
        }
        self.current_room = "kitchen"
        self.inventory = []

    def reset(self):
        self.current_room = "kitchen"
        self.inventory = []
        return self.rooms[self.current_room]["desc"]

    def step(self, command):
        command = command.lower().strip()
        room = self.rooms[self.current_room]

        if command.startswith("go "):
            direction = command.replace("go ", "")
            if direction in room["exits"]:
                self.current_room = room["exits"][direction]
                return self.rooms[self.current_room]["desc"]
            else:
                return "You can't go that way."

        if command.startswith("take "):
            item = command.replace("take ", "")
            if item in room["objects"]:
                room["objects"].remove(item)
                self.inventory.append(item)
                return f"You take the {item}."
            else:
                return f"There is no {item} here."

        if command == "look":
            return room["desc"]

        if command == "inventory":
            return f"You are carrying: {', '.join(self.inventory) if self.inventory else 'nothing'}"

        return "I don't understand that command."


if __name__ == "__main__":
    game = MiniWorld()
    print(game.reset())
    print(game.step("take apple"))
    print(game.step("go north"))
    print(game.step("go east"))
    print(game.step("take key"))
    print(game.step("inventory"))