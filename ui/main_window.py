import tkinter as tk
from tkinter import ttk, filedialog
import json, os, sys
from collections import deque

# Resolve base directory — works both for plain .py and PyInstaller --onefile
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _path(rel):
    return os.path.join(BASE_DIR, rel)

# ── PALETTE ───────────────────────────────────────────────────────────────────
C = {
    "panel":       "#ffffff", "panel_fg":   "#2c2c2c",
    "section":     "#f8f8f8", "row":        "#ffffff",
    "array":       "#fafafa", "choice_idx": "#ffe0e0",
    "blood":       "#cc0000", "blood_dim":  "#990000",
    "blood_pale":  "#ff3333", "blood_faint":"#ffe0e0",
    "plum_pale":   "#ff6666", "gold":       "#cc6600",
    "gold_pale":   "#ff9933", "sky":        "#87CEEB",
    "sky_light":   "#b8e4f9", "sky_dark":   "#5ba3c9",
    "wire":        "#4a6a7a", "wire_dim":   "#6a8a9a",
    "text":        "#2c2c2c", "text_dim":   "#666666",
    "text_muted":  "#999999", "text_mono":  "#cc0000",
    "text_italic": "#444444", "border_mid": "#ff9999",
    "border_dark": "#ffcccc", "grid":       "#a8d8f0",
}

SPEAKER_TABS = {"Geralt": C["blood"], "Villager": C["blood_dim"],
                "Геральт": C["blood"], "Крестьянин": C["blood_dim"]}

CANVAS_W, CANVAS_H   = 1060, 760
NODE_W,   NODE_H     = 200, 108
LEVEL_GAP            = 190
ZOOM_MIN, ZOOM_MAX, ZOOM_STEP = 0.15, 3.0, 1.12
DATA_FILE = _path("data/demo_dialogue.json")

MONO    = ("Consolas", 9)
MONO_SM = ("Consolas", 8)
SERIF   = ("Georgia", 10, "italic")

# ── MODEL ─────────────────────────────────────────────────────────────────────
class DialogueNode:
    def __init__(self, node_id, speaker="", text="", choices=None):
        self.node_id = node_id
        self.speaker = speaker
        self.text    = text
        self.choices = choices or []

    def to_dict(self):
        return {"id": self.node_id, "speaker": self.speaker,
                "text": self.text, "choices": self.choices}


class DialogueTree:
    def __init__(self):
        self.title = "Untitled"
        self.start_node_id = None
        self.nodes = {}


def load_from_json(path):
    tree = DialogueTree()
    if not os.path.exists(path):
        return tree
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        tree.title         = data.get("title", "Untitled")
        tree.start_node_id = data.get("start_node_id")
        tree._saved_positions = data.get("positions", {})
        for nd in data.get("nodes", []):
            nid = nd.get("id") or nd.get("node_id")
            if nid:
                tree.nodes[nid] = DialogueNode(
                    nid, nd.get("speaker",""), nd.get("text",""), nd.get("choices",[]))
    except Exception as e:
        print(f"Load error: {e}")
    return tree


def _default_tree():
    t = DialogueTree()
    t.start_node_id = "node_start"
    t.nodes["node_start"] = DialogueNode(
        "node_start", "Geralt", "What do you want, villager? Speak quickly.",
        [{"text": "Help request", "next_node_id": "node_002"}])
    t.nodes["node_002"] = DialogueNode(
        "node_002", "Villager", "Something in the woods… people are disappearing.",
        [{"text": "Investigate", "next_node_id": "node_003"},
         {"text": "Walk away",   "next_node_id": "node_004"}])
    t.nodes["node_003"] = DialogueNode("node_003", "Geralt",   "I'll look into it. But it won't be cheap.")
    t.nodes["node_004"] = DialogueNode("node_004", "Villager", "Please… we have nowhere else to turn.")
    return t


# ── WINDOW ────────────────────────────────────────────────────────────────────
window = tk.Tk()
window.geometry("1400x860")
window.title("DTV — Dialogue Tree Visualizer")
window.configure(bg=C["panel"])

style = ttk.Style()
style.theme_use("clam")
for orient in ("Vertical", "Horizontal"):
    style.configure(f"{orient}.TScrollbar", background=C["panel"],
                    troughcolor=C["row"], bordercolor=C["border_mid"],
                    arrowcolor=C["blood"], relief="flat")

main_frame = tk.Frame(window, bg=C["panel"])
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame, width=CANVAS_W, height=CANVAS_H,
                   bg=C["sky"], highlightthickness=0)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# ── RIGHT PANEL (scrollable) ──────────────────────────────────────────────────
panel_outer = tk.Frame(main_frame, width=256, bg=C["panel"])
panel_outer.pack(side=tk.RIGHT, fill=tk.Y)
panel_outer.pack_propagate(False)

panel_canvas = tk.Canvas(panel_outer, bg=C["panel"], highlightthickness=0)
panel_scroll = ttk.Scrollbar(panel_outer, orient="vertical",
                              command=panel_canvas.yview, style="Vertical.TScrollbar")
panel_canvas.configure(yscrollcommand=panel_scroll.set)
panel_scroll.pack(side=tk.RIGHT, fill=tk.Y)
panel_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

panel = tk.Frame(panel_canvas, bg=C["panel"])
panel_win = panel_canvas.create_window((0, 0), window=panel, anchor="nw")
panel.bind("<Configure>", lambda e: (
    panel_canvas.configure(scrollregion=panel_canvas.bbox("all")),
    panel_canvas.itemconfig(panel_win, width=panel_canvas.winfo_width())))
panel_canvas.bind("<Configure>", lambda e: panel_canvas.itemconfig(panel_win, width=e.width))
for seq, delta in (("<MouseWheel>", None), ("<Button-4>", -1), ("<Button-5>", 1)):
    panel_canvas.bind(seq, lambda e, d=delta:
        panel_canvas.yview_scroll(d if d else int(-e.delta/120), "units"))

