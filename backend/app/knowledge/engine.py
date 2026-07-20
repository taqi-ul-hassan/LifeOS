from datetime import date, timedelta
from sqlalchemy import select
from ..models import KnowledgeGraphNode, LearningSession


class Knowledge:
    def __init__(self, s):
        self.s = s

    def import_(self, u, title, content, kind="resource"):
        n = KnowledgeGraphNode(
            user_id=u,
            label=title,
            node_type=kind,
            attributes={"content": content, "version": 1},
        )
        self.s.add(n)
        self.s.commit()
        return n

    def search(self, u, q):
        return [
            n
            for n in self.s.scalars(
                select(KnowledgeGraphNode).where(KnowledgeGraphNode.user_id == u)
            )
            if q.lower() in n.label.lower() or q.lower() in str(n.attributes).lower()
        ]

    def mastery(self, u):
        sessions = list(
            self.s.scalars(select(LearningSession).where(LearningSession.user_id == u))
        )
        out = {}
        for x in sessions:
            out[x.topic] = min(100, out.get(x.topic, 0) + x.minutes / 3)
        return {k: round(v, 1) for k, v in out.items()}

    def path(self, u):
        m = self.mastery(u)
        weak = [k for k, v in m.items() if v < 60]
        return {
            "next_topic": weak[0] if weak else "Choose a new learning goal",
            "daily_minutes": 30,
            "steps": [
                "Read concept overview",
                "Practice retrieval",
                "Review flashcards",
            ],
        }

    def cards(self, u, topic):
        nodes = self.search(u, topic)
        return [
            {
                "front": n.label,
                "back": str(n.attributes.get("content", ""))[:180],
                "next_review": str(date.today() + timedelta(days=1)),
            }
            for n in nodes
        ]

    def quiz(self, u, topic):
        return {
            "topic": topic,
            "questions": [
                {
                    "question": f"Explain {n.label}.",
                    "answer": str(n.attributes.get("content", ""))[:180],
                }
                for n in self.search(u, topic)[:5]
            ],
        }
