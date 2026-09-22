from collections import defaultdict

class ConversationMemoryAgent:
    def __init__(self):
        self.sessions = defaultdict(list)

    def add_turn(self, session_id: str, role: str, message: str):
        self.sessions[session_id].append({"role": role, "message": message})
        # Keep sliding window of last 6 turns
        if len(self.sessions[session_id]) > 6:
            self.sessions[session_id].pop(0)

    def get_history(self, session_id: str) -> list:
        return self.sessions[session_id]

    def contextualize_query(self, session_id: str, current_query: str) -> str:
        history = self.sessions.get(session_id, [])
        if not history:
            return current_query
        # Simple resolution heuristic: stitch the last user subject if pronouns or short follow-ups occur
        if any(w in current_query.lower().split() for w in ["it", "that", "this", "explain", "more"]):
            last_queries = [h["message"] for h in reversed(history) if h["role"] == "user"]
            if last_queries:
                return f"{last_queries[0]} -> {current_query}"
        return current_query