const TRACE_DATA = [
  {
    "step": 1,
    "room_before": "entrance_hall",
    "room_after": "garden",
    "action": "go east",
    "response": "You are in the Garden. Overgrown bushes surround a fountain. Exits: west leads to entrance hall.",
    "contradiction": null
  },
  {
    "step": 2,
    "room_before": "garden",
    "room_after": "entrance_hall",
    "action": "go west",
    "response": "You are in the Entrance Hall. A dusty rug covers the floor. Exits: north leads to kitchen; east leads to garden.",
    "contradiction": null
  },
  {
    "step": 3,
    "room_before": "entrance_hall",
    "room_after": "kitchen",
    "action": "go north",
    "response": "You are in the Kitchen. Pots hang from the ceiling. Exits: south leads to entrance hall; down leads to cellar; east leads to a door that is locked. You see: east door.",
    "contradiction": null
  },
  {
    "step": 4,
    "room_before": "kitchen",
    "room_after": "cellar",
    "action": "go down",
    "response": "You are in the Cellar. It's dark and smells of earth. Exits: up leads to kitchen. You see: brass key.",
    "contradiction": null
  },
  {
    "step": 5,
    "room_before": "cellar",
    "room_after": "cellar",
    "action": "pick up brass key",
    "response": "You pick up the brass key.",
    "contradiction": null
  },
  {
    "step": 6,
    "room_before": "cellar",
    "room_after": "kitchen",
    "action": "go up",
    "response": "You are in the Kitchen. Pots hang from the ceiling. Exits: south leads to entrance hall; down leads to cellar; east leads to a door that is locked. You see: east door.",
    "contradiction": null
  },
  {
    "step": 7,
    "room_before": "kitchen",
    "room_after": "kitchen",
    "action": "unlock door",
    "response": "You unlock the door with the brass key. It creaks open. The door is no longer locked.",
    "contradiction": {
      "node": "east_door",
      "field": "state",
      "old_value": "locked",
      "new_value": "open",
      "believed_since_step": 6,
      "corrected_at_step": 7,
      "reason": "direct observation contradicted prior belief"
    }
  },
  {
    "step": 8,
    "room_before": "kitchen",
    "room_after": "study",
    "action": "go east",
    "response": "You are in the Study. Bookshelves line the walls. Exits: west leads to kitchen. Objective complete! You have reached the Study.",
    "contradiction": null
  }
];