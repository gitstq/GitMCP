# Contributing to GitMCP

Thank you for your interest in contributing to GitMCP! This guide outlines the process.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/gitmcp.git
   cd gitmcp
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

## Code Style

- Follow PEP 8 conventions
- Use type hints for all function signatures
- Add docstrings to all public functions and classes
- Keep functions focused and under 50 lines when possible

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions or modifications
- `chore:` Maintenance tasks

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Ensure all tests pass
4. Submit a PR with a clear description

## Reporting Issues

When reporting issues, please include:
- OS and Python version
- GitMCP version
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs
