<p align="center">
<img width="1536" height="347" alt="logo-cutout" src="https://github.com/user-attachments/assets/7fccee89-0f30-4655-94cd-ef104ef39485" />
</p>

# Terminally Simple

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)

> One terminal app. Essential tools. Zero distractions.

A minimalist, keyboard-first terminal application for distraction-free productivity.
Built with [Textual](https://textual.textualize.io/).

Showcase: https://imgur.com/a/rhskc5u

## Features

- **Editor** — Markdown/text notes with autosave, crash recovery, rename and file browser;
  reopens the note you were last writing and shows a live word count
- **Task manager** — add, edit, complete, reorder, undo and clear tasks (persisted)
- **Weather** — current conditions, hourly and 3-day forecast for any city
  ([Open-Meteo](https://open-meteo.com/), no API key, °C or °F)
- **Pomodoro** — 25/5/15 focus cycles that keep running while you switch screens
- **Themes & units** — 11 themes with non-destructive preview, °C or °F
- **Safe by default** — atomic writes, backups, autosave recovery, quit confirmation
- **Cross-platform** — Linux, macOS and Windows (XDG / AppData / Application Support)

## Installation

```bash
pipx install terminallysimple     # recommended: isolated, adds the `terminallysimple` command
terminallysimple
```

or with pip:

```bash
pip install terminallysimple
terminallysimple
```

From a git checkout:

```bash
git clone https://github.com/firetin/terminallysimple.git
cd terminallysimple
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e .
terminallysimple               # or: python -m app
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv venv
uv pip install -e .
uv run terminallysimple
```

### Command line

```text
terminallysimple --version
terminallysimple --notes-dir ~/notes     # override the notes folder
terminallysimple --log-level DEBUG       # more detail in the log file
```

## Keyboard reference

Press `?` (or `F1`) anywhere to see the bindings for the current screen.

### Everywhere

| Key | Action |
| --- | --- |
| `Ctrl+W` | Weather forecast (or city setup) |
| `Ctrl+P` | Pomodoro timer |
| `?` / `F1` | Help |
| `Ctrl+Q` | Quit (asks first if there is unsaved work) |

### Main menu

| key | action |
| --- | --- |
| `1` / `2` / `3` | Editor / Tasks / Settings |
| `w`, `p` | Weather, Pomodoro |
| `↑`/`k`, `↓`/`j`, `Enter`, `q` | Navigate, select, quit |

### Editor

| Key | Action |
| --- | --- |
| `Ctrl+S` | Save (asks for a name the first time, confirms overwrites) |
| `Ctrl+O` | Open a note |
| `Ctrl+N` | New note |
| `Ctrl+R` | Rename |
| `Ctrl+A`, `Ctrl+Z`, `Ctrl+Y` | Select all, undo, redo |
| `Tab` | Indent |
| `Esc` | Back to the menu |

Notes are stored in your documents folder as Markdown. Anything unsaved is
snapshotted every 30 seconds, when you leave the editor and when the app quits —
on the next start you are asked whether to restore it.

### Task manager

| Key | Action |
| --- | --- |
| `a` / `e` / `d` | Add / edit / delete |
| `Space` or `Enter` | Toggle complete |
| `Shift+↑` / `Shift+↓` | Reorder |
| `c` | Clear completed |
| `Ctrl+Z` | Undo the last delete / edit / clear |
| `Esc` | Back |

### Weather dialog

`c` change city · `r` refresh · `Enter`/`Esc` close (shows today plus the next days)

### Pomodoro dialog

`s` start/resume · `p` pause · `r` reset · `Esc` close

## Where data lives

| What | Linux | macOS | Windows |
| --- | --- | --- | --- |
| Notes | `~/Documents/Terminally Simple` | `~/Documents/Terminally Simple` | `%USERPROFILE%\Documents\Terminally Simple` |
| Settings | `~/.config/terminallysimple` | `~/Library/Application Support/terminallysimple` | `%APPDATA%\terminallysimple` |
| Tasks, weather cache, log, autosave | `~/.local/share/terminallysimple` | `~/Library/Application Support/terminallysimple` | `%LOCALAPPDATA%\terminallysimple` |

Old `notes/` folders and `~/.config/terminallysimple/tasks.json` are migrated
automatically on first run.

## Development

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check .
mypy .
python -m pytest --cov
```

See [CONTRIBUTING.md](CONTRIBUTING.md). The test suite runs headless through
Textual's `run_test()` driver, so no terminal is required.

## Support

- 🐛 [Report bugs](https://github.com/firetin/terminallysimple/issues)
- 💡 [Request features](https://github.com/firetin/terminallysimple/issues)
- 💬 [Discussions](https://github.com/firetin/terminallysimple/discussions)

## License

MIT License - Copyright (c) 2025 Firetin

---

⭐ Star this repo if you find it useful!
