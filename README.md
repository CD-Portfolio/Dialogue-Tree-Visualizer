# Dialogue Tree Visualizer

A node-based dialogue editor and visualization tool designed for creating, debugging, and managing branching narrative structures used in games.

Built with Python and Tkinter, this project focuses on narrative tooling, editor development, and interactive workflow design for dialogue-heavy games and visual novels.

---

# Features

## Interactive Canvas System

* Node-based graphical dialogue editor
* Drag-and-drop node positioning
* Canvas panning and zooming
* Background grid system
* Selectable and movable nodes
* Inline node renaming directly on canvas

## Dialogue Editing

* Create, duplicate, rename, and delete nodes
* Edit dialogue text and speaker information
* Create and modify branching choices
* Context menus for faster workflow

## Visualization

* Automatic dialogue graph rendering
* Arrow-based node connections
* Choice labels displayed on graph edges
* Color-coded speaker headers

## Navigation Tools

* Search by node ID
* Search by speaker name
* Search dialogue text
* Jump-to-node functionality
* Breadcrumb navigation

## Validation & Debugging

* Broken reference detection
* Unreachable node detection
* Dead-end detection
* Problem node highlighting
* Validation jump tools

## History System

* Undo / Redo support
* Tracks editing operations
* Tracks node movement
* Tracks structural modifications

## Data Management

* JSON import/export support
* Persistent node positions
* Automatic graph reconstruction from saved files

---

# Screenshots

## Main Editor

<img width="1920" height="1020" alt="main_editor" src="https://github.com/user-attachments/assets/977a1d3a-9718-4119-8eab-88b15f79b448" />

## Branching Dialogue Example

<img width="1920" height="1020" alt="Снимок экрана 2026-06-03 142014" src="https://github.com/user-attachments/assets/aa89db0c-ea8d-47ec-b6e1-33d9dda605db" />

## Editing Workflow

<img width="1920" height="1020" alt="Снимок экрана 2026-06-03 142050" src="https://github.com/user-attachments/assets/a15595a0-44b9-4f2f-ac0b-ad36f0ac0bc3" />

## Validation System

<img width="477" height="540" alt="Снимок экрана 2026-06-03 142103" src="https://github.com/user-attachments/assets/f306845c-eacb-40eb-860c-c33dcb524fa3" />

<img width="1920" height="1020" alt="Снимок экрана 2026-06-03 142156" src="https://github.com/user-attachments/assets/c1503623-f199-46b2-921f-bd4bd56b32ab" />

---

# Installation

Clone repository:

```bash
git clone https://github.com/CD-Portfolio/Dialogue-Tree-Visualizer.git
cd Dialogue-Tree-Visualizer
```

Run:

```bash
python main.py
```

Requirements:

```text
Python 3.10+
No external dependencies required
```

---

# Project Structure

```text
Dialogue-Tree-Visualizer/

├── core/        # dialogue data structures and serialization

├── ui/          # editor interface and canvas systems

├── data/        # example dialogue files

├── main.py

├── requirements.txt
```

---

# Motivation

Narrative-heavy games rely heavily on tools capable of visualizing and managing complex branching structures.

This project was created to explore editor development and narrative tooling by building a dedicated system for creating, editing, validating, and debugging dialogue trees.

The focus of this project is not only dialogue visualization, but also workflow design for interactive narrative development.

---

# Current Development Goals

* Improved editor workflow
* Larger dialogue support
* Additional quality-of-life features
* Better usability for large narrative projects

---

# Why This Project?

This project combines:

* Narrative systems
* Tool programming
* Graph visualization
* Interactive GUI development
* Data serialization
* Workflow engineering

The goal is to build a lightweight narrative editor suitable for game development workflows.

---

# License

MIT License
