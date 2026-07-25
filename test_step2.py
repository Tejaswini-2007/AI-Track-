from world_model.graph import WorldModel
from world_model.journal import ContradictionJournal

wm = WorldModel()
journal = ContradictionJournal()

# Step 1: agent enters kitchen, sees the door is locked
wm.add_connection("entrance_hall", "north", "kitchen", step=1)
wm.update_object("east_door", location="kitchen", state="locked", step=1, journal=journal)

print("--- Slice at step 1 (in kitchen) ---")
print(wm.get_slice("kitchen"))
print()

# Step 3: agent picks up the key
wm.update_object("brass_key", location="inventory", state="in_inventory", step=3, journal=journal)

# Step 6: agent unlocks the door -> CONTRADICTS earlier belief (locked -> open)
wm.update_object("east_door", location="kitchen", state="open", step=6, journal=journal)

print("--- Slice at step 6 (in kitchen, after unlocking) ---")
print(wm.get_slice("kitchen"))
print()

print(journal.summary())

wm.save("logs/test_world_model.json")
journal.save("logs/test_contradiction_journal.json")
print("Saved to logs/ folder.")