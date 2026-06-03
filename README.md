# Dialogue Tree Visualizer

A node-based dialogue editor for creating, debugging, and managing branching narrative structures used in games and visual novels.

Built with Python and Tkinter — no external dependencies required.

[⬇ Download v1.0.0 (Windows)](https://github.com/CD-Portfolio/Dialogue-Tree-Visualizer/releases/tag/v1.0.0)

---

## Screenshots

### Main Editor

<img width="1920" height="1020" alt="main_editor" src="https://github.com/user-attachments/assets/977a1d3a-9718-4119-8eab-88b15f79b448" />

### Branching Dialogue

<img width="1920" height="1020" alt="branching" src="https://github.com/user-attachments/assets/aa89db0c-ea8d-47ec-b6e1-33d9dda605db" />

### Editing Workflow

<img width="1920" height="1020" alt="editing" src="https://github.com/user-attachments/assets/a15595a0-44b9-4f2f-ac0b-ad36f0ac0bc3" />

### Validation System

<img width="477" height="540" alt="validation_panel" src="https://github.com/user-attachments/assets/f306845c-eacb-40eb-860c-c33dcb524fa3" />

<img width="1920" height="1020" alt="validation_canvas" src="https://github.com/user-attachments/assets/c1503623-f199-46b2-921f-bd4bd56b32ab" />

---

## Features

- **Canvas** — drag nodes, pan, zoom, inline rename, context menus
- **Editing** — create, duplicate, delete nodes; edit speaker, text, choices
- **Visualization** — auto-rendered graph with arrows and choice labels
- **Validation** — detects broken links, unreachable nodes, dead ends; highlights errors on canvas
- **Search** — find nodes by ID, speaker, or text; jump-to-node
- **History** — undo / redo up to 60 steps
- **Data** — JSON import/export with persistent node positions

---

## Installation

```bash
git clone https://github.com/CD-Portfolio/Dialogue-Tree-Visualizer.git
cd Dialogue-Tree-Visualizer
python ui/main_window.py
```

Python 3.10+ required. No external dependencies.

Or just [download the Windows build](https://github.com/CD-Portfolio/Dialogue-Tree-Visualizer/releases/tag/v1.0.0) — unzip and run `main_window.exe`.

---

## Project Structure

```
Dialogue-Tree-Visualizer/
├── core/               # dialogue data model and JSON serialization
├── ui/                 # canvas, panels, editor logic
│   └── main_window.py  # entry point
├── data/               # example dialogue files
├── main.py             # legacy CLI preview
└── requirements.txt
```

---

## Motivation

Narrative-heavy games depend on tools that can visualize and manage complex branching structures. This project explores editor development and narrative tooling — building a dedicated system for creating, editing, validating, and debugging dialogue trees from scratch.

---

License
MIT
## License

MIT
