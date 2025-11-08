# Contributing to Cite-Agent

## Quick Start

```bash
git clone https://github.com/Spectating101/cite-agent.git
cd cite-agent
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Development

### Running Tests
```bash
pytest tests/enhanced/ tests/test_workflow_integration.py -v
```

### Code Quality
```bash
ruff check cite_agent/
black cite_agent/
mypy cite_agent/
```

### Before Committing
```bash
pre-commit install
pre-commit run --all-files
```

## Pull Request Process

1. Fork the repo
2. Create branch: `git checkout -b feature/your-feature`
3. Write tests
4. Make changes
5. Run tests: `pytest`
6. Commit: `git commit -m "Add feature"`
7. Push: `git push origin feature/your-feature`
8. Open PR

## Code Style

- Use type hints
- Write docstrings
- Keep functions < 50 lines
- Test coverage > 80%

## Questions?

Open an issue.
