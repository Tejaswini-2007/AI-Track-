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

actions = ["go north", "go down", "pick up key", "go up", "unlock door", "go east"]
prev_room = g.current_room
step = 0

for a in actions:
    step += 1
    result = g.take_action(a)
    facts = ex.extract(result, current_room=g.current_room, previous_room=prev_room, action_taken=a)
    updater.apply_facts(facts, step)

    print(f"Step {step}: > {a}")
    print(f"  World model slice: {wm.get_slice(g.current_room)}")
    print()

    prev_room = g.current_room

print(journal.summary())
wm.save("logs/test_full_world_model.json")
journal.save("logs/test_full_contradiction_journal.json")
print("Saved final world model and journal to logs/.")