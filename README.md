---

# Dialogue Tree Visualizer

A node-based editor for creating and inspecting branching dialogue graphs used in narrative-driven games.

The tool provides a structured representation of dialogue systems and supports editing, validation, and JSON-based serialization of graph data.

Built with Python and Tkinter.

---

# Features

## Graph Editor

* Node-based dialogue representation on a 2D canvas
* Drag-and-drop node positioning
* Node creation, duplication, deletion
* Inline editing of node properties
* Context menu-based node operations

## Dialogue Structure

* Speaker and text fields per node
* Multiple outgoing choices per node
* Directed graph representation of dialogue flow
* Persistent node position storage

## Visualization

* Automatic rendering of node connections
* Directed edges between dialogue nodes
* Choice labels displayed on connections
* Visual distinction of node states

## Navigation

* Search by node ID
* Search by speaker or dialogue text
* Direct navigation to selected nodes

## Validation System

* Detection of invalid node references
* Detection of unreachable nodes
* Detection of dead-end nodes
* Visual highlighting of issues on graph

## History System

* Undo / redo support
* Tracks structural and positional changes
* Command-based history stack (up to 60 states)

## Data Management

* JSON import/export support
* Full graph serialization
* Persistent node layout storage
* Automatic reconstruction from saved data

---

# Screenshots

## Main Editor

<img width="1920" height="1020" src="https://github.com/user-attachments/assets/977a1d3a-9718-4119-8eab-88b15f79b448" />

Core editing interface with node-based dialogue graph representation.

## Branching Dialogue

<img width="1920" height="1020" src="https://github.com/user-attachments/assets/aa89db0c-ea8d-47ec-b6e1-33d9dda605db" />

Example of branching dialogue structure with multiple paths between nodes.

## Editing Workflow

<img width="1920" height="1020" src="https://github.com/user-attachments/assets/a15595a0-44b9-4f2f-ac0b-ad36f0ac0bc3" />

Node editing workflow showing inline modifications and graph restructuring.

## Validation System

<img width="477" height="540" src="https://github.com/user-attachments/assets/f306845c-eacb-40eb-860c-c33dcb524fa3" />

Validation output highlighting structural issues in the dialogue graph.

## Validation Overview

<img width="1920" height="1020" src="https://github.com/user-attachments/assets/c1503623-f199-46b2-921f-bd4bd56b32ab" />

Graph-level validation view showing detected issues across the dialogue structure.

---

# Installation

Clone repository:

```bash
git clone https://github.com/CD-Portfolio/Dialogue-Tree-Visualizer.git
cd Dialogue-Tree-Visualizer
```

Run application:

```bash
python main.py
```

---

# Requirements

```text
Python 3.10+
No external dependencies required
```

---

# Project Structure

```text
Dialogue-Tree-Visualizer/

├── core/        # data model and serialization logic
├── ui/          # editor interface and canvas system
├── data/        # example dialogue files
├── main.py      # entry point
├── requirements.txt
├── LICENSE
```

---

# System Overview

The project implements a graph-based dialogue editor where nodes represent dialogue entries and edges define branching transitions.

The system supports:

* interactive graph editing
* structural validation of dialogue trees
* JSON-based serialization
* visual inspection of node relationships

The focus is on data integrity, workflow support, and structured narrative authoring.

---

# Notes

The tool is intended for prototyping branching dialogue systems and experimenting with narrative structure design.

It is not tied to any specific game engine.

---

# License

MIT License
