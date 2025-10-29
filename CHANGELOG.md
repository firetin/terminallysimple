# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation
- CONTRIBUTING.md with development guidelines
- CODE_OF_CONDUCT.md for community standards
- Comprehensive code review and security audit

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
