# Terminally Simple

> One terminal app. All your essential tools. Zero distractions.

A minimalist terminal application that consolidates your everyday tools into a single, elegant interface. Work with focus—write, check, create—without the noise of multiple apps.

## Philosophy

Terminally Simple is built on the principle that productivity tools should be functional, lean, and distraction-free. Instead of juggling multiple applications, access everything you need from one clean terminal interface.

## Features

### Currently Available
- **Text/Markdown Editor** — Distraction-free writing and journaling with file browser
- **Theme Customization** — Use the palette (Ctrl+P) to change themes

### Roadmap
- [ ] Weather forecast widget
- [ ] Website security checker (ethical verification)
- [ ] Calculator
- [ ] Quick notes
- [ ] Task manager
- [ ] More tools based on community feedback

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
pip install textual

# Run the app
python app.py
```

## Usage

Launch the app and navigate through available tools using the menu. Each tool runs as an independent sub-program within the terminal interface.

```bash
python app.py
```

### Text Editor
- Files are saved in the `notes/` folder within the app directory
- Press `Ctrl+O` to browse and open saved files
- Press `Ctrl+S` to save (auto-generates timestamped filename)
- Press `Ctrl+N` to start a new document

## Contributing

Contributions are welcome! Please keep the minimalist philosophy in mind:
- Clarity over complexity
- Function over form
- Simplicity over feature bloat

## License

See [LICENSE](LICENSE) for details.

---

**Built with focus. Designed for simplicity.**
