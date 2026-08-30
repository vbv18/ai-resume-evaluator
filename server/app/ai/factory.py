from app.ai.providers.base import AIProvider
from app.ai.providers.groq_provider import GroqProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.core.config import Settings


def get_ai_provider(settings: Settings) -> AIProvider:
    """
    Factory function returning the configured AIProvider instance.
    """
    provider_name = settings.ai_provider.lower().strip()

    if provider_name == "mock":
        return MockAIProvider()
    elif provider_name in ("groq", "openai"):
        return GroqProvider(settings)
    else:
        # Default fallback to Groq
        return GroqProvider(settings)
