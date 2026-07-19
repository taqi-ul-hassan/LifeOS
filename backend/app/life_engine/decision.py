from .schemas import Recommendation, UnifiedContext


class DecisionEngine:
    def recommend(self, context: UnifiedContext) -> list[Recommendation]:
        results = []
        if context.energy_level < 0.45:
            results.append(
                Recommendation(
                    category="workload",
                    message="Reduce today to one essential outcome.",
                    reason="Recent energy is low, so protecting recovery improves plan reliability.",
                    priority=1,
                )
            )
        if context.available_minutes < 120:
            results.append(
                Recommendation(
                    category="calendar",
                    message="Avoid adding new commitments today.",
                    reason="Calendar capacity is below two hours.",
                    priority=2,
                )
            )
        if context.current_task:
            results.append(
                Recommendation(
                    category="next_action",
                    message=f"Start with {context.current_task}.",
                    reason="It is the highest-ranked incomplete task in current context.",
                    priority=1,
                )
            )
        return results