# ── PANEL BUILDERS ────────────────────────────────────────────────────────────
def _sep(parent=None):
    tk.Frame(parent or panel, height=1, bg=C["border_mid"]).pack(fill=tk.X)

def _section(title, parent=None):
    p = parent or panel
    hdr = tk.Frame(p, bg=C["section"])
    hdr.pack(fill=tk.X)
    _sep(hdr)
    inner = tk.Frame(hdr, bg=C["section"])
    inner.pack(fill=tk.X, padx=0)
    tk.Label(inner, text="▾ " + title.upper(), bg=C["section"], fg=C["blood"],
             font=MONO_SM).pack(side=tk.LEFT, padx=10, pady=5)
    _sep(hdr)

def _prop_row(label, widget_fn, required=False):
    row = tk.Frame(panel, bg=C["row"])
    row.pack(fill=tk.X)
    tk.Label(row, text=label + (" *" if required else ""), bg=C["row"],
             fg=C["blood"] if required else C["text_dim"],
             font=MONO_SM, width=9, anchor="w").pack(side=tk.LEFT, padx=(10,4), pady=5)
    w = widget_fn(row)
    w.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10), pady=4)
    _sep()
    return w

def _entry(parent, textvariable=None, fg=None):
    return tk.Entry(parent, bg=C["row"], fg=fg or C["text"], relief=tk.FLAT,
                    font=MONO, textvariable=textvariable,
                    insertbackground=C["text"],
                    highlightthickness=1, highlightbackground=C["border_mid"],
                    highlightcolor=C["blood"])

def _btn(parent, text, bg, cmd, full=False, side=None):
    b = tk.Button(parent, text=text, bg=bg, fg=C["blood"], relief=tk.FLAT,
                  font=MONO_SM, cursor="hand2", command=cmd,
                  highlightthickness=1, highlightbackground=C["border_mid"],
                  activebackground=C["border_mid"], activeforeground=C["blood"], pady=5)
    kw = {"fill": tk.X, "pady": (0,4)} if full else {"side": side or tk.LEFT, "fill": tk.X, "expand": True, "padx": (0,3)}
    b.pack(**kw)
    return b

# ── BREADCRUMB ────────────────────────────────────────────────────────────────
bc_frame = tk.Frame(panel, bg=C["panel"])
bc_frame.pack(fill=tk.X)
_sep(bc_frame)
bc_inner = tk.Frame(bc_frame, bg=C["panel"])
bc_inner.pack(fill=tk.X, padx=10, pady=6)
tk.Label(bc_inner, text="tree / ", bg=C["panel"], fg=C["text_dim"], font=MONO_SM).pack(side=tk.LEFT)
bc_node_lbl = tk.Label(bc_inner, text="—", bg=C["panel"], fg=C["blood"], font=MONO_SM)
bc_node_lbl.pack(side=tk.LEFT)
_sep(bc_frame)

# ── IDENTITY ──────────────────────────────────────────────────────────────────
_section("Identity")
node_id_var  = tk.StringVar(value="—")
speaker_var  = tk.StringVar()
type_var     = tk.StringVar(value="—")

id_entry = _prop_row("ID", lambda p: _entry(p, textvariable=node_id_var, fg=C["blood"]), required=True)

type_row = tk.Frame(panel, bg=C["row"]); type_row.pack(fill=tk.X)
tk.Label(type_row, text="Type", bg=C["row"], fg=C["text_dim"],
         font=MONO_SM, width=9, anchor="w").pack(side=tk.LEFT, padx=(10,4), pady=5)
tk.Label(type_row, textvariable=type_var, bg=C["row"], fg=C["blood"], font=MONO_SM).pack(side=tk.LEFT)
_sep()

speaker_entry = _prop_row("Speaker", lambda p: _entry(p, textvariable=speaker_var))

# ── DIALOGUE ──────────────────────────────────────────────────────────────────
_section("Dialogue")
text_frame = tk.Frame(panel, bg=C["row"])
text_frame.pack(fill=tk.X, padx=10, pady=(6,4))
text_entry = tk.Text(text_frame, height=5, bg=C["row"], fg=C["text_italic"],
                     insertbackground=C["text"], relief=tk.FLAT, font=SERIF,
                     wrap=tk.WORD, highlightthickness=1,
                     highlightbackground=C["border_mid"], highlightcolor=C["blood"],
                     padx=6, pady=5)
text_entry.pack(fill=tk.X)
_sep()

# ── CHOICES ───────────────────────────────────────────────────────────────────
_section("Choices")
ch_bar = tk.Frame(panel, bg=C["array"]); ch_bar.pack(fill=tk.X)
ch_inner = tk.Frame(ch_bar, bg=C["array"]); ch_inner.pack(fill=tk.X, padx=10, pady=5)
tk.Label(ch_inner, text="choices[]", bg=C["array"], fg=C["text_dim"], font=MONO_SM).pack(side=tk.LEFT)
ch_count_lbl = tk.Label(ch_inner, text="0", bg=C["border_mid"], fg=C["text_muted"], font=MONO_SM, padx=6, pady=1)
ch_count_lbl.pack(side=tk.LEFT, padx=6)
add_ch_btn = tk.Label(ch_inner, text="+ add", bg=C["blood_faint"], fg=C["blood"],
                      font=MONO_SM, padx=8, pady=1, relief=tk.FLAT, cursor="hand2",
                      highlightthickness=1, highlightbackground=C["border_mid"])
add_ch_btn.pack(side=tk.RIGHT)
_sep()
choices_frame = tk.Frame(panel, bg=C["panel"]); choices_frame.pack(fill=tk.X)
choice_rows = []

