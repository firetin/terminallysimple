# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-01

### Fixed — data safety
- Unsaved editor content is no longer lost: the buffer is snapshotted on autosave,
  on screen change, on unmount and on app shutdown (previously `on_unmount` raised
  `NoMatches` and nothing was written)
- Notes, tasks and settings are written atomically (temp file + `os.replace`) and
  keep a `.bak`; corrupt files are quarantined instead of being overwritten
- A single malformed task record no longer discards the whole task list
- Saving over an existing note asks for confirmation
- Recovering an autosave snapshot is now an explicit prompt instead of a silent load
- Quitting with unsaved changes asks first (`Ctrl+Q` / menu Exit)

### Fixed — behaviour
- `Ctrl+W` / `Ctrl+P` are priority shortcuts, so weather and Pomodoro work while
  typing in the editor (plain `w`/`p` still type text)
- Hourly forecasts are filtered in the city's timezone (Tokyo no longer shows hours
  that already passed), and the in-memory weather cache is keyed by coordinates
- Theme preview no longer persists without pressing `s`; `Esc` restores the saved theme
- Pomodoro and weather state live in app services, so the timer keeps running when
  you switch screens instead of resetting per screen
- Header is built from real widgets with a CSS layout: no more manual padding,
  emoji width drift or overflow on narrow terminals (optional parts hide instead)
- Notes moved out of the package directory into the platform documents folder, with
  automatic migration of the old `notes/` folder
- Tasks/config/log paths follow XDG/AppData/Application Support via `platformdirs`
- Log rotation (1 MB × 3) instead of an unbounded `app.log`

### Added
- Help screen (`?` or `F1`) generated from the active bindings
- 3-day forecast in the weather dialog (daily min/max and conditions)
- The editor reopens the note you were last writing and shows a live word count
- `Ctrl+Z` in the task manager undoes the last delete, edit or clear
- Temperature units (°C/°F) in Settings
- Weather disk cache plus "last updated" in the forecast dialog, and clearer errors
- `--version`, `--notes-dir` and `--log-level` command line options
- `py.typed`, real `[project.scripts]` packaging, `pip install -e .` works
- GitHub Actions CI (ruff, mypy, pytest on 3 OS × 4 Python versions), pre-commit,
  dependabot, PR template and `SECURITY.md`

### Changed
- Requires Python 3.10+ and `textual>=0.86` (the old floor could not provide themes)
- Test suite replaced: 53 headless `pytest` tests covering editor, tasks, settings,
  services, storage and weather parsing (the previous files were scripts that made
  `pytest` crash on import)
- Documentation rewritten; stale implementation notes removed

## [0.1.0] - 2025-10-29

### Added
- Text/Markdown Editor with distraction-free writing experience
  - Auto-save every 30 seconds
  - File browser for opening saved files
  - Undo/Redo support (Ctrl+Z, Ctrl+Y)
  - Select all (Ctrl+A)
  - Rename files (Ctrl+R)
  - Files saved to `notes/` directory
  
- Task Manager (To-Do List)
  - Add, edit, delete tasks
  - Mark tasks as complete/incomplete
  - Clear all completed tasks
  - Tasks persist to `~/.config/terminallysimple/tasks.json`
  - Keyboard-driven interface
  
- Settings Screen
  - 11 beautiful themes to choose from
  - Live theme preview
  - Persistent theme selection
  
- Weather Widget
  - Real-time weather display in header
  - Hourly forecast view
  - City search with geocoding
  - Data from Open-Meteo API (free, no API key required)
  - 30-minute weather cache
  - Updates automatically
  
- System Resource Monitor
  - CPU usage display
  - RAM usage display
  - Color-coded indicators (green/yellow/red)
  
- Core Features
  - Keyboard-driven navigation (j/k or arrow keys)
  - Minimalist, distraction-free interface
  - Cross-platform support (Linux, macOS, Windows)
  - Configuration saved to `~/.config/terminallysimple/`
  - Logging to file for debugging

### Security
- Input validation and sanitization for filenames
- Path traversal protection
- Safe file operations
- No hardcoded credentials

### Documentation
- Comprehensive README.md
- MIT License
- Usage instructions for all features
- Installation guide

---

## Release Notes

### Version 0.1.0 - Initial Release

This is the first public release of Terminally Simple! 🎉

**Terminally Simple** is a minimalist terminal application that consolidates your everyday tools into a single, elegant interface. Built with Python and [Textual](https://textual.textualize.io/), it provides:

- **Distraction-free text editing** for notes and journaling
- **Simple task management** to track your to-dos
- **Beautiful themes** to customize your experience
- **Weather at a glance** right in the header
- **Zero distractions** - focus on what matters

Perfect for users who love working in the terminal and want a unified, keyboard-driven experience for common productivity tasks.

---

### Future Plans

Ideas for future versions (not committed):
- Task priorities and categories
- Export tasks to Markdown/CSV
- Calendar integration
- Pomodoro timer
- More customization options
- Plugin system

Want to contribute? Check out [CONTRIBUTING.md](CONTRIBUTING.md)!

---

[Unreleased]: https://github.com/firetin/terminallysimple/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/firetin/terminallysimple/releases/tag/v0.1.0
