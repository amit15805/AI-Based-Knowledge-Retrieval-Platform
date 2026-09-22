class ClarificationAgent:
    @staticmethod
    def generate_clarification(query: str, reason: str) -> dict:
        return {
            "needs_clarification": True,
            "clarification_question": f"Your query is ambiguous ({reason}). Could you specify which component, protocol, or timeframe you are asking about?",
            "suggested_options": [
                f"Clarify architecture of {query}",
                f"Ask for implementation steps for {query}",
                f"Compare options regarding {query}"
            ]
        }