# ── METADATA ──────────────────────────────────────────────────────────────────
_section("Metadata")
pos_var       = tk.StringVar(value="—")
edges_in_var  = tk.StringVar(value="0")
edges_out_var = tk.StringVar(value="0")
for lbl, var in [("Position", pos_var), ("Edges out", edges_out_var), ("Edges in", edges_in_var)]:
    _prop_row(lbl, lambda p, v=var: tk.Label(p, textvariable=v, bg=C["row"],
              fg=C["text_mono"], font=MONO_SM, anchor="w"))

# ── VIEW ──────────────────────────────────────────────────────────────────────
_section("View")
zoom_row = tk.Frame(panel, bg=C["row"]); zoom_row.pack(fill=tk.X, padx=10, pady=6)
zoom_lbl = tk.Label(zoom_row, text="100%", bg=C["row"], fg=C["text_mono"], font=MONO_SM)
zoom_lbl.pack(side=tk.LEFT)
for sym, fn in [("⌂", lambda: reset_view()), ("−", lambda: zoom_at_center(1/ZOOM_STEP)), ("+", lambda: zoom_at_center(ZOOM_STEP))]:
    b = tk.Label(zoom_row, text=sym, bg=C["section"], fg=C["blood"], font=MONO_SM,
                 padx=8, pady=2, cursor="hand2", relief=tk.FLAT,
                 highlightthickness=1, highlightbackground=C["border_mid"])
    b.pack(side=tk.RIGHT, padx=2)
    b.bind("<Button-1>", lambda e, f=fn: f())
_sep()

# ── ACTIONS ───────────────────────────────────────────────────────────────────
_section("Actions")
act_frame = tk.Frame(panel, bg=C["panel"]); act_frame.pack(fill=tk.X, padx=10, pady=8)
_btn(act_frame, "✓  apply changes", C["blood_faint"], lambda: save_node(), full=True)
for row_items in [
    [("+  new node",  lambda: add_node()),       ("⌘F  find",     lambda: open_search())],
    [("💾 save json", lambda: save_json()),       ("📂 open json", lambda: open_json())],
    [("validate",     lambda: open_validate()),   ("undo (^Z)",    lambda: undo())],
    [("delete node",  lambda: delete_node()),],
]:
    r = tk.Frame(act_frame, bg=C["panel"]); r.pack(fill=tk.X, pady=(0,3))
    for text, cmd in row_items:
        _btn(r, text, C["blood_faint"] if "delete" in text else C["section"], cmd)

# ── STATUS ────────────────────────────────────────────────────────────────────
_sep()
sf = tk.Frame(panel, bg=C["panel"]); sf.pack(fill=tk.X)
sg = tk.Canvas(sf, width=8, height=8, bg=C["panel"], highlightthickness=0)
sg.pack(side=tk.LEFT, padx=(10,4), pady=7)
sg.create_oval(1,1,7,7, fill=C["blood"], outline="")
panel_status = tk.Label(sf, text="click a node to edit", bg=C["panel"],
                         fg=C["text_dim"], font=MONO_SM, anchor="w")
panel_status.pack(side=tk.LEFT, fill=tk.X, padx=(0,8), pady=6)
_sep()

# ── DATA ──────────────────────────────────────────────────────────────────────
os.makedirs(_path("data"), exist_ok=True)
tree = load_from_json(DATA_FILE)
if not tree.nodes:
    tree = _default_tree()

selected_node_id = None
_error_nodes: set = set()  # nids with validation errors (shown on canvas)
node_positions   = {}
drag_data        = {"node_id": None, "last_sx": 0, "last_sy": 0, "moved": False}
cam              = {"offset_x": 0.0, "offset_y": 0.0, "scale": 1.0}
pan_data         = {"active": False, "start_x": 0, "start_y": 0, "start_ox": 0.0, "start_oy": 0.0}
ctrl_drag        = {"active": False}

# ── HISTORY ───────────────────────────────────────────────────────────────────
_undo_stack, _redo_stack = [], []

def _snapshot():
    return {"start": tree.start_node_id,
            "nodes": {nid: n.to_dict() for nid, n in tree.nodes.items()},
            "positions": {nid: dict(p) for nid, p in node_positions.items()}}

def _restore(snap):
    global selected_node_id
    tree.start_node_id = snap["start"]
    tree.nodes.clear()
    for nid, d in snap["nodes"].items():
        tree.nodes[nid] = DialogueNode(d["id"], d["speaker"], d["text"], d.get("choices",[]))
    node_positions.clear()
    node_positions.update({nid: dict(p) for nid, p in snap["positions"].items()})
    (_load_node_to_panel if selected_node_id in tree.nodes else lambda _: (_clear_panel(), setattr(globals(), "selected_node_id", None)))(selected_node_id)
    draw_all()

def push_history():
    _undo_stack.append(_snapshot())
    if len(_undo_stack) > 60: _undo_stack.pop(0)
    _redo_stack.clear()

def undo(e=None):
    if not _undo_stack: panel_status.config(text="nothing to undo"); return
    _redo_stack.append(_snapshot()); _restore(_undo_stack.pop())
    panel_status.config(text="undo ✓")

def redo(e=None):
    if not _redo_stack: panel_status.config(text="nothing to redo"); return
    _undo_stack.append(_snapshot()); _restore(_redo_stack.pop())
    panel_status.config(text="redo ✓")

window.bind("<Control-z>", undo); window.bind("<Control-Z>", undo)
window.bind("<Control-y>", redo); window.bind("<Control-Y>", redo)

# ── COORD HELPERS ─────────────────────────────────────────────────────────────
def _sx(wx): return wx * cam["scale"] + cam["offset_x"]
def _sy(wy): return wy * cam["scale"] + cam["offset_y"]
def _sw(w):  return w  * cam["scale"]

def screen_to_world(sx, sy):
    return (sx - cam["offset_x"]) / cam["scale"], (sy - cam["offset_y"]) / cam["scale"]

def world_to_screen(wx, wy):
    return wx * cam["scale"] + cam["offset_x"], wy * cam["scale"] + cam["offset_y"]

