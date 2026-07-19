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

    async def respond(
        self, request: AIRequest, user_id: str | None = None, session=None
    ) -> AIResponse:
        try:
            agent = self.router.route(request.prompt, request.agent)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        provider_name = (request.provider or self.settings.ai_default_provider).lower()
        provider = self.providers.get(provider_name)
        if not provider:
            raise HTTPException(422, f"Unknown provider: {provider_name}")
        system_prompt = agent.system_prompt
        if user_id and session:
            from .memory.schemas import MemorySearch
            from .memory.service import MemoryService

            memory = MemoryService(session, self.settings)
            retrieved = await memory.retrieve(
                user_id,
                MemorySearch(query=request.prompt, top_k=6, min_similarity=0.08),
            )
            if retrieved.context:
                system_prompt = (
                    f"{system_prompt}\n\nRelevant user memory:\n{retrieved.context}"
                )
        output = await provider.generate(system_prompt, request.prompt)
        if user_id and session:
            from .memory.schemas import MemoryCreate
            from .memory.service import MemoryService

            await MemoryService(session, self.settings).create(
                user_id,
                MemoryCreate(
                    title=f"Conversation with {agent.name}",
                    content=request.prompt,
                    memory_type="episodic",
                    source="conversation",
                    metadata={"agent": agent.name},
                ),
            )
        return AIResponse(
            agent=agent.name,
            provider=provider.name,
            model=provider.model,
            output=output,
        )
