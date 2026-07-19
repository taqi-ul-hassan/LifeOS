import asyncio
import pytest
from app.config import Settings
from app.orchestrator import Orchestrator
from app.providers import Provider
from app.schemas import AIRequest


class RecordingProvider(Provider):
    name = "test"
    model = "test-model"

    async def generate(self, system_prompt: str, prompt: str) -> str:
        return f"{system_prompt.split('.')[0]}: {prompt}"


@pytest.mark.parametrize(
    ("prompt", "agent"),
    [
        ("Help me set a strategic direction", "ceo"),
        ("Plan my week and task list", "planner"),
        ("Review this Python API code", "coding"),
        ("Create a study plan for my exam", "learning"),
        ("Suggest a sleep and workout routine", "health"),
        ("Build a monthly budget", "finance"),
        ("Frame a research hypothesis", "research"),
    ],
)
def test_orchestrator_routes_specialists(prompt: str, agent: str):
    orchestrator = Orchestrator(
        Settings(ai_default_provider="test"), {"test": RecordingProvider()}
    )
    response = asyncio.run(orchestrator.respond(AIRequest(prompt=prompt)))
    assert response.agent == agent
    assert response.provider == "test"


def test_explicit_agent_overrides_keyword_route():
    orchestrator = Orchestrator(
        Settings(ai_default_provider="test"), {"test": RecordingProvider()}
    )
    response = asyncio.run(
        orchestrator.respond(AIRequest(prompt="Plan my day", agent="health"))
    )
    assert response.agent == "health"


def test_general_requests_default_to_planner():
    orchestrator = Orchestrator(
        Settings(ai_default_provider="test"), {"test": RecordingProvider()}
    )
    response = asyncio.run(
        orchestrator.respond(AIRequest(prompt="Help me get started"))
    )
    assert response.agent == "planner"


def test_unknown_provider_is_rejected():
    orchestrator = Orchestrator(
        Settings(ai_default_provider="test"), {"test": RecordingProvider()}
    )
    with pytest.raises(Exception) as error:
        asyncio.run(
            orchestrator.respond(AIRequest(prompt="Plan my day", provider="missing"))
        )
    assert getattr(error.value, "status_code", None) == 422
