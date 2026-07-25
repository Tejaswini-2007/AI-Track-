"""
Contradiction Journal
-----------------------
Tracks every time the world model's belief about something changes in a
conflicting way (e.g. a door believed 'locked' is later found 'open').

This is the direct, visible proof that the system detects and resolves
contradictions instead of silently overwriting them.
"""

import json


class ContradictionJournal:
    def __init__(self):
        self.entries = []

    def log_contradiction(self, node, field, old_value, new_value, old_step, new_step, reason):
        entry = {
            "node": node,
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "believed_since_step": old_step,
            "corrected_at_step": new_step,
            "reason": reason,
        }
        self.entries.append(entry)
        print(f"\n⚠️  CONTRADICTION DETECTED — {node}.{field}")
        print(f"    Old belief: {old_value} (held since step {old_step})")
        print(f"    New belief: {new_value} (observed at step {new_step})")
        print(f"    Reason: {reason}\n")

    def has_contradictions(self):
        return len(self.entries) > 0

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.entries, f, indent=2)

    def summary(self):
        return f"{len(self.entries)} contradiction(s) detected and resolved."