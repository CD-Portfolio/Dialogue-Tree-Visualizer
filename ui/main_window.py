import tkinter as tk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

tree = load_dialogue_from_json("data/example_dialogue.json")

node_positions = {}

# Рисуем узлы
for i, (node_id, node) in enumerate(tree.nodes.items()):

    offset_y = i * 180

    x1, y1 = 50, 50 + offset_y
    x2, y2 = 300, 150 + offset_y

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
        end_node = node_positions[choice["next_node_id"]]

        # нижний центр первого узла
        start_x = (start_node["x1"] + start_node["x2"]) / 2
        start_y = start_node["y2"]

        # верхний центр второго узла
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