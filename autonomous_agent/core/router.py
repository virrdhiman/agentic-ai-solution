"""Universal Problem Router — classifies problems and builds agent teams."""

from __future__ import annotations

import logging
from typing import Any

from autonomous_agent.core.models import (
    AgentRole,
    ProblemClassification,
    ProblemType,
    RiskLevel,
)

logger = logging.getLogger(__name__)

# Keyword-to-problem-type mapping for fast classification
PROBLEM_KEYWORDS: dict[ProblemType, list[str]] = {
    ProblemType.SOFTWARE_BUG: [
        "bug", "error", "fix", "broken", "crash", "exception", "fails", "fault",
        "incorrect", "wrong", "malfunction",
    ],
    ProblemType.FEATURE_REQUEST: [
        "feature", "add", "create", "implement", "new", "enhance", "improve",
        "extend", "build",
    ],
    ProblemType.WEBSITE_PROBLEM: [
        "website", "web page", "webpage", "html", "css", "dom", "render", "layout",
        "frontend", "ui", "ux", "page not loading", "page broken",
    ],
    ProblemType.BROWSER_PROBLEM: [
        "browser", "chrome", "firefox", "safari", "playwright", "selenium",
        "cypress",
    ],
    ProblemType.API_PROBLEM: [
        "api", "endpoint", "rest", "graphql", "request", "response", "http",
        "swagger", "openapi",
    ],
    ProblemType.DATABASE_PROBLEM: [
        "database", "sql", "query", "migration", "schema", "table", "index",
        "postgres", "mysql", "sqlite", "mongo",
    ],
    ProblemType.DATA_PROBLEM: [
        "data", "excel", "csv", "json", "xml", "transform", "ETL",
        "pipeline", "analytics", "report",
    ],
    ProblemType.INFRASTRUCTURE_PROBLEM: [
        "infrastructure", "server", "vps", "cpu", "memory", "disk", "network",
        "nginx", "apache", "load balancer",
    ],
    ProblemType.DOCKER_PROBLEM: [
        "docker", "container", "compose", "image", "dockerfile", "kubernetes",
        "k8s", "pod",
    ],
    ProblemType.DEPLOYMENT_PROBLEM: [
        "deploy", "deployment", "ci/cd", "pipeline", "release", "rollback",
        "publish",
    ],
    ProblemType.PERFORMANCE_PROBLEM: [
        "performance", "slow", "latency", "optimization", "bottleneck",
        "profiling", "cache",
    ],
    ProblemType.SECURITY_PROBLEM: [
        "security", "vulnerability", "auth", "authentication", "authorization",
        "injection", "xss", "csrf", "secret",
    ],
    ProblemType.CONFIGURATION_PROBLEM: [
        "config", "configuration", "setting", "environment", "env", "yaml",
        "toml", "ini",
    ],
    ProblemType.DEPENDENCY_PROBLEM: [
        "dependency", "package", "version", "conflict", "install", "pip",
        "npm", "yarn", "cargo",
    ],
    ProblemType.DOCUMENTATION_PROBLEM: [
        "documentation", "docs", "readme", "comment", "guide", "tutorial",
        "api docs",
    ],
}

# Skill-to-agent mapping
SKILL_AGENTS: dict[str, list[AgentRole]] = {
    "python": [AgentRole.DEVELOPER],
    "javascript": [AgentRole.DEVELOPER],
    "typescript": [AgentRole.DEVELOPER],
    "debugging": [AgentRole.INVESTIGATOR, AgentRole.DEVELOPER],
    "testing": [AgentRole.QA],
    "security": [AgentRole.SECURITY],
    "database": [AgentRole.DATA],
    "browser": [AgentRole.BROWSER],
    "infrastructure": [AgentRole.INFRASTRUCTURE],
    "docker": [AgentRole.INFRASTRUCTURE],
    "performance": [AgentRole.PERFORMANCE],
    "documentation": [AgentRole.DOCUMENTATION],
    "investigation": [AgentRole.INVESTIGATOR],
    "analysis": [AgentRole.BUSINESS_ANALYST],
    "review": [AgentRole.CODE_REVIEWER],
}

