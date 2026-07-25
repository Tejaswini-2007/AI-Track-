"""
Updater
---------
Takes the list of facts produced by the Extractor and writes them into the
World Model. This is the piece that "closes the loop" - Extractor produces
facts, Updater applies them, World Model stores them (detecting contradictions
along the way via the Journal).
"""

class Updater:
    def __init__(self, world_model, journal):
        self.world_model = world_model
        self.journal = journal

    def apply_facts(self, facts, step):
        for fact in facts:
            if fact["type"] == "room":
                self.world_model.add_room(fact["name"], step)

            elif fact["type"] == "connection":
                self.world_model.add_connection(
                    fact["from"], fact["direction"], fact["to"], step
                )

            elif fact["type"] == "object":
                self.world_model.update_object(
                    fact["name"],
                    location=fact.get("location"),
                    state=fact.get("state"),
                    step=step,
                    journal=self.journal,
                    expected=fact.get("expected", False),
                )

            # "objective_complete" facts don't touch the world model -
            # they're handled directly in the main agent loop