from app.modules.registry import ModuleManifest, register_module
from app.modules.ai_assistant.router import router as ai_router


def register():
    register_module(ModuleManifest(
        name="ai_assistant",
        version="0.1.0",
        description="AI assistant (placeholder for future LLM integration)",
        router_factory=lambda: ai_router,
        prefix="/api/ai",
        tags=["AI Assistant"],
    ))