# ── LAYOUT ────────────────────────────────────────────────────────────────────
def compute_layout():
    if not tree.start_node_id or tree.start_node_id not in tree.nodes:
        return {}, {}
    levels, order = {tree.start_node_id: 0}, {}
    q = deque([tree.start_node_id])
    while q:
        cur = q.popleft()
        lv  = levels[cur]
        order.setdefault(lv, []).append(cur)
        for c in tree.nodes.get(cur, DialogueNode("")).choices:
            nxt = c["next_node_id"]
            if nxt not in levels and nxt in tree.nodes:
                levels[nxt] = lv + 1; q.append(nxt)
    for nid in tree.nodes:
        if nid not in levels:
            ml = max(order.keys(), default=0) + 1
            levels[nid] = ml; order.setdefault(ml, []).append(nid)
    return levels, order

def init_positions():
    node_positions.clear()
    saved = getattr(tree, "_saved_positions", {})
    cw = canvas.winfo_width() or CANVAS_W
    _, order = compute_layout()
    for level, nodes in order.items():
        n   = len(nodes)
        gap = (cw - n * NODE_W) / (n + 1)
        for i, nid in enumerate(nodes):
            if nid in saved:
                node_positions[nid] = dict(saved[nid])
            else:
                x1 = gap + i * (NODE_W + gap)
                y1 = 50 + level * LEVEL_GAP
                node_positions[nid] = {"x1": x1, "y1": y1, "x2": x1+NODE_W, "y2": y1+NODE_H}

# ── DRAW ──────────────────────────────────────────────────────────────────────
def draw_all():
    canvas.delete("all")
    # grid
    gw = 32 * cam["scale"]
    cw, ch = canvas.winfo_width() or CANVAS_W, canvas.winfo_height() or CANVAS_H
    ox, oy = cam["offset_x"] % gw, cam["offset_y"] % gw
    x = ox
    while x < cw: canvas.create_line(x, 0, x, ch, fill=C["grid"], tags=("grid",)); x += gw
    y = oy
    while y < ch: canvas.create_line(0, y, cw, y, fill=C["grid"], tags=("grid",)); y += gw
    _draw_edges(); _draw_nodes()

def _draw_nodes():
    sc = cam["scale"]
    for nid, pos in node_positions.items():
        node = tree.nodes.get(nid)
        if not node: continue
        x1, y1, x2, y2 = _sx(pos["x1"]), _sy(pos["y1"]), _sx(pos["x2"]), _sy(pos["y2"])
        tag    = f"node_{nid}"
        tab_h  = _sw(22)
        tab_col = C["blood_dim"] if nid == tree.start_node_id else SPEAKER_TABS.get(node.speaker, C["blood"])
        is_sel = nid == selected_node_id
        is_start = nid == tree.start_node_id

        if nid in _error_nodes:
            canvas.create_rectangle(x1-4, y1-4, x2+4, y2+4, outline="#ff4400",
                                     width=2, dash=(3,2), tags=(tag,))
        if is_sel:
            canvas.create_rectangle(x1-3, y1-3, x2+3, y2+3, outline=C["blood"], width=2, tags=(tag,))
        if is_start:
            canvas.create_rectangle(x1-6, y1-6, x2+6, y2+6, outline=C["blood"],
                                     width=1, dash=(4,3), tags=(tag,))

        canvas.create_rectangle(x1, y1, x2, y2, outline=C["wire"], fill=C["sky_light"],
                                 width=max(1, int(1.5*sc)), tags=(tag,))
        ins = max(2, _sw(2))
        canvas.create_rectangle(x1+ins, y1+ins, x2-ins, y2-ins, outline=C["wire_dim"],
                                 fill="", width=max(1, int(0.5*sc)), tags=(tag,))
        canvas.create_rectangle(x1, y1, x2, y1+tab_h, outline="", fill=tab_col, tags=(tag,))

        fs_id, fs_spk, fs_txt = (max(a, min(b, int(c*sc))) for a, b, c in [(7,10,8),(8,14,10),(7,11,9)])
        cx = (x1+x2)/2

        canvas.create_text(cx, y1+tab_h*0.5, text=nid, font=("Consolas", fs_id),
                            fill="#ffffff", tags=(tag,))
        if is_start:
            canvas.create_text(x2 - _sw(8), y1 + tab_h*0.5, text="START",
                                font=("Consolas", fs_id-1), fill=C["blood_pale"],
                                anchor="e", tags=(tag,))

        sy_sep = y1 + tab_h
        canvas.create_line(x1, sy_sep, x2, sy_sep, fill=C["wire"],
                            width=max(1, int(0.5*sc)), tags=(tag,))
        canvas.create_text(x1 + _sw(10), sy_sep + _sw(14), text=node.speaker,
                            anchor="w", font=("Georgia", fs_spk, "bold"),
                            fill=C["blood_dim"], tags=(tag,))
        # Centre text in the body zone above the footer (footer = 20px at bottom)
        body_top = sy_sep + _sw(18)
        body_bot = (y2 - _sw(20)) if node.choices else y2
        body_cy  = (body_top + body_bot) / 2
        canvas.create_text(cx, body_cy, text=node.text,
                            width=_sw(176), anchor="center",
                            font=("Georgia", fs_txt, "italic"),
                            fill=C["text"], tags=(tag,))

        if node.choices:
            # Footer strip — fully inside card: separator at y2-20, text centred in remaining 20px
            fy = y2 - _sw(20)
            canvas.create_line(x1+_sw(4), fy, x2-_sw(4), fy,
                                fill=C["sky_dark"], width=1, tags=(tag,))
            # Build label, then hard-truncate so it never exceeds card width
            ch_text = "  ·  ".join(c["text"] for c in node.choices[:2])
            if len(node.choices) > 2: ch_text += f"  +{len(node.choices)-2}"
            max_chars = max(8, int(_sw(NODE_W - 16) / max(1, int(7*sc))))
            if len(ch_text) > max_chars: ch_text = ch_text[:max_chars-1] + "…"
            canvas.create_text(cx, fy + _sw(10), text=ch_text,
                                font=("Consolas", max(6, int(7*sc))),
                                fill=C["gold_pale"], anchor="center",
                                width=x2-x1-_sw(10),   # tkinter clips to this width
                                tags=(tag,))

        for ev, fn in [("<Button-1>", _on_node_press), ("<B1-Motion>", _on_node_drag),
                       ("<ButtonRelease-1>", _on_node_release), ("<Double-Button-1>", _on_node_double_click)]:
            canvas.tag_bind(tag, ev, fn)

