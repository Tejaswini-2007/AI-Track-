import matplotlib.pyplot as plt
import networkx as nx


class WorldModel:
    """
    The living knowledge graph. Stores what the agent believes about
    the world, with a confidence score per fact so we can later detect
    contradictions instead of silently overwriting beliefs.
    """

    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_room(self, room_name):
        if not self.graph.has_node(room_name):
            self.graph.add_node(room_name, type="room", confidence=1.0)

    def add_object(self, obj_name, room_name, confidence=0.9):
        if not self.graph.has_node(obj_name):
            self.graph.add_node(obj_name, type="object", confidence=confidence)
        self.add_room(room_name)

        # only add the edge if it doesn't already exist — otherwise we'd
        # create a duplicate edge every time we re-confirm the same fact
        if not self.graph.has_edge(room_name, obj_name):
            self.graph.add_edge(room_name, obj_name, relation="contains", confidence=confidence)
    def remove_object_from_room(self, obj_name, room_name):
        # if the edge exists, remove it (object picked up / no longer there)
        if self.graph.has_edge(room_name, obj_name):
            self.graph.remove_edge(room_name, obj_name)

    def update_from_facts(self, facts):
        """
        Ingest a structured facts dict (from the Extractor) into the graph.
        This is a simplified version of the 'Self-Correction Engine' —
        for now it just adds/removes, we'll add contradiction detection next.
        """
        room = facts["room"]
        self.add_room(room)

        # remove objects no longer present in this room
        current_edges = list(self.graph.out_edges(room, data=True))
        for source, target, data in current_edges:
            if data.get("relation") == "contains" and target not in facts["objects_in_room"]:
                self.remove_object_from_room(target, room)

        # add/confirm objects present now
        for obj in facts["objects_in_room"]:
            self.add_object(obj, room)

    def where_is(self, obj_name):
        """Very simple query: which room currently 'contains' this object?"""
        for source, target, data in self.graph.edges(data=True):
            if target == obj_name and data.get("relation") == "contains":
                return source
        return None

    def describe(self):
        """Print the whole graph in a human-readable way, for debugging."""
        print(f"\n--- WORLD MODEL: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges ---")
        for node, data in self.graph.nodes(data=True):
            print(f"  [{data.get('type')}] {node} (confidence={data.get('confidence')})")
        for source, target, data in self.graph.edges(data=True):
            print(f"  {source} --{data.get('relation')}--> {target}")

    def draw_live(self, turn_number):
        plt.clf()
        pos = nx.spring_layout(self.graph, seed=42)

        room_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("type") == "room"]
        object_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("type") == "object"]

        nx.draw_networkx_nodes(self.graph, pos, nodelist=room_nodes, node_color="#4C9AFF", node_size=1200)
        nx.draw_networkx_nodes(self.graph, pos, nodelist=object_nodes, node_color="#FFAB4C", node_size=800)
        nx.draw_networkx_labels(self.graph, pos, font_size=9)
        nx.draw_networkx_edges(self.graph, pos, arrowstyle="->", arrowsize=15)

        edge_labels = {(u, v): d.get("relation", "") for u, v, d in self.graph.edges(data=True)}
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=7)

        plt.title(f"AtlasMind World Model - Turn {turn_number}")
        plt.axis("off")
        plt.pause(0.1)


if __name__ == "__main__":
    from game_engine import MiniWorld
    from extractor import extract_facts

    game = MiniWorld()
    world = WorldModel()

    obs = game.reset()
    facts = extract_facts(obs, game)
    world.update_from_facts(facts)
    world.describe()

    obs = game.step("take apple")
    facts = extract_facts(obs, game)
    world.update_from_facts(facts)
    world.describe()

    print("\nWhere is the knife?", world.where_is("knife"))
    print("Where is the apple?", world.where_is("apple"))