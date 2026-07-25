from agent.ollama_agent import get_next_action

slice_text = "You are in kitchen. Exits: down -> cellar, east -> door (locked). You are carrying: brass key."
objective = "unlock the door and reach the study"

action = get_next_action(slice_text, objective)
print(f"Model suggested action: '{action}'")