def _draw_edges():
    sc = cam["scale"]
    for nid, node in tree.nodes.items():
        if nid not in node_positions: continue
        s = node_positions[nid]
        sx_m, sy_b = _sx((s["x1"]+s["x2"])/2), _sy(s["y2"])
        for ch in node.choices:
            nxt = ch["next_node_id"]
            if nxt not in node_positions: continue
            e = node_positions[nxt]
            ex_m, ey_t = _sx((e["x1"]+e["x2"])/2), _sy(e["y1"])
            my  = (sy_b + ey_t) / 2
            col = C["blood"] if nid == tree.start_node_id else C["blood_dim"]
            canvas.create_line(sx_m, sy_b, sx_m, my, ex_m, my, ex_m, ey_t,
                                arrow=tk.LAST, fill=col, width=max(1, int(1.5*sc)),
                                smooth=True, tags=("edge",))
            canvas.create_text((sx_m+ex_m)/2, (sy_b+ey_t)/2, text=ch["text"],
                                width=_sw(130), fill=C["gold"],
                                font=("Consolas", max(6, min(9, int(7*sc)))), tags=("edge",))

# ── ZOOM / PAN ────────────────────────────────────────────────────────────────
def _apply_zoom(factor, px, py):
    old = cam["scale"]
    new = max(ZOOM_MIN, min(ZOOM_MAX, old * factor))
    if new == old: return
    wx = (px - cam["offset_x"]) / old
    wy = (py - cam["offset_y"]) / old
    cam.update(scale=new,
               offset_x=px - wx*new,
               offset_y=py - wy*new)
    zoom_lbl.config(text=f"{int(new*100)}%")
    draw_all()

def zoom_at_center(f):
    _apply_zoom(f, (canvas.winfo_width() or CANVAS_W)/2, (canvas.winfo_height() or CANVAS_H)/2)

def reset_view():
    cam.update(scale=1.0, offset_x=0.0, offset_y=0.0)
    zoom_lbl.config(text="100%"); draw_all()

canvas.bind("<MouseWheel>", lambda e: _apply_zoom(ZOOM_STEP if e.delta > 0 else 1/ZOOM_STEP, e.x, e.y))
canvas.bind("<Button-4>",   lambda e: _apply_zoom(ZOOM_STEP,   e.x, e.y))
canvas.bind("<Button-5>",   lambda e: _apply_zoom(1/ZOOM_STEP, e.x, e.y))

def _on_pan_start(e):
    pan_data.update(active=True, start_x=e.x, start_y=e.y,
                    start_ox=cam["offset_x"], start_oy=cam["offset_y"])
    canvas.config(cursor="fleur")

def _on_pan_move(e):
    if not pan_data["active"]: return
    cam["offset_x"] = pan_data["start_ox"] + e.x - pan_data["start_x"]
    cam["offset_y"] = pan_data["start_oy"] + e.y - pan_data["start_y"]
    draw_all()

def _on_pan_end(e): pan_data["active"] = False; canvas.config(cursor="")

canvas.bind("<Button-2>",        _on_pan_start)
canvas.bind("<B2-Motion>",       _on_pan_move)
canvas.bind("<ButtonRelease-2>", _on_pan_end)
canvas.bind("<Control-Button-1>",        lambda e: (ctrl_drag.update(active=True),  _on_pan_start(e)))
canvas.bind("<Control-B1-Motion>",       lambda e: ctrl_drag["active"] and _on_pan_move(e))
canvas.bind("<Control-ButtonRelease-1>", lambda e: (ctrl_drag.update(active=False), _on_pan_end(e)))

# ── NODE INTERACTION ──────────────────────────────────────────────────────────
def _get_node_at(sx, sy):
    wx, wy = screen_to_world(sx, sy)
    for nid, p in node_positions.items():
        if p["x1"] <= wx <= p["x2"] and p["y1"] <= wy <= p["y2"]:
            return nid
    return None

def _on_node_press(event):
    global selected_node_id
    if ctrl_drag["active"]: return
    nid = _get_node_at(event.x, event.y)
    if not nid: return
    drag_data.update(node_id=nid, moved=False, last_sx=event.x, last_sy=event.y)
    selected_node_id = nid; _load_node_to_panel(nid); draw_all()

def _on_node_drag(event):
    nid = drag_data["node_id"]
    if not nid or ctrl_drag["active"]: return
    if not drag_data["moved"]: push_history(); drag_data["moved"] = True
    dx_w = (event.x - drag_data["last_sx"]) / cam["scale"]
    dy_w = (event.y - drag_data["last_sy"]) / cam["scale"]
    drag_data.update(last_sx=event.x, last_sy=event.y)
    p = node_positions[nid]
    node_positions[nid] = {"x1": p["x1"]+dx_w, "y1": p["y1"]+dy_w,
                            "x2": p["x2"]+dx_w, "y2": p["y2"]+dy_w}
    canvas.move(f"node_{nid}", event.x - drag_data["last_sx"] + dx_w*cam["scale"],
                               event.y - drag_data["last_sy"] + dy_w*cam["scale"])
    canvas.delete("edge"); _draw_edges()

def _on_node_release(e):
    if drag_data.get("moved"): draw_all()
    drag_data["node_id"] = None

