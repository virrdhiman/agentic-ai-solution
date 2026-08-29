"""Tests for the Universal Problem Router."""

from autonomous_agent.core.router import UniversalProblemRouter
from autonomous_agent.core.models import ProblemType, RiskLevel


class TestUniversalProblemRouter:
    def setup_method(self):
        self.router = UniversalProblemRouter()

    def test_classify_bug(self):
        result = self.router.classify("Fix the broken login page")
        assert result.problem_type == ProblemType.SOFTWARE_BUG

    def test_classify_feature(self):
        result = self.router.classify("Add a new dashboard feature")
        assert result.problem_type == ProblemType.FEATURE_REQUEST

    def test_classify_database(self):
        result = self.router.classify("The database query is returning wrong results")
        assert result.problem_type == ProblemType.DATABASE_PROBLEM

    def test_classify_security(self):
        result = self.router.classify("There is a security vulnerability in authentication")
        assert result.problem_type == ProblemType.SECURITY_PROBLEM

    def test_classify_performance(self):
        result = self.router.classify("The application is extremely slow")
        assert result.problem_type == ProblemType.PERFORMANCE_PROBLEM

    def test_classify_docker(self):
        result = self.router.classify("Docker container keeps restarting")
        assert result.problem_type == ProblemType.DOCKER_PROBLEM

    def test_classify_api(self):
        result = self.router.classify("The REST API endpoint returns 500")
        assert result.problem_type == ProblemType.API_PROBLEM

    def test_classify_unknown(self):
        result = self.router.classify("Something weird happened")
        assert result.problem_type == ProblemType.UNKNOWN

    def test_agent_team_populated(self):
        result = self.router.classify("Fix the broken test suite")
        assert len(result.required_agents) > 0

    def test_risk_level_for_security(self):
        result = self.router.classify("Security audit needed")
        assert result.risk_level == RiskLevel.HIGH

    def test_risk_level_for_feature(self):
        result = self.router.classify("Add a new feature to the dashboard")
        assert result.risk_level == RiskLevel.LOW

    def test_acceptance_criteria_populated(self):
        result = self.router.classify("Fix the bug")
        assert len(result.acceptance_criteria) > 0

    def test_confidence_for_known_type(self):
        result = self.router.classify("Fix the broken login")
        assert result.confidence > 0.5

    def test_confidence_for_unknown(self):
        result = self.router.classify("asjdhfkajsdhfk")
        assert result.confidence <= 0.5

    def test_environment_from_context(self):
        result = self.router.classify(
            "Fix the bug",
            context={"environment": "production"},
        )
        assert result.environment == "production"

    def test_required_tools_populated(self):
        result = self.router.classify("The website page is broken")
        assert len(result.required_tools) > 0
