<p align="center">
<img width="1536" height="347" alt="logo-cutout" src="https://github.com/user-attachments/assets/7fccee89-0f30-4655-94cd-ef104ef39485" />
</p>


# Terminally Simple

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)

> One terminal app. All your essential tools. Zero distractions.

A minimalist terminal application that consolidates your everyday tools into a single, elegant interface. Work with focus—write, check, create—without the noise of multiple apps.

**Built with [Textual](https://textual.textualize.io/) - Modern TUI framework for Python**

## Philosophy

Terminally Simple is built on the principle that productivity tools should be functional, lean, and distraction-free. Instead of juggling multiple applications, access everything you need from one clean terminal interface.

## Features

### Currently Available
- **Text/Markdown Editor** — Distraction-free writing and journaling with file browser
- **Task Manager** — Simple to-do list to track your tasks
- **Settings Screen** — Choose from 11 beautiful themes with live preview
- **Weather Widget** — Real-time weather and hourly forecast for any city worldwide
- **Cross-platform** — Works on Linux, macOS, and Windows

## Tech Stack

- **Primary**: [Textual](https://textual.textualize.io/) (Python TUI framework)
- **Language**: Python (open to other languages where they provide better efficiency)
- **Design**: Minimalist, functional, clean

## Installation

```bash
# Clone the repository
git clone https://github.com/firetin/terminallysimple.git
cd terminallysimple

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

## Usage

Launch the app and navigate through available tools using the menu. Each tool runs as an independent sub-program within the terminal interface.

```bash
python app.py
```

## Showcase

<img width="5511" height="2526" alt="ts-github" src="https://github.com/user-attachments/assets/5dc5880a-2145-42b5-a7ea-62a4b5bb7a72" />

### Text Editor
- Files are saved in the `notes/` folder within the app directory
- **Autosave:** Your work is automatically saved every 30 seconds
- Press `Ctrl+O` to browse and open saved files
- Press `Ctrl+S` to save your document
- Press `Ctrl+N` to start a new document
- Press `Ctrl+R` to rename the current file
- Press `Ctrl+A` to select all text
- Press `Ctrl+Z` to undo changes
- Press `Ctrl+Y` to redo changes
- Press `Escape` to return to the main menu
- Maximum data loss: 30 seconds (thanks to autosave)

### Task Manager
- Simple to-do list for tracking your tasks
- Press `a` to add a new task
- Press `d` to delete the focused task
- Press `e` to edit the focused task
- Press `Space` or `Enter` to toggle task completion
- Press `c` to clear all completed tasks
- Navigate with `j/k` or arrow keys
- Tasks are automatically saved to `~/.config/terminallysimple/tasks.json`
- Press `Escape` to return to the main menu

### Settings
- Press `2` from the main menu or navigate to Settings
- Choose from 11 beautiful themes with instant preview
- Navigate with `j/k` or arrow keys
- Press `Enter` to preview a theme
- Press `s` to save your selection
- Press `Escape` to cancel and restore original theme

### Weather Widget
- Click "Weather" in the top-right header to set up your city
- Shows real-time temperature and weather icon (☀️ ☁️ 💧 ❄️ ⛈️)
- Click again to view detailed hourly forecast
- Powered by [Open-Meteo API](https://open-meteo.com/) - completely free, no API key needed
- Updates automatically every 30 minutes
- Works for any city worldwide

### Available Themes
- Dark & Light (default Textual themes)
- Nord - Arctic-inspired palette
- Gruvbox - Retro warm colors
- Catppuccin (Mocha & Latte) - Soothing pastels
- Dracula - Popular purple-based theme
- Tokyo Night - Inspired by Tokyo at night
- Monokai - Classic coding theme
- Flexoki - Flexible, accessible colors
- Solarized Light - Scientific precision

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Philosophy
- **Clarity over complexity** - Code should be readable
- **Function over form** - Features should be practical
- **Simplicity over feature bloat** - Keep it minimal
- **Keyboard-driven** - Mouse optional

### Quick Start for Contributors
```bash
git clone https://github.com/firetin/terminallysimple.git
cd terminallysimple
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Support

- 🐛 **Found a bug?** [Open an issue](https://github.com/firetin/terminallysimple/issues/new?template=bug_report.md)
- 💡 **Have an idea?** [Request a feature](https://github.com/firetin/terminallysimple/issues/new?template=feature_request.md)
- 💬 **Questions?** Open a [discussion](https://github.com/firetin/terminallysimple/discussions)

## Roadmap

Future ideas (contributions welcome!):
- [ ] Task priorities and categories
- [ ] Calendar integration
- [ ] Export tasks to Markdown/CSV
- [ ] Pomodoro timer
- [ ] Plugin system

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License - See [LICENSE](LICENSE) for details.

Copyright (c) 2025 Firetin

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) by Textualize.io
- Weather data from [Open-Meteo](https://open-meteo.com/)
- Inspired by the Unix philosophy: Do one thing and do it well

---

**Built with focus. Designed for simplicity.**

⭐ Star this repo if you find it useful!
