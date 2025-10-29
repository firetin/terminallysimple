# Contributing to Terminally Simple

First off, thank you for considering contributing to Terminally Simple! It's people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed and what behavior you expected**
* **Include screenshots if possible**
* **Include your environment details** (OS, Python version, terminal emulator)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List any similar features in other applications if applicable**

### Pull Requests

* Fill in the required template
* Follow the Python style guide (we use Black and Ruff)
* Include appropriate test cases if applicable
* Update documentation as needed
* End all files with a newline

## Development Setup

### Prerequisites

* Python 3.8 or higher
* pip and venv

### Setting Up Your Development Environment

1. **Fork and clone the repository**
```bash
git clone https://github.com/yourusername/terminallysimple.git
cd terminallysimple
```

2. **Create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install development dependencies** (optional)
```bash
pip install black ruff mypy pytest
```

5. **Run the application**
```bash
python app.py
```

## Development Guidelines

### Code Style

We follow these guidelines:
* **Black** for code formatting (line length: 100)
* **Ruff** for linting
* **Type hints** where practical
* **Docstrings** for functions and classes

Format your code before committing:
```bash
black app.py editor.py tasks.py settings.py
ruff check .
```

### Project Structure

```
terminallysimple/
├── app.py              # Main application and menu
├── editor.py           # Text editor implementation
├── tasks.py            # Task manager implementation
├── settings.py         # Settings screen
├── config.py           # Configuration management
├── constants.py        # Shared constants
├── base_screen.py      # Base classes for screens
├── dialogs/           # Modal dialogs
│   └── weather_dialogs.py
├── utils/             # Utility functions
│   ├── validators.py  # Input validation
│   └── weather.py     # Weather API integration
└── widgets/           # Custom widgets
    └── system_header.py

```

### Coding Principles

This project follows these principles:
1. **Minimalism** - Keep features simple and focused
2. **Clarity** - Code should be readable and self-documenting
3. **User Experience** - Distraction-free, keyboard-driven interface
4. **Zero Dependencies** - Minimize external dependencies when possible

### Adding New Features

When adding a new feature:
1. Discuss it in an issue first
2. Keep it minimal and focused
3. Follow the existing UI patterns
4. Add keyboard shortcuts (avoid mouse-only interactions)
5. Update README.md with usage instructions
6. Update CHANGELOG.md

### File Organization

* Put new screens in the root directory (e.g., `tasks.py`, `settings.py`)
* Put modal dialogs in `dialogs/`
* Put utility functions in `utils/`
* Put reusable widgets in `widgets/`

## Testing

### Manual Testing Checklist

Before submitting a PR, please test:

**Text Editor:**
- [ ] Create new file (Ctrl+N)
- [ ] Save file (Ctrl+S)
- [ ] Open existing file (Ctrl+O)
- [ ] Rename file (Ctrl+R)
- [ ] Autosave works (wait 30 seconds)
- [ ] Undo/Redo (Ctrl+Z, Ctrl+Y)
- [ ] Select all (Ctrl+A)

**Task Manager:**
- [ ] Add task (a)
- [ ] Edit task (e)
- [ ] Delete task (d)
- [ ] Toggle completion (Space)
- [ ] Clear completed (c)
- [ ] Tasks persist after restart

**Settings:**
- [ ] Change theme
- [ ] Theme persists after restart
- [ ] Theme preview works

**Weather:**
- [ ] Set city
- [ ] View forecast
- [ ] Change city
- [ ] Refresh weather

**General:**
- [ ] All keyboard shortcuts work
- [ ] Navigation (j/k, arrows) works
- [ ] No crashes on invalid input
- [ ] Clean exit (no errors)

### Automated Tests

We're working on adding more automated tests. For now, ensure your changes don't break existing functionality.

## Git Workflow

1. Create a feature branch from `main`:
```bash
git checkout -b feature/my-new-feature
```

2. Make your changes and commit with clear messages:
```bash
git commit -m "Add task priority feature"
```

3. Push to your fork:
```bash
git push origin feature/my-new-feature
```

4. Open a Pull Request against the `main` branch

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Examples:
```
Add task priority feature

- Add priority field to Task class
- Update UI to show priority indicator
- Add keyboard shortcuts to set priority

Closes #123
```

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## Recognition

Contributors will be recognized in the README.md file. Thank you for your contributions!

---

**Remember:** Keep it simple, keep it clean, keep it focused. That's the Terminally Simple way! ✨
