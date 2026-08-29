"""Tests for AI providers."""

import pytest

from autonomous_agent.providers.base import AIProvider
from autonomous_agent.providers.mock import MockProvider


class TestMockProvider:
    def setup_method(self):
        self.provider = MockProvider()

    def test_implements_interface(self):
        assert isinstance(self.provider, AIProvider)

    def test_analyze_bug(self):
        result = self.provider.analyze("Fix the broken login", context={"problem": "Fix the broken login"})
        assert "problem_type" in result
        assert result["problem_type"] == "software_bug"

    def test_analyze_feature(self):
        result = self.provider.analyze("Add a new dashboard", context={"problem": "Add a new dashboard"})
        assert result["problem_type"] == "feature_request"

    def test_analyze_unknown(self):
        result = self.provider.analyze("Something weird is happening", context={"problem": "Something weird is happening"})
        assert result["problem_type"] == "unknown"

    def test_plan(self):
        result = self.provider.plan("Fix the bug", context={"problem": "Fix the bug"})
        assert "steps" in result
        assert len(result["steps"]) > 0

    def test_generate(self):
        result = self.provider.generate("Write code", context={"problem": "Fix the bug"})
        assert "implementation" in result

    def test_debug(self):
        result = self.provider.debug("Find root cause", context={"problem": "Fix the bug"})
        assert "hypothesis" in result

    def test_review(self):
        result = self.provider.review("Review the code", context={"problem": "Fix the bug"})
        assert "verdict" in result

    def test_summarize(self):
        result = self.provider.summarize("Summarize findings", context={"problem": "Fix the bug"})
        assert "summary" in result

    def test_call_tracking(self):
        self.provider.analyze("test", context={})
        self.provider.plan("test", context={})
        assert self.provider.call_count == 2
        assert len(self.provider.calls) == 2
        assert self.provider.calls[0]["method"] == "analyze"
        assert self.provider.calls[1]["method"] == "plan"

    def test_debug_with_retry_context(self):
        result = self.provider.debug(
            "retry",
            context={"attempt": 3, "strategy_level": 2},
        )
        assert "hypothesis" in result
        assert "3" in result["hypothesis"]


class TestProviderRouter:
    def test_create_mock_provider(self):
        from autonomous_agent.config.settings import ProviderType
        from autonomous_agent.providers.router import create_provider

        provider = create_provider(ProviderType.MOCK)
        assert isinstance(provider, MockProvider)

    def test_fallback_to_mock_on_invalid(self):
        from autonomous_agent.providers.router import create_provider

        # Should fall back to mock when opensource can't connect
        provider = create_provider(None)
        assert isinstance(provider, MockProvider)
