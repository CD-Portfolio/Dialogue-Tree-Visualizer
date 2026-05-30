import tkinter as tk
import sys
import os
from collections import deque

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from core.dialogue_tree import load_dialogue_from_json

window = tk.Tk()
window.geometry("1400x800")
window.title("DTV - Dialogue Editor")

my_canvas = tk.Canvas(
    window,
    width=1380,
    height=780,
    bg="lightblue"
)

my_canvas.pack()

tree = load_dialogue_from_json(
    "data/example_dialogue.json"
)

# BFS вычисление уровней

queue = deque([tree.start_node_id])

levels = {
    tree.start_node_id: 0
}

while queue:

    current_id = queue.popleft()
    current_node = tree.nodes[current_id]

    for choice in current_node.choices:

        next_id = choice["next_node_id"]

        if next_id not in levels:

            levels[next_id] = levels[current_id] + 1
            queue.append(next_id)

print(levels)

# Узлы по уровням

nodes_per_level = {}

for node_id, level in levels.items():

    if level not in nodes_per_level:
        nodes_per_level[level] = []

    nodes_per_level[level].append(node_id)

print(nodes_per_level)

# Настройки

canvas_width = 1380
node_width = 250
node_height = 100

node_positions = {}

# Рисуем узлы

for node_id, node in tree.nodes.items():

    level = levels[node_id]

    siblings = nodes_per_level[level]
    position = siblings.index(node_id)
    count = len(siblings)

    gap = (canvas_width - count * node_width) / (count + 1)

    x1 = gap + position * (node_width + gap)
    y1 = 50 + level * 180

    x2 = x1 + node_width
    y2 = y1 + node_height

    my_canvas.create_rectangle(
        x1,
        y1,
        x2,
        y2,
        outline="black",
        fill="white"
    )

    text_x = (x1 + x2) / 2
    text_y = (y1 + y2) / 2

    my_canvas.create_text(
        text_x,
        text_y,
        text=node.text,
        width=220,
        anchor="center"
    )

    node_positions[node_id] = {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "center_x": text_x,
        "center_y": text_y
    }

# Рисуем связи

for node_id, node in tree.nodes.items():

    for choice in node.choices:

        start_node = node_positions[node_id]
        end_node = node_positions[
            choice["next_node_id"]
        ]

        start_x = (start_node["x1"] + start_node["x2"]) / 2
        start_y = start_node["y2"]

        end_x = (end_node["x1"] + end_node["x2"]) / 2
        end_y = end_node["y1"]

        my_canvas.create_line(
            start_x,
            start_y,
            end_x,
            end_y,
            arrow=tk.LAST,
            width=2
        )

window.mainloop()