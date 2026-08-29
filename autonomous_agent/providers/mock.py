"""Mock provider — deterministic responses for testing and default operation.

This provider does not call any external API. It returns structured
responses that allow the full lifecycle to execute and be tested.
"""

from __future__ import annotations

from typing import Any

from autonomous_agent.providers.base import AIProvider


class MockProvider(AIProvider):
    """Deterministic mock provider for testing and offline operation."""

    def __init__(self) -> None:
        self.call_count = 0
        self.calls: list[dict[str, Any]] = []

    def _record(self, method: str, prompt: str, context: dict[str, Any] | None) -> None:
        """Record a provider call for testing and debugging."""
        self.call_count += 1
        self.calls.append({"method": method, "prompt": prompt, "context": context})

    def analyze(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Analyze a problem and return a classification.

        Returns a dict with problem_type, required_agents, risk_level, etc.
        """
        self._record("analyze", prompt, context)
        problem = (context or {}).get("problem", prompt)
        # Return a reasonable classification
        problem_lower = problem.lower()
        if any(w in problem_lower for w in ["bug", "error", "fix", "broken", "fail"]):
            return {
                "problem_type": "software_bug",
                "affected_systems": ["application"],
                "required_skills": ["python", "debugging"],
                "required_tools": ["shell", "file", "git"],
                "required_agents": ["investigator", "developer", "qa"],
                "required_tests": ["unit", "integration"],
                "risk_level": "medium",
                "environment": "development",
                "acceptance_criteria": [
                    "Problem is reproduced",
                    "Root cause identified",
                    "Fix implemented",
                    "Tests pass",
                ],
                "confidence": 0.8,
            }
        elif any(w in problem_lower for w in ["feature", "add", "create", "implement"]):
            return {
                "problem_type": "feature_request",
                "affected_systems": ["application"],
                "required_skills": ["python"],
                "required_tools": ["shell", "file", "git"],
                "required_agents": ["business_analyst", "developer", "qa"],
                "required_tests": ["unit"],
                "risk_level": "low",
                "environment": "development",
                "acceptance_criteria": [
                    "Feature implemented",
                    "Tests written",
                    "Documentation updated",
                ],
                "confidence": 0.85,
            }
        else:
            return {
                "problem_type": "unknown",
                "affected_systems": ["unknown"],
                "required_skills": ["investigation"],
                "required_tools": ["shell", "file"],
                "required_agents": ["investigator"],
                "required_tests": [],
                "risk_level": "medium",
                "environment": "development",
                "acceptance_criteria": ["Problem classified", "Solution proposed"],
                "confidence": 0.3,
            }

    def plan(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Create a step-by-step execution plan."""
        self._record("plan", prompt, context)
        return {
            "steps": [
                "Investigate the problem space",
                "Identify root cause",
                "Design minimal solution",
                "Implement changes",
                "Write tests",
                "Run tests",
                "Review changes",
            ],
            "estimated_effort": "medium",
            "risks": ["May require multiple iterations"],
            "rollback_plan": "Revert git changes",
        }

    def generate(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Generate code or a response."""
        self._record("generate", prompt, context)
        return {
            "implementation": "Solution implemented based on analysis",
            "files_modified": [],
            "description": "Applied minimal safe change to resolve the issue",
        }

    def debug(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Debug a problem and identify root cause."""
        self._record("debug", prompt, context)
        attempt = (context or {}).get("attempt", 1)
        return {
            "hypothesis": f"Attempt {attempt}: Root cause analysis based on available evidence",
            "evidence": "Evidence gathered from code analysis and testing",
            "confidence": 0.7,
            "recommendation": "Apply targeted fix with verification",
        }

    def review(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Review code, tests, or results."""
        self._record("review", prompt, context)
        return {
            "verdict": "pass",
            "findings": ["No critical issues found"],
            "suggestions": ["Consider adding edge case tests"],
            "confidence": 0.8,
        }

    def summarize(self, prompt: str, *, context: dict[str, Any] | None = None) -> Any:
        """Summarize information."""
        self._record("summarize", prompt, context)
        return {
            "summary": "Problem analyzed and resolved through systematic investigation",
            "key_findings": ["Root cause identified", "Solution implemented", "Tests passing"],
        }
