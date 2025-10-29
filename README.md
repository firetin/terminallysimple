# Terminally Simple

> One terminal app. All your essential tools. Zero distractions.

A minimalist terminal application that consolidates your everyday tools into a single, elegant interface. Work with focus—write, check, create—without the noise of multiple apps.

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

## Showcase (early in development)

<img width="2528" height="1291" alt="1" src="https://github.com/user-attachments/assets/895d0d46-5bb6-46ba-bc0f-b5e07c8ffa65" />
<img width="2529" height="1289" alt="2" src="https://github.com/user-attachments/assets/dda84da4-4db7-43f4-8989-38c03e8b9d84" />
<img width="2532" height="1291" alt="3" src="https://github.com/user-attachments/assets/2554e50b-0d4c-4254-a0ab-cc24f33478d2" />

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

Contributions are welcome! Please keep the minimalist philosophy in mind:
- Clarity over complexity
- Function over form
- Simplicity over feature bloat

## Notes
Total time spent on development so far: 2 hours
28.10.2025 - 20:00-22:30

## License

See [LICENSE](LICENSE) for details.

---

**Built with focus. Designed for simplicity.**
