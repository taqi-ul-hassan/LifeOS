from datetime import datetime, timezone


class ImportanceScorer:
    def score(
        self, content: str, metadata: dict, created_at: datetime | None = None
    ) -> float:
        text = content.lower()
        now = datetime.now(timezone.utc)
        recency = (
            1
            if not created_at
            else max(
                0,
                1
                - min((now - created_at.replace(tzinfo=timezone.utc)).days, 365) / 365,
            )
        )
        signals = [
            metadata.get("frequency", 0) / 10,
            metadata.get("explicit_preference", False),
            metadata.get("emotional_significance", 0),
            metadata.get("goal_relevance", 0),
            metadata.get("project_relevance", 0),
            metadata.get("learning_relevance", 0),
            metadata.get("health_relevance", 0),
            metadata.get("decision_impact", 0),
            metadata.get("agent_usage_frequency", 0) / 10,
            any(word in text for word in ("important", "prefer", "decided", "goal")),
        ]
        normalized = sum(float(min(1, signal)) for signal in signals) / len(signals)
        return round(
            min(
                1,
                max(
                    0,
                    0.35 * normalized
                    + 0.25 * recency
                    + 0.4 * float(metadata.get("explicit_importance", 0.5)),
                ),
            ),
            4,
        )
