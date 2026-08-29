"""Provider router — creates the appropriate AI provider based on config."""

from __future__ import annotations

import logging
from typing import Any

from autonomous_agent.config.settings import ProviderType, get_settings
from autonomous_agent.providers.base import AIProvider

logger = logging.getLogger(__name__)


def create_provider(
    provider_type: ProviderType | None = None,
    **kwargs: Any,
) -> AIProvider:
    """Factory function to create the right AI provider.

    Falls back through: configured -> mock
    """
    settings = get_settings()
    ptype = provider_type or settings.agent_provider

    if ptype == ProviderType.OPENSOURCE:
        try:
            from autonomous_agent.providers.opensource import OpenSourceProvider

            return OpenSourceProvider(**kwargs)
        except Exception as e:
            logger.warning("Failed to create OpenSource provider: %s. Falling back to mock.", e)
            return _create_mock()

    elif ptype == ProviderType.N8N:
        try:
            from autonomous_agent.providers.n8n import N8NProvider

            return N8NProvider(**kwargs)
        except Exception as e:
            logger.warning("Failed to create N8N provider: %s. Falling back to mock.", e)
            return _create_mock()

    elif ptype == ProviderType.HYBRID:
        # Hybrid uses opensource as default, other providers for specific tasks
        try:
            from autonomous_agent.providers.opensource import OpenSourceProvider

            return OpenSourceProvider(**kwargs)
        except Exception:
            return _create_mock()

    else:
        return _create_mock()


def _create_mock() -> AIProvider:
    from autonomous_agent.providers.mock import MockProvider

    return MockProvider()
