# Contributing to Terminally Simple

Thank you for contributing! Please see our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Check existing issues first, then create a new issue with:
* Clear title and description
* Steps to reproduce
* Expected vs actual behavior
* Environment details (OS, Python version, terminal)

### Suggesting Features

Open an issue with:
* Clear description of the feature
* Why it would be useful
* Examples if applicable

### Pull Requests

* Follow Python style (Black, Ruff)
* Update documentation
* Keep changes focused and minimal

## Development Setup

```bash
git clone https://github.com/yourusername/terminallysimple.git
cd terminallysimple
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Guidelines

* **Keep it simple** - Minimal and focused features
* **Keyboard-first** - Avoid mouse-only interactions
* **Follow existing patterns** - Match current UI/code style
* **Use Black & Ruff** - Format code before committing

## Git Workflow

```bash
git checkout -b feature/my-feature
# Make changes
git commit -m "Add feature description"
git push origin feature/my-feature
# Open Pull Request
```

Use clear commit messages in present tense ("Add feature" not "Added feature").

## Questions?

Open an issue or discussion. Thank you for contributing!
