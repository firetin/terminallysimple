# Contributing to Terminally Simple

Thanks for helping out! Please read our [Code of Conduct](CODE_OF_CONDUCT.md) first.

## How to contribute

### Reporting bugs

Check existing issues first, then open one with:

* a clear title and description
* steps to reproduce
* expected vs. actual behaviour
* environment details (OS, Python version, terminal)

### Suggesting features

Open an issue describing the feature, why it is useful and how it fits the
"keyboard-first, zero distraction" goal. Small, focused features land fastest.

## Development setup

Requires Python 3.10+.

```bash
git clone https://github.com/firetin/terminallysimple.git
cd terminallysimple
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
terminallysimple               # or: python -m app
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv venv
uv pip install -e ".[dev]"
uv run terminallysimple
```

`pre-commit install` wires the linters into your commits.

## Checks before opening a pull request

```bash
ruff check .
ruff format --check .
mypy .
python -m pytest --cov
```

All four run in CI on Linux, macOS and Windows for Python 3.10–3.13.
The workflow lives in `ci/github-actions-ci.yml`; move it to
`.github/workflows/ci.yml` to enable it on your fork.

## Tests

The UI tests use Textual's `run_test()` driver and run headless:

```python
async def test_something(pilot) -> None:
    app = TerminallySimple()
    async with app.run_test() as pilot:
        await pilot.press("1")
        assert isinstance(app.screen, EditorScreen)
```

`tests/conftest.py` redirects `HOME`/`XDG_*` to a temporary directory for every
test, so tests never touch your real notes, tasks or settings. Please keep it
that way (use `tmp_path`, never the user's home directory).

## Guidelines

* **Keep it simple** — minimal, focused features.
* **Keyboard-first** — every action needs a key binding and must appear in `?` help.
* **Never lose user data** — write through `utils.storage` (atomic writes), keep
  autosave test coverage green.
* **State lives in services** — `services.py` owns cross-screen state; widgets are views.
* **Style** — `ruff format` (100 columns) and the ruff rules in `pyproject.toml`.

## Pull requests

```bash
git checkout -b feature/my-feature
# make changes
git commit -m "Add feature description"
git push origin feature/my-feature
```

Use present-tense commit messages ("Add feature", not "Added feature") and keep
a pull request focused on one thing.
