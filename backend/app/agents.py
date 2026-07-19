from dataclasses import dataclass


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    description: str
    system_prompt: str
    keywords: tuple[str, ...]


AGENTS = {
    "ceo": AgentDefinition(
        "ceo",
        "Strategic direction and trade-offs.",
        "You are the LifeOS CEO Agent. Clarify outcomes, identify trade-offs, and give concise strategic guidance. Do not claim access to memory, tools, or external systems.",
        (
            "strategy",
            "priority",
            "priorities",
            "decision",
            "direction",
            "tradeoff",
            "trade-off",
        ),
    ),
    "planner": AgentDefinition(
        "planner",
        "Plans tasks, schedules, and goals.",
        "You are the LifeOS Planner Agent. Convert requests into a realistic plan with ordered steps and time-aware suggestions. Do not claim access to calendar data.",
        ("plan", "schedule", "task", "todo", "goal", "deadline", "week", "day"),
    ),
    "coding": AgentDefinition(
        "coding",
        "Software engineering advice.",
        "You are the LifeOS Coding Agent. Give precise software engineering guidance, surface risks, and propose testable implementation steps.",
        (
            "code",
            "bug",
            "api",
            "python",
            "typescript",
            "repository",
            "deploy",
            "database",
        ),
    ),
    "learning": AgentDefinition(
        "learning",
        "Study planning and skill development.",
        "You are the LifeOS Learning Agent. Create active-learning plans, retrieval practice, and useful assessment ideas.",
        ("learn", "study", "course", "exam", "flashcard", "practice", "skill"),
    ),
    "health": AgentDefinition(
        "health",
        "General wellness support.",
        "You are the LifeOS Health Agent. Offer general wellness guidance, encourage qualified care for medical concerns, and never diagnose.",
        ("sleep", "workout", "exercise", "health", "nutrition", "mood", "stress"),
    ),
    "finance": AgentDefinition(
        "finance",
        "Personal finance organization.",
        "You are the LifeOS Finance Agent. Provide educational budgeting and cash-flow guidance. Do not provide individualized investment, tax, or legal advice.",
        ("budget", "expense", "spending", "income", "save", "finance", "invest"),
    ),
    "research": AgentDefinition(
        "research",
        "Research framing and synthesis.",
        "You are the LifeOS Research Agent. Frame research questions, distinguish evidence from assumptions, and propose a source evaluation plan. Do not invent sources.",
        (
            "research",
            "paper",
            "evidence",
            "experiment",
            "hypothesis",
            "compare",
            "literature",
        ),
    ),
}


class AgentRouter:
    def route(self, prompt: str, requested_agent: str | None = None) -> AgentDefinition:
        if requested_agent:
            agent = AGENTS.get(requested_agent.lower())
            if not agent:
                raise ValueError(f"Unknown agent: {requested_agent}")
            return agent
        normalized = prompt.lower()
        ranked = [
            (sum(keyword in normalized for keyword in agent.keywords), agent)
            for agent in AGENTS.values()
        ]
        score, agent = max(ranked, key=lambda item: item[0])
        return agent if score else AGENTS["planner"]
