import asyncio
import threading
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from game_engine import MiniWorld
from extractor import extract_facts
from world_model import WorldModel
from reasoning_agent import decide_action
from main_loop import pick_fallback_action

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Shared state the background loop writes to and the API reads from
state = {
    "graph_nodes": [],
    "graph_edges": [],
    "log": [],
    "turn": 0,
    "running": False,
    "current_room": None,
    "exits": [],
    "inventory": [],
    "objects_in_room": [],
}

game = MiniWorld()
world = WorldModel()


def snapshot_graph():
    nodes = []
    for node, data in world.graph.nodes(data=True):
        nodes.append({"id": node, "type": data.get("type"), "confidence": data.get("confidence")})
    edges = []
    for source, target, data in world.graph.edges(data=True):
        edges.append({"source": source, "target": target, "relation": data.get("relation")})
    return nodes, edges


def agent_loop(num_turns=15):
    global game, world
    game = MiniWorld()
    world = WorldModel()
    obs = game.reset()
    state["log"] = [f"[TURN 0] {obs}"]
    state["turn"] = 0
    state["running"] = True

    last_room, last_inventory, stall_count = None, None, 0

    for turn in range(1, num_turns + 1):
        if not state["running"]:
            break

        facts = extract_facts(obs, game)
        world.update_from_facts(facts)

        action = decide_action(facts)

        if facts["room"] == last_room and facts["inventory"] == last_inventory:
            stall_count += 1
        else:
            stall_count = 0

        if stall_count >= 2:
            action = pick_fallback_action(facts)
            log_line = f"[TURN {turn}] (stalled, fallback) -> '{action}'"
        else:
            log_line = f"[TURN {turn}] Agent: '{action}'"

        last_room = facts["room"]
        last_inventory = list(facts["inventory"])

        obs = game.step(action)

        updated_facts = extract_facts(obs, game)
        state["current_room"] = updated_facts["room"]
        state["exits"] = updated_facts["exits"]
        state["inventory"] = updated_facts["inventory"]
        state["objects_in_room"] = updated_facts["objects_in_room"]

        nodes, edges = snapshot_graph()
        state["graph_nodes"] = nodes
        state["graph_edges"] = edges
        state["log"].append(log_line)
        state["log"].append(f"    Result: {obs}")
        state["turn"] = turn

        time.sleep(1.0)

    state["running"] = False


@app.post("/api/start")
def start_run():
    if not state["running"]:
        thread = threading.Thread(target=agent_loop, daemon=True)
        thread.start()
    return {"started": True}

@app.post("/api/stop")
def stop_run():
    state["running"] = False
    return {"stopped": True}


@app.get("/api/state")
def get_state():
    return state


@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html") as f:
        return f.read()