def _on_node_double_click(event):
    nid = _get_node_at(event.x, event.y)
    if not nid: return
    pos = node_positions[nid]
    x1, y1 = world_to_screen(pos["x1"], pos["y1"])
    x2, _  = world_to_screen(pos["x2"], pos["y2"])
    evar   = tk.StringVar(value=nid)
    inline = _entry(canvas, textvariable=evar, fg=C["blood"])
    canvas.create_window((x1+x2)//2, y1 + _sw(11), window=inline,
                          width=_sw(180), tags=("inline_entry",))

    def _confirm(e=None):
        global selected_node_id
        new_id = evar.get().strip()
        canvas.delete("inline_entry")
        if new_id and new_id != nid:
            selected_node_id = rename_node_id(nid, new_id)
            node_id_var.set(selected_node_id)
        draw_all()

    inline.bind("<Return>", _confirm)
    inline.bind("<Escape>", lambda e: (canvas.delete("inline_entry"), draw_all()))
    inline.focus_set()

canvas.bind("<Double-Button-1>", _on_node_double_click)

# ── CONTEXT MENU ──────────────────────────────────────────────────────────────
def _show_context_menu(event):
    global selected_node_id
    nid = _get_node_at(event.x, event.y)
    wx, wy = screen_to_world(event.x, event.y)
    m = tk.Menu(window, tearoff=0, bg=C["panel"], fg=C["text"],
                activebackground=C["blood"], activeforeground=C["panel"],
                relief=tk.FLAT, borderwidth=1)
    if nid:
        selected_node_id = nid; _load_node_to_panel(nid); draw_all()
        m.add_command(label=f"  [{nid}]", state=tk.DISABLED, font=MONO_SM)
        m.add_separator()
        m.add_command(label="✏  Rename (inline)", command=lambda: _on_node_double_click(event))
        m.add_command(label="⧉  Duplicate",       command=lambda: _duplicate_node(nid))
        m.add_separator()
        if nid != tree.start_node_id:
            m.add_command(label="★  Set as Start", command=lambda: _set_as_start(nid))
        m.add_command(label="✕  Delete Node", command=delete_node)
        m.add_separator()
        m.add_command(label="⌂  Jump to Start", command=lambda: jump_to_node(tree.start_node_id))
    else:
        m.add_command(label="＋  Add Node here", command=lambda: _add_node_at(wx, wy))
        m.add_separator()
        m.add_command(label="🔎  Validate",    command=open_validate)
        m.add_command(label="⌘F  Find Node",  command=open_search)
    m.tk_popup(event.x_root, event.y_root)

canvas.bind("<Button-3>", _show_context_menu)

def _duplicate_node(nid):
    src = tree.nodes[nid]
    new_id = nid + "_copy"
    while new_id in tree.nodes: new_id += "_copy"
    push_history()
    tree.nodes[new_id] = DialogueNode(new_id, src.speaker, src.text, [dict(c) for c in src.choices])
    pos = node_positions[nid]
    node_positions[new_id] = {k: v+40 for k, v in pos.items()}
    panel_status.config(text=f"duplicated → {new_id}"); draw_all()

def _set_as_start(nid):
    push_history(); tree.start_node_id = nid
    panel_status.config(text=f"start node → {nid} ✓"); draw_all()

def _add_node_at(wx, wy):
    new_id = _gen_id(); push_history()
    tree.nodes[new_id] = DialogueNode(new_id, "Speaker", "Dialogue text")
    node_positions[new_id] = {"x1": wx-NODE_W/2, "y1": wy-NODE_H/2,
                               "x2": wx+NODE_W/2, "y2": wy+NODE_H/2}
    panel_status.config(text=f"created: {new_id}"); draw_all()

# ── CHOICES PANEL ─────────────────────────────────────────────────────────────
def _update_choice_count(): ch_count_lbl.config(text=str(len(choice_rows)))

def _clear_choice_rows():
    for r in choice_rows: r["frame"].destroy()
    choice_rows.clear(); _update_choice_count()

def _build_choice_row(idx, choice_text="", next_id=""):
    frame = tk.Frame(choices_frame, bg=C["array"]); frame.pack(fill=tk.X)
    tk.Label(frame, text=str(idx), bg=C["choice_idx"], fg=C["blood"],
             font=MONO_SM, width=3).pack(side=tk.LEFT, fill=tk.Y)
    body = tk.Frame(frame, bg=C["array"]); body.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=4)

    text_var, next_var = tk.StringVar(value=choice_text), tk.StringVar(value=next_id)
    _entry(body, textvariable=text_var, fg=C["text_italic"]).pack(fill=tk.X, pady=(0,3))

    n_row = tk.Frame(body, bg=C["array"]); n_row.pack(fill=tk.X)
    tk.Label(n_row, text="→", bg=C["array"], fg=C["blood"], font=MONO_SM).pack(side=tk.LEFT)
    _entry(n_row, textvariable=next_var, fg=C["text_mono"]).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4,0))

    row_data = {}
    del_btn = tk.Label(frame, text="×", bg=C["array"], fg=C["blood"], font=("Consolas",11), cursor="hand2", padx=6)
    del_btn.pack(side=tk.RIGHT, fill=tk.Y)
    del_btn.bind("<Button-1>", lambda e: (frame.destroy(), choice_rows.remove(row_data), _update_choice_count()))
    _sep(choices_frame)
    row_data.update(frame=frame, text_var=text_var, next_var=next_var)
    choice_rows.append(row_data); _update_choice_count()

def _collect_choices():
    return [{"text": r["text_var"].get().strip(), "next_node_id": r["next_var"].get().strip()}
            for r in choice_rows if r["text_var"].get().strip() and r["next_var"].get().strip()]

add_ch_btn.bind("<Button-1>", lambda e: (
    _build_choice_row(len(choice_rows)) if selected_node_id
    else panel_status.config(text="select a node first")))

