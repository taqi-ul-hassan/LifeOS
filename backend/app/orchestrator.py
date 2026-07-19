from fastapi import HTTPException
from .agents import AgentRouter
from .config import Settings
from .providers import Provider, build_providers
from .schemas import AIRequest, AIResponse


class Orchestrator:
    def __init__(
        self, settings: Settings, providers: dict[str, Provider] | None = None
    ):
        self.settings = settings
        self.providers = providers or build_providers(settings)
        self.router = AgentRouter()

    async def respond(self, request: AIRequest) -> AIResponse:
        try:
            agent = self.router.route(request.prompt, request.agent)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        provider_name = (request.provider or self.settings.ai_default_provider).lower()
        provider = self.providers.get(provider_name)
        if not provider:
            raise HTTPException(422, f"Unknown provider: {provider_name}")
        output = await provider.generate(agent.system_prompt, request.prompt)
        return AIResponse(
            agent=agent.name,
            provider=provider.name,
            model=provider.model,
            output=output,
        )