# Problem type to default agent team
PROBLEM_TYPE_AGENTS: dict[ProblemType, list[AgentRole]] = {
    ProblemType.SOFTWARE_BUG: [AgentRole.INVESTIGATOR, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.FEATURE_REQUEST: [
        AgentRole.BUSINESS_ANALYST,
        AgentRole.DEVELOPER,
        AgentRole.QA,
    ],
    ProblemType.WEBSITE_PROBLEM: [AgentRole.BROWSER, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.BROWSER_PROBLEM: [AgentRole.BROWSER, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.API_PROBLEM: [AgentRole.INVESTIGATOR, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.DATABASE_PROBLEM: [AgentRole.DATA, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.DATA_PROBLEM: [AgentRole.DATA, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.INFRASTRUCTURE_PROBLEM: [
        AgentRole.INFRASTRUCTURE,
        AgentRole.DEVELOPER,
        AgentRole.QA,
    ],
    ProblemType.DOCKER_PROBLEM: [AgentRole.INFRASTRUCTURE, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.DEPLOYMENT_PROBLEM: [AgentRole.INFRASTRUCTURE, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.PERFORMANCE_PROBLEM: [
        AgentRole.PERFORMANCE,
        AgentRole.DEVELOPER,
        AgentRole.QA,
    ],
    ProblemType.SECURITY_PROBLEM: [AgentRole.SECURITY, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.CONFIGURATION_PROBLEM: [AgentRole.INVESTIGATOR, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.DEPENDENCY_PROBLEM: [AgentRole.INVESTIGATOR, AgentRole.DEVELOPER, AgentRole.QA],
    ProblemType.DOCUMENTATION_PROBLEM: [
        AgentRole.DOCUMENTATION,
        AgentRole.CODE_REVIEWER,
    ],
    ProblemType.UNKNOWN: [AgentRole.INVESTIGATOR],
}


class UniversalProblemRouter:
    """Classifies problems and determines the required agent team.

    Uses keyword matching for fast local classification, with the AI
    provider as a fallback for ambiguous cases.
    """

    def __init__(self, provider: Any = None) -> None:
        self.provider = provider

    def classify(self, problem: str, context: dict[str, Any] | None = None) -> ProblemClassification:
        """Classify a problem and determine the required team."""
        # Step 1: Keyword-based classification
        problem_type = self._keyword_classify(problem)

        # Step 2: Build classification
        classification = ProblemClassification(
            problem_type=problem_type,
            required_agents=[a.value for a in PROBLEM_TYPE_AGENTS.get(problem_type, [])],
            confidence=0.7 if problem_type != ProblemType.UNKNOWN else 0.3,
        )

        # Step 3: Enrich with context
        if context:
            classification.environment = context.get("environment", "development")

        # Step 4: Add required skills and tools
        classification.required_skills = self._determine_skills(problem, problem_type)
        classification.required_tools = self._determine_tools(problem_type)
        classification.required_tests = self._determine_tests(problem_type)
        classification.risk_level = self._assess_risk(problem_type)

        # Step 5: Add default acceptance criteria
        classification.acceptance_criteria = self._default_criteria(problem_type)

        logger.info(
            "Classified problem as %s (confidence: %.1f)",
            problem_type.value,
            classification.confidence,
        )
        return classification

    def _keyword_classify(self, problem: str) -> ProblemType:
        """Fast keyword-based classification.

        Scans the problem text for keywords associated with each problem type
        and returns the type with the highest match count.
        """
        problem_lower = problem.lower()
        scores: dict[ProblemType, int] = {}

        for ptype, keywords in PROBLEM_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in problem_lower)
            if score > 0:
                scores[ptype] = score

        if not scores:
            return ProblemType.UNKNOWN

        return max(scores, key=scores.get)  # type: ignore[arg-type]

    def _determine_skills(self, problem: str, problem_type: ProblemType) -> list[str]:
        """Determine required skills from the problem text and type."""
        skills = set()
        for skill, _agents in SKILL_AGENTS.items():
            if skill in problem.lower():
                skills.add(skill)
        # Add default skills for problem type
        if problem_type == ProblemType.DATABASE_PROBLEM:
            skills.add("database")
        elif problem_type == ProblemType.SECURITY_PROBLEM:
            skills.add("security")
        return sorted(skills)

    def _determine_tools(self, problem_type: ProblemType) -> list[str]:
        """Map problem type to required tools."""
        tool_map = {
            ProblemType.SOFTWARE_BUG: ["shell", "file", "git", "test"],
            ProblemType.FEATURE_REQUEST: ["shell", "file", "git", "test"],
            ProblemType.WEBSITE_PROBLEM: ["browser", "file", "shell"],
            ProblemType.BROWSER_PROBLEM: ["browser", "playwright", "shell"],
            ProblemType.API_PROBLEM: ["http", "shell", "file", "test"],
            ProblemType.DATABASE_PROBLEM: ["database", "shell", "file"],
            ProblemType.INFRASTRUCTURE_PROBLEM: ["shell", "infrastructure", "docker"],
            ProblemType.DOCKER_PROBLEM: ["docker", "shell"],
            ProblemType.PERFORMANCE_PROBLEM: ["shell", "infrastructure", "test"],
            ProblemType.SECURITY_PROBLEM: ["shell", "file", "git"],
        }
        return tool_map.get(problem_type, ["shell", "file"])

    def _determine_tests(self, problem_type: ProblemType) -> list[str]:
        """Determine which test types are needed for this problem type."""
        test_map = {
            ProblemType.SOFTWARE_BUG: ["unit", "integration", "regression"],
            ProblemType.FEATURE_REQUEST: ["unit", "integration"],
            ProblemType.API_PROBLEM: ["api", "integration"],
            ProblemType.DATABASE_PROBLEM: ["integration", "data"],
            ProblemType.SECURITY_PROBLEM: ["security"],
            ProblemType.PERFORMANCE_PROBLEM: ["performance"],
        }
        return test_map.get(problem_type, ["unit"])

    def _assess_risk(self, problem_type: ProblemType) -> RiskLevel:
        """Assess the risk level based on the problem type."""
        risk_map = {
            ProblemType.SOFTWARE_BUG: RiskLevel.MEDIUM,
            ProblemType.FEATURE_REQUEST: RiskLevel.LOW,
            ProblemType.SECURITY_PROBLEM: RiskLevel.HIGH,
            ProblemType.INFRASTRUCTURE_PROBLEM: RiskLevel.HIGH,
            ProblemType.DEPLOYMENT_PROBLEM: RiskLevel.HIGH,
            ProblemType.DATABASE_PROBLEM: RiskLevel.MEDIUM,
            ProblemType.PERFORMANCE_PROBLEM: RiskLevel.MEDIUM,
        }
        return risk_map.get(problem_type, RiskLevel.LOW)

    def _default_criteria(self, problem_type: ProblemType) -> list[str]:
        """Generate default acceptance criteria for a problem type."""
        criteria = [
            "Problem is understood and classified",
            "Root cause identified with evidence",
            "Solution implemented with minimal safe change",
            "Tests pass",
            "No regressions introduced",
        ]
        if problem_type == ProblemType.SECURITY_PROBLEM:
            criteria.append("Security scan passes")
        if problem_type == ProblemType.PERFORMANCE_PROBLEM:
            criteria.append("Performance benchmarks meet targets")
        return criteria
