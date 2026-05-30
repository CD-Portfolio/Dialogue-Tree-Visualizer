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

for i, (node_id, node) in enumerate(tree.nodes.items()):

    offset_x = i * 300

    x1, y1 = 50 + offset_x, 50
    x2, y2 = 300 + offset_x, 150

    my_canvas.create_rectangle(
        x1, y1,
        x2, y2,
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

    node_positions[node_id] = (text_x, text_y)

for node_id, node in tree.nodes.items():
    for choice in node.choices:

        start_x, start_y = node_positions[node_id]

        end_x, end_y = node_positions[choice["next_node_id"]]

        my_canvas.create_line(
            start_x,
            start_y,
            end_x,
            end_y,
            arrow=tk.LAST,
            width=2
        )

window.mainloop()