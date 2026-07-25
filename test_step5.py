from environment.game import Game
from agent.extractor import Extractor
from agent.updater import Updater
from world_model.graph import WorldModel
from world_model.journal import ContradictionJournal

g = Game()
ex = Extractor()
wm = WorldModel()
journal = ContradictionJournal()
updater = Updater(wm, journal)

actions = ["go north", "go down", "pick up key", "go up"]
prev_room = g.current_room
step = 0

for a in actions:
    step += 1
    result = g.take_action(a)
    facts = ex.extract(result, current_room=g.current_room, previous_room=prev_room, action_taken=a)
    updater.apply_facts(facts, step)
    prev_room = g.current_room

# Now the agent is back in the kitchen, holding the key.
# Objective: "unlock the door" -> relevant keyword: "door"
print("Slice WITHOUT objective keywords:")
print(wm.get_slice(g.current_room))
print()

print("Slice WITH objective keyword 'door':")
print(wm.get_slice(g.current_room, objective_keywords=["door"]))