# ── PANEL LOAD / CLEAR ────────────────────────────────────────────────────────
def _clear_panel():
    node_id_var.set("—"); speaker_var.set("")
    text_entry.delete("1.0", tk.END); type_var.set("—")
    pos_var.set("—"); edges_in_var.set("0"); edges_out_var.set("0")
    bc_node_lbl.config(text="—"); _clear_choice_rows()

def _load_node_to_panel(nid):
    node = tree.nodes[nid]
    node_id_var.set(nid); speaker_var.set(node.speaker)
    text_entry.delete("1.0", tk.END); text_entry.insert("1.0", node.text)
    type_var.set("START NODE" if nid == tree.start_node_id else "dialogue fragment")
    pos = node_positions.get(nid, {})
    pos_var.set(f"{int(pos['x1'])}, {int(pos['y1'])}" if pos else "—")
    edges_out_var.set(str(len(node.choices)))
    edges_in_var.set(str(sum(1 for n in tree.nodes.values() for c in n.choices if c["next_node_id"] == nid)))
    bc_node_lbl.config(text=nid); panel_status.config(text=f"editing · {nid}")
    _clear_choice_rows()
    for i, c in enumerate(node.choices): _build_choice_row(i, c["text"], c["next_node_id"])

# ── RENAME / ACTIONS ──────────────────────────────────────────────────────────
def rename_node_id(old_id, new_id):
    if not new_id or new_id == old_id: return old_id
    if new_id in tree.nodes: panel_status.config(text=f"ID '{new_id}' exists!"); return old_id
    push_history()
    node = tree.nodes.pop(old_id)
    node.node_id = new_id; tree.nodes[new_id] = node
    node_positions[new_id] = node_positions.pop(old_id, {})
    if tree.start_node_id == old_id: tree.start_node_id = new_id
    for n in tree.nodes.values():
        for c in n.choices:
            if c["next_node_id"] == old_id: c["next_node_id"] = new_id
    panel_status.config(text=f"renamed {old_id} → {new_id} ✓"); return new_id

def _gen_id():
    i = len(tree.nodes) + 1
    nid = f"node_{i:03d}"
    while nid in tree.nodes: i += 1; nid = f"node_{i:03d}"
    return nid

def add_node():
    push_history(); new_id = _gen_id()
    tree.nodes[new_id] = DialogueNode(new_id, "Speaker", "Dialogue text")
    cx, cy = screen_to_world((canvas.winfo_width() or CANVAS_W)/2, (canvas.winfo_height() or CANVAS_H)/2)
    node_positions[new_id] = {"x1": cx-NODE_W/2, "y1": cy-NODE_H/2, "x2": cx+NODE_W/2, "y2": cy+NODE_H/2}
    panel_status.config(text=f"created: {new_id}"); draw_all()

def save_node():
    global selected_node_id
    if not selected_node_id: panel_status.config(text="no node selected"); return
    push_history()
    new_id = node_id_var.get().strip()
    if new_id and new_id != selected_node_id:
        selected_node_id = rename_node_id(selected_node_id, new_id)
    node = tree.nodes[selected_node_id]
    node.speaker = speaker_var.get().strip()
    node.text    = text_entry.get("1.0", tk.END).strip()
    node.choices = _collect_choices()
    _load_node_to_panel(selected_node_id)
    panel_status.config(text=f"applied · {selected_node_id} ✓"); draw_all()

def delete_node():
    global selected_node_id
    if not selected_node_id: panel_status.config(text="no node selected"); return
    if selected_node_id == tree.start_node_id: panel_status.config(text="cannot delete start node"); return
    push_history()
    del tree.nodes[selected_node_id]
    node_positions.pop(selected_node_id, None)
    for n in tree.nodes.values():
        n.choices = [c for c in n.choices if c["next_node_id"] != selected_node_id]
    selected_node_id = None; _clear_panel()
    panel_status.config(text="deleted ✓"); draw_all()

def save_json():
    path = filedialog.asksaveasfilename(
        defaultextension=".json", filetypes=[("JSON files","*.json"),("All","*")],
        initialfile=DATA_FILE)
    if not path: return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"title": tree.title, "start_node_id": tree.start_node_id,
                   "positions": {nid: dict(p) for nid, p in node_positions.items()},
                   "nodes": [n.to_dict() for n in tree.nodes.values()]}, f, indent=4, ensure_ascii=False)
    panel_status.config(text=f"saved → {os.path.basename(path)} ✓")

def open_json():
    global tree, selected_node_id
    path = filedialog.askopenfilename(filetypes=[("JSON files","*.json"),("All","*")])
    if not path: return
    loaded = load_from_json(path)
    if not loaded.nodes: panel_status.config(text="empty or invalid file"); return
    push_history()
    tree = loaded; selected_node_id = None
    _clear_panel(); init_positions(); draw_all()
    panel_status.config(text=f"opened ← {os.path.basename(path)} ✓")

def jump_to_node(nid):
    global selected_node_id
    if nid not in node_positions: return
    pos = node_positions[nid]
    cx, cy = (pos["x1"]+pos["x2"])/2, (pos["y1"]+pos["y2"])/2
    cw, ch = canvas.winfo_width() or CANVAS_W, canvas.winfo_height() or CANVAS_H
    cam["offset_x"] = cw/2 - cx*cam["scale"]
    cam["offset_y"] = ch/2 - cy*cam["scale"]
    selected_node_id = nid; _load_node_to_panel(nid); draw_all()

# ── VALIDATE ──────────────────────────────────────────────────────────────────
def run_validation():
    all_ids = set(tree.nodes.keys())
    broken      = [f"  [{nid}] → '{c['next_node_id']}'"
                   for nid, node in tree.nodes.items()
                   for c in node.choices if c["next_node_id"] not in all_ids]
    visited = set()
    q = deque([tree.start_node_id]) if tree.start_node_id else deque()
    while q:
        cur = q.popleft()
        if cur in visited or cur not in tree.nodes: continue
        visited.add(cur)
        for c in tree.nodes[cur].choices: q.append(c["next_node_id"])
    unreachable = [f"  [{nid}]" for nid in all_ids if nid not in visited]
    dead_ends   = [f"  [{nid}]  {tree.nodes[nid].text[:40]}…" for nid in all_ids if not tree.nodes[nid].choices]
    return {"broken": broken, "unreachable": unreachable, "dead_ends": dead_ends}

