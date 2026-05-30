import tkinter as tk
import sys
import os
import json
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.dialogue_tree import load_dialogue_from_json, DialogueNode

# ── ТЁМНАЯ ТЕМА ──────────────────────────────────────────
BG_COLOR = "#1e1e2e"
PANEL_BG = "#282a36"

NODE_BORDER = "#44475a"
NODE_START = "#f1fa8c"

TEXT_PRIMARY = "#f8f8f2"
TEXT_SPEAKER = "#ff79c6"
TEXT_CHOICE = "#8be9fd"
LINE_COLOR = "#6272a4"

SPEAKER_COLORS = {
    "Geralt": "#2d4a3e",
    "Villager": "#4a2d2d",
}

# ── Константы ──────────────────────────────────────────
CANVAS_WIDTH, CANVAS_HEIGHT = 1080, 780
NODE_WIDTH, NODE_HEIGHT = 250, 100
LEVEL_SPACING = 180

# ── Окно ───────────────────────────────────────────────
window = tk.Tk()
window.geometry("1400x800")
window.title("DTV - Dialogue Editor")
window.configure(bg=BG_COLOR)

main_frame = tk.Frame(window, bg=BG_COLOR)
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(
    main_frame,
    width=CANVAS_WIDTH,
    height=CANVAS_HEIGHT,
    bg=BG_COLOR,
    highlightthickness=0
)
canvas.pack(side=tk.LEFT)

panel = tk.Frame(main_frame, width=300, bg=PANEL_BG, relief=tk.SUNKEN, bd=2)
panel.pack(side=tk.RIGHT, fill=tk.Y)

# ── Панель ─────────────────────────────────────────────
tk.Label(panel, text="Node Details", font=("Arial", 12, "bold"),
         bg=PANEL_BG, fg=TEXT_PRIMARY).pack(pady=10)

tk.Label(panel, text="Speaker:", bg=PANEL_BG, fg=TEXT_PRIMARY,
         font=("Arial", 9, "bold")).pack(pady=(10, 0))

speaker_entry = tk.Entry(panel, width=30)
speaker_entry.pack(pady=5)

tk.Label(panel, text="Text:", bg=PANEL_BG, fg=TEXT_PRIMARY,
         font=("Arial", 9, "bold")).pack()

text_entry = tk.Text(
    panel,
    width=30,
    height=6,
    bg="#1f1f2e",
    fg=TEXT_PRIMARY,
    insertbackground=TEXT_PRIMARY
)
text_entry.pack(pady=5)

panel_text = tk.Label(panel, text="Click a node to edit",
                      bg=PANEL_BG, fg=TEXT_PRIMARY, wraplength=280)
panel_text.pack(pady=5)

# ── Данные ─────────────────────────────────────────────
tree = load_dialogue_from_json("data/example_dialogue.json")

selected_node_id = None
node_positions = {}

# ── Лэйаут ─────────────────────────────────────────────
def compute_layout():
    queue = deque([tree.start_node_id])
    levels = {tree.start_node_id: 0}
    order_per_level = {}

    while queue:
        current = queue.popleft()
        level = levels[current]

        order_per_level.setdefault(level, []).append(current)

        for choice in tree.nodes[current].choices:
            nxt = choice["next_node_id"]
            if nxt not in levels:
                levels[nxt] = level + 1
                queue.append(nxt)

    return levels, order_per_level


