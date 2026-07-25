from environment.game import Game

g = Game()
print(g.look())

actions = ["go north", "go east", "go down", "pick up key", "go up", "unlock door", "go east"]
for a in actions:
    print(f"> {a}")
    print(g.take_action(a))
    print()

print("Objective complete?", g.is_done())