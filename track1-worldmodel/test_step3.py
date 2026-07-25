from environment.game import Game
from agent.extractor import Extractor

g = Game()
ex = Extractor()

actions = ["go north", "go down", "pick up key", "go up", "unlock door", "go east"]
prev_room = g.current_room

for a in actions:
    result = g.take_action(a)
    facts = ex.extract(result, current_room=g.current_room, previous_room=prev_room, action_taken=a)
    print(f"> {a}")
    print(f"  game text: {result}")
    print(f"  extracted facts: {facts}")
    print()
    prev_room = g.current_room