def open_validate():
    global _error_nodes
    issues = run_validation()
    total  = sum(len(v) for v in issues.values())
    _error_nodes = {s.split(']')[0].strip('[').strip() for s in issues['broken'] + issues['unreachable']}
    draw_all()
    win    = tk.Toplevel(window); win.title("Validation Report")
    win.geometry("460x480"); win.configure(bg=C["panel"]); win.resizable(False, True)
    tk.Label(win, text="✓ No issues found!" if total==0 else f"⚠ {total} issue(s) found",
             bg=C["panel"], fg=C["blood"] if total==0 else C["blood_pale"],
             font=("Consolas",11)).pack(pady=(14,6))
    fr = tk.Frame(win, bg=C["panel"]); fr.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,8))
    sb  = ttk.Scrollbar(fr, style="Vertical.TScrollbar"); sb.pack(side=tk.RIGHT, fill=tk.Y)
    txt = tk.Text(fr, bg=C["row"], fg=C["text"], relief=tk.FLAT,
                   font=("Consolas",9), yscrollcommand=sb.set, wrap=tk.WORD, borderwidth=0)
    txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); sb.config(command=txt.yview)
    txt.tag_config("section", foreground=C["blood"], font=("Consolas",9))
    txt.tag_config("ok",  foreground=C["blood"]); txt.tag_config("err", foreground=C["blood_pale"])
    for key, title in [("broken","🔗 Broken links"),("unreachable","🚫 Unreachable"),("dead_ends","⛔ Dead ends")]:
        txt.insert(tk.END, f"\n{title}\n", "section")
        for line in (issues[key] or ["  — none"]): txt.insert(tk.END, line+"\n", "err" if issues[key] else "ok")
    txt.config(state=tk.DISABLED)
    btn_row = tk.Frame(win, bg=C["panel"]); btn_row.pack(fill=tk.X, padx=12, pady=(0,12))
    first_err = None
    if issues["broken"]:    first_err = issues["broken"][0].split("]")[0].strip("[ ")
    elif issues["unreachable"]: first_err = issues["unreachable"][0].strip("[ ]")
    if first_err:
        tk.Button(btn_row, text="→ Jump to first error", bg=C["blood_faint"], fg=C["blood"],
                  relief=tk.FLAT, font=("Consolas",9),
                  command=lambda: (jump_to_node(first_err), win.destroy())
                  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,4))
    def _clear_errors():
        global _error_nodes; _error_nodes = set(); draw_all(); win.destroy()
    tk.Button(btn_row, text="Clear highlights", bg=C["section"], fg=C["blood"],
              relief=tk.FLAT, font=("Consolas",9), command=_clear_errors
              ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,4))
    tk.Button(btn_row, text="Close", bg=C["section"], fg=C["blood"],
              relief=tk.FLAT, font=("Consolas",9), command=win.destroy
              ).pack(side=tk.LEFT, expand=True, fill=tk.X)
    win.bind("<Escape>", lambda e: win.destroy())

# ── SEARCH ────────────────────────────────────────────────────────────────────
_search_win = None

def open_search():
    global _search_win
    if _search_win and tk.Toplevel.winfo_exists(_search_win):
        _search_win.lift(); _search_win.focus_force(); return
    _search_win = win = tk.Toplevel(window)
    win.title("Find Node"); win.geometry("380x400"); win.configure(bg=C["panel"])
    q_var = tk.StringVar()
    q_entry = _entry(win, textvariable=q_var)
    q_entry.pack(fill=tk.X, padx=10, pady=10, ipady=5); q_entry.focus_set()
    lf = tk.Frame(win, bg=C["panel"]); lf.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
    sb  = ttk.Scrollbar(lf, style="Vertical.TScrollbar"); sb.pack(side=tk.RIGHT, fill=tk.Y)
    lb  = tk.Listbox(lf, bg=C["row"], fg=C["text"], selectbackground=C["blood"],
                      selectforeground=C["panel"], relief=tk.FLAT, font=("Consolas",9),
                      yscrollcommand=sb.set, activestyle="none", borderwidth=0)
    lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); sb.config(command=lb.yview)
    tk.Label(win, text="↵ jump  ·  Esc close", bg=C["panel"], fg=C["text_dim"],
             font=("Consolas",7)).pack(pady=(0,6))
    _ids = []
    def _search(*_):
        q = q_var.get().strip().lower(); lb.delete(0, tk.END); _ids.clear()
        for nid, node in tree.nodes.items():
            if q in nid.lower() or q in node.speaker.lower() or q in node.text.lower():
                lb.insert(tk.END, f"[{nid}]  {node.speaker}: {node.text[:42]}{'…' if len(node.text)>42 else ''}")
                _ids.append(nid)
        if not _ids: lb.insert(tk.END, "  no results")
    def _jump(e=None):
        sel = lb.curselection()
        if sel and sel[0] < len(_ids): jump_to_node(_ids[sel[0]]); win.focus_force()
    q_var.trace_add("write", _search)
    lb.bind("<Double-Button-1>", _jump); lb.bind("<Return>", _jump)
    q_entry.bind("<Return>", lambda e: (lb.selection_set(0) if lb.size() > 0 else None, _jump()))
    win.bind("<Escape>", lambda e: win.destroy()); _search()

window.bind("<Control-f>", lambda e: open_search()); window.bind("<Control-F>", lambda e: open_search())

# ── START ─────────────────────────────────────────────────────────────────────
init_positions()
draw_all()
window.mainloop()