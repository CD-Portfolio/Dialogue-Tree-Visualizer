import tkinter as tk
import sys
import os
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.dialogue_tree import load_dialogue_from_json

# Константы
CANVAS_WIDTH, CANVAS_HEIGHT = 1380, 780
NODE_WIDTH, NODE_HEIGHT = 250, 100
LEVEL_SPACING = 180

# Окно
window = tk.Tk()
window.geometry("1400x800")
window.title("DTV - Dialogue Editor")

canvas = tk.Canvas(window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="lightblue")
canvas.pack()

# Загрузка данных
tree = load_dialogue_from_json("data/example_dialogue.json")

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

# Рисуем узлы
node_positions = {}
for node_id, node in tree.nodes.items():
    level = levels[node_id]
    siblings = nodes_per_level[level]
    position = siblings.index(node_id)
    count = len(siblings)

    gap = (CANVAS_WIDTH - count * NODE_WIDTH) / (count + 1)
    x1 = gap + position * (NODE_WIDTH + gap)
    y1 = 50 + level * LEVEL_SPACING
    x2, y2 = x1 + NODE_WIDTH, y1 + NODE_HEIGHT

    canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white", width=2)
    
    # Имя персонажа сверху
    canvas.create_text((x1+x2)/2, y1+20, text=node.speaker,
                      font=("Arial", 9, "bold"), fill="darkred")
    
    # Разделитель
    canvas.create_line(x1+10, y1+35, x2-10, y1+35, fill="gray")
    
    # Текст реплики снизу
    canvas.create_text((x1+x2)/2, y1+65, text=node.text,
                      width=220, font=("Arial", 8), fill="black")

    node_positions[node_id] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}

# Рисуем связи
for node_id, node in tree.nodes.items():
    for choice in node.choices:
        s = node_positions[node_id]
        e = node_positions[choice["next_node_id"]]

        sx, sy = (s["x1"]+s["x2"])/2, s["y2"]
        ex, ey = (e["x1"]+e["x2"])/2, e["y1"]

        canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST, width=2)
        canvas.create_text((sx+ex)/2, (sy+ey)/2, text=choice["text"],
                          width=150, fill="darkblue", font=("Arial", 8))

window.mainloop()