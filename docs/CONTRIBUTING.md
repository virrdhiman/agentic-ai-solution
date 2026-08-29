# Contributing

> **Author:** Virender Dhiman

Thank you for considering contributing to the Autonomous Agent system.

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd "Agentic AI Solution"

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v
```

## Project Structure

```
autonomous_agent/
├── core/           # State machine, models, orchestrator, evidence, router
├── providers/      # AI provider abstraction (mock, opensource, cursor, n8n)
├── tools/          # Tool abstraction (filesystem, shell, git)
├── config/         # Settings and configuration
├── api/            # REST API (FastAPI)
├── db/             # Database models (SQLAlchemy)
├── cli/            # CLI entry point (Click)
tests/              # Unit and benchmark tests
docs/               # Project documentation
policies/           # Permission policies (YAML)
```

## Code Style

- Python 3.11+
- Type hints on all public functions
- Docstrings on all classes and public methods (Google style)
- `ruff` for linting (line length: 100)
- `mypy` for type checking

```bash
# Lint
ruff check autonomous_agent/ tests/

# Format
ruff format autonomous_agent/ tests/

# Type check
mypy autonomous_agent/
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_state.py -v

# Run with coverage
python -m pytest tests/ --cov=autonomous_agent --cov-report=term-missing
```

### Test Categories

- **Unit tests** (`test_*.py`): Test individual components in isolation
- **Benchmark tests** (`test_benchmark_*.py`): Prove end-to-end quality (e.g., 10/10 score)

## Adding a New Provider

1. Create `autonomous_agent/providers/your_provider.py`
2. Implement the `AIProvider` abstract base class
3. Add your provider to `providers/router.py`
4. Add config settings in `config/settings.py`
5. Write tests in `tests/test_providers.py`

## Adding a New Tool

1. Create a class in `autonomous_agent/tools/` inheriting from `Tool`
2. Set `name`, `description`, `permission_level`
3. Implement `execute(**kwargs) -> ToolResult`
4. Register it in `tools/base.py` → `get_registry()`
5. Write tests in `tests/test_tools.py`

## Adding a New Agent Role

1. Add the role to `AgentRole` enum in `core/models.py`
2. Add it to `PROBLEM_TYPE_AGENTS` in `core/router.py` if applicable
3. Implement the agent logic in the orchestrator lifecycle
4. Write tests

## Commit Messages

Use clear, descriptive commit messages:
- `feat: add new tool for database queries`
- `fix: resolve state transition bug in orchestrator`
- `docs: add architecture documentation`
- `test: add benchmark test for 10/10 quality`

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Ensure all tests pass: `python -m pytest tests/ -v`
4. Ensure linting passes: `ruff check autonomous_agent/ tests/`
5. Update documentation if needed
6. Submit a pull request with a clear description

## Reporting Issues

When reporting issues, include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version and OS
- Relevant logs or error messages
