import tkinter as tk
import sys
import os
import json
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.dialogue_tree import load_dialogue_from_json, DialogueNode

# Константы
CANVAS_WIDTH, CANVAS_HEIGHT = 1080, 780
NODE_WIDTH, NODE_HEIGHT = 250, 100
LEVEL_SPACING = 180
SPEAKER_COLORS = {
    "Geralt": "#d4e8d4",
    "Villager": "#e8d4d4",
}

# Окно
window = tk.Tk()
window.geometry("1400x800")
window.title("DTV - Dialogue Editor")

# Главный фрейм
main_frame = tk.Frame(window)
main_frame.pack(fill=tk.BOTH, expand=True)

# Canvas слева
canvas = tk.Canvas(main_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="lightblue")
canvas.pack(side=tk.LEFT)

# Панель справа
panel = tk.Frame(main_frame, width=300, height=780, bg="white", relief=tk.SUNKEN, bd=2)
panel.pack(side=tk.RIGHT, fill=tk.Y)

panel_title = tk.Label(panel, text="Node Details", font=("Arial", 12, "bold"), bg="white")
panel_title.pack(pady=10)

tk.Label(panel, text="Speaker:", bg="white", font=("Arial", 9, "bold")).pack(pady=(10, 0))
speaker_entry = tk.Entry(panel, width=30)
speaker_entry.pack(pady=5)

tk.Label(panel, text="Text:", bg="white", font=("Arial", 9, "bold")).pack()
text_entry = tk.Text(panel, width=30, height=6)
text_entry.pack(pady=5)

panel_text = tk.Label(panel, text="Click a node to edit", bg="white", wraplength=280)
panel_text.pack(pady=5)

# Загрузка данных
tree = load_dialogue_from_json("data/example_dialogue.json")

selected_node_id = None

def add_node():
    new_id = f"node_{len(tree.nodes)+1:03d}"
    tree.nodes[new_id] = DialogueNode(
        node_id=new_id,
        speaker="New Speaker",
        text="New dialogue text"
    )
    panel_text.config(text=f"Created: {new_id}")

def save_json():
    data = {
        "title": tree.title,
        "start_node_id": tree.start_node_id,
        "nodes": [node.to_dict() for node in tree.nodes.values()]
    }
    with open("data/example_dialogue.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    panel_text.config(text="Saved successfully!")

def save_node():
    if not selected_node_id:
        panel_text.config(text="No node selected!")
        return

    node = tree.nodes[selected_node_id]
    node.speaker = speaker_entry.get()
    node.text = text_entry.get("1.0", tk.END).strip()
    panel_text.config(text=f"Node {selected_node_id} updated!")

tk.Button(
    panel,
    text="+ Add Node",
    font=("Arial", 10),
    bg="#d4e8d4",
    command=add_node
).pack(pady=10)

tk.Button(
    panel,
    text="💾 Save JSON",
    font=("Arial", 10),
    bg="#d4e8d4",
    command=save_json
).pack(pady=10)

tk.Button(
    panel,
    text="✏️ Save Node",
    font=("Arial", 10),
    bg="#d4d4e8",
    command=save_node
).pack(pady=5)

# BFS — уровни узлов
queue = deque([tree.start_node_id])
levels = {tree.start_node_id: 0}

while queue:
    current_id = queue.popleft()
    for choice in tree.nodes[current_id].choices:
        next_id = choice["next_node_id"]
        if next_id not in levels:
            levels[next_id] = levels[current_id] + 1
            queue.append(next_id)

# Группировка по уровням
nodes_per_level = {}
for node_id, level in levels.items():
    nodes_per_level.setdefault(level, []).append(node_id)

# Позиции узлов
node_positions = {}

# Рисование узлов
for node_id, node in tree.nodes.items():
    level = levels[node_id]
    siblings = nodes_per_level[level]
    position = siblings.index(node_id)
    count = len(siblings)

    gap = (CANVAS_WIDTH - count * NODE_WIDTH) / (count + 1)
    x1 = gap + position * (NODE_WIDTH + gap)
    y1 = 50 + level * LEVEL_SPACING
    x2, y2 = x1 + NODE_WIDTH, y1 + NODE_HEIGHT

    canvas.create_rectangle(
        x1, y1, x2, y2,
        outline="black",
        fill=SPEAKER_COLORS.get(node.speaker, "#f0f0f0"),
        width=2
    )

    if node_id == tree.start_node_id:
        canvas.create_rectangle(x1-4, y1-4, x2+4, y2+4, outline="gold", width=3)

    canvas.create_text(
        (x1+x2)/2, y1+20,
        text=node.speaker,
        font=("Arial", 9, "bold"),
        fill="darkred"
    )

    canvas.create_line(
        x1+10, y1+35,
        x2-10, y1+35,
        fill="gray"
    )

    canvas.create_text(
        (x1+x2)/2, y1+65,
        text=node.text,
        width=220,
        font=("Arial", 8),
        fill="black"
    )

    node_positions[node_id] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}

# Клик по узлу
def on_click(event):
    global selected_node_id
    for node_id, pos in node_positions.items():
        if pos["x1"] <= event.x <= pos["x2"] and pos["y1"] <= event.y <= pos["y2"]:
            selected_node_id = node_id
            node = tree.nodes[node_id]
            speaker_entry.delete(0, tk.END)
            speaker_entry.insert(0, node.speaker)
            text_entry.delete("1.0", tk.END)
            text_entry.insert("1.0", node.text)
            panel_text.config(text=f"Editing: {node_id}")
            return

canvas.bind("<Button-1>", on_click)

# Связи
for node_id, node in tree.nodes.items():
    for choice in node.choices:
        s = node_positions[node_id]
        e = node_positions[choice["next_node_id"]]

        sx, sy = (s["x1"]+s["x2"])/2, s["y2"]
        ex, ey = (e["x1"]+e["x2"])/2, e["y1"]

        canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST, width=2)
        canvas.create_text(
            (sx+ex)/2,
            (sy+ey)/2,
            text=choice["text"],
            width=150,
            fill="darkblue",
            font=("Arial", 8)
        )

window.mainloop()