def draw_nodes(levels, order_per_level):
    for level, nodes in order_per_level.items():
        count = len(nodes)
        if count == 0:
            continue

        gap = (CANVAS_WIDTH - count * NODE_WIDTH) / (count + 1)

        for i, node_id in enumerate(nodes):
            node = tree.nodes[node_id]

            x1 = gap + i * (NODE_WIDTH + gap)
            y1 = 50 + level * LEVEL_SPACING
            x2, y2 = x1 + NODE_WIDTH, y1 + NODE_HEIGHT

            canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=NODE_BORDER,
                fill=SPEAKER_COLORS.get(node.speaker, "#2a2a3e"),
                width=2
            )

            if node_id == tree.start_node_id:
                canvas.create_rectangle(
                    x1-4, y1-4, x2+4, y2+4,
                    outline=NODE_START,
                    width=3
                )

            canvas.create_text(
                (x1+x2)/2, y1+20,
                text=node.speaker,
                font=("Arial", 9, "bold"),
                fill=TEXT_SPEAKER
            )

            canvas.create_line(
                x1+10, y1+35, x2-10, y1+35,
                fill=LINE_COLOR
            )

            canvas.create_text(
                (x1+x2)/2, y1+65,
                text=node.text,
                width=220,
                font=("Arial", 8),
                fill=TEXT_PRIMARY
            )

            node_positions[node_id] = {
                "x1": x1, "y1": y1,
                "x2": x2, "y2": y2
            }


def draw_edges():
    for node_id, node in tree.nodes.items():
        if node_id not in node_positions:
            continue

        for choice in node.choices:
            nxt = choice["next_node_id"]
            if nxt not in node_positions:
                continue

            s = node_positions[node_id]
            e = node_positions[nxt]

            sx, sy = (s["x1"]+s["x2"])/2, s["y2"]
            ex, ey = (e["x1"]+e["x2"])/2, e["y1"]

            canvas.create_line(
                sx, sy, ex, ey,
                arrow=tk.LAST,
                fill=LINE_COLOR,
                width=2
            )

            canvas.create_text(
                (sx+ex)/2,
                (sy+ey)/2,
                text=choice["text"],
                width=150,
                fill=TEXT_CHOICE,
                font=("Arial", 8)
            )


def redraw():
    canvas.delete("all")
    node_positions.clear()

    levels, order_per_level = compute_layout()
    draw_nodes(levels, order_per_level)
    draw_edges()

    canvas.bind("<Button-1>", on_click)


# ── UI логика ──────────────────────────────────────────
def on_click(event):
    global selected_node_id

    for node_id, pos in node_positions.items():
        if (pos["x1"] <= event.x <= pos["x2"] and
            pos["y1"] <= event.y <= pos["y2"]):

            selected_node_id = node_id
            node = tree.nodes[node_id]

            speaker_entry.delete(0, tk.END)
            speaker_entry.insert(0, node.speaker)

            text_entry.delete("1.0", tk.END)
            text_entry.insert("1.0", node.text)

            panel_text.config(text=f"Editing: {node_id}")
            return


def add_node():
    new_id = f"node_{len(tree.nodes)+1:03d}"
    tree.nodes[new_id] = DialogueNode(
        new_id,
        "New Speaker",
        "New dialogue text"
    )
    panel_text.config(text=f"Created: {new_id}")
    redraw()


def save_node():
    if not selected_node_id:
        panel_text.config(text="No node selected!")
        return

    node = tree.nodes[selected_node_id]
    node.speaker = speaker_entry.get()
    node.text = text_entry.get("1.0", tk.END).strip()

    panel_text.config(text=f"Node {selected_node_id} updated")
    redraw()


def save_json():
    data = {
        "title": tree.title,
        "start_node_id": tree.start_node_id,
        "nodes": [n.to_dict() for n in tree.nodes.values()]
    }

    with open("data/example_dialogue.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    panel_text.config(text="Saved")


# ── Кнопки ─────────────────────────────────────────────
tk.Button(panel, text="+ Add Node",
          bg="#2d4a3e", fg=TEXT_PRIMARY,
          command=add_node).pack(pady=5)

tk.Button(panel, text="Save Node",
          bg="#4a2d4a", fg=TEXT_PRIMARY,
          command=save_node).pack(pady=5)

tk.Button(panel, text="Save JSON",
          bg="#3a3a2a", fg=TEXT_PRIMARY,
          command=save_json).pack(pady=5)

# ── Старт ──────────────────────────────────────────────
redraw()
window.mainloop()