<p align="center">
<img width="1536" height="347" alt="logo-cutout" src="https://github.com/user-attachments/assets/7fccee89-0f30-4655-94cd-ef104ef39485" />
</p>


# Terminally Simple

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)

> One terminal app. Essential tools. Zero distractions.

A minimalist terminal application for distraction-free productivity. Built with [Textual](https://textual.textualize.io/).
Showcase of the app: https://imgur.com/a/rhskc5u

## Features

- **Text/Markdown Editor** — Distraction-free writing with autosave
- **Task Manager** — Simple to-do list
- **Weather Widget** — Real-time weather for any city
- **Pomodoro Timer** — Focus sessions with automatic breaks
- **11 Beautiful Themes** — Dark, light, and custom color schemes
- **Cross-platform** — Linux, macOS, Windows

## Installation

### Using pip

```bash
git clone https://github.com/firetin/terminallysimple.git
cd terminallysimple
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Using uv

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and run
git clone https://github.com/firetin/terminallysimple.git
cd terminallysimple
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python app.py
```

## Quick Start

### Text Editor
- `Ctrl+S` - Save | `Ctrl+O` - Open | `Ctrl+N` - New | `Ctrl+D` - Delete (in file browser)
- `Ctrl+R` - Rename | `Ctrl+A` - Select All | `Ctrl+Z/Y` - Undo/Redo
- Supports .md, .txt, and .text files
- Files saved to `notes/` folder with autosave every 30 seconds

### Task Manager
- `a` - Add | `e` - Edit | `d` - Delete | `Space` - Toggle complete
- `c` - Clear completed | `Shift+↑/↓` - Reorder tasks
- Click task to toggle completion

### Weather
- Press `w` anywhere to open weather forecast
- Click "Weather" in header to set city or view forecast
- `c` - Change city | `r` - Refresh forecast
- Free API from [Open-Meteo](https://open-meteo.com/)

### Pomodoro Timer
- Press `p` anywhere to open Pomodoro timer
- `s` - Start/Resume | `p` - Pause | `r` - Reset
- Default: 25 min work, 5 min break, 15 min long break (every 4 cycles)
- Notifications when sessions complete

### Settings
- Choose from 11 themes with live preview
- Settings auto-save

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

**Quick start (with uv):**
```bash
git clone https://github.com/firetin/terminallysimple.git
cd terminallysimple
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate
python app.py
```

## Support

- 🐛 [Report bugs](https://github.com/firetin/terminallysimple/issues)
- 💡 [Request features](https://github.com/firetin/terminallysimple/issues)
- 💬 [Discussions](https://github.com/firetin/terminallysimple/discussions)

## Requested features

1. ✅ ~~Be able to launch weather forecast feature via keyboard - add this option to the settings (note - make the app keyboard first and mouse optional)~~ - Press `w` anywhere!
2. ✅ ~~Pomodoro timer implemented in the top bar like the weather~~ - Press `p` anywhere!

## License

MIT License - Copyright (c) 2025 Firetin

---

⭐ Star this repo if you find it useful!
