import tkinter as tk

window = tk.Tk()
window.geometry("800x600")
window.title("DTV - Dialogue Editor")

my_canvas = tk.Canvas(
    window,
    width=780,
    height=580,
    bg="lightblue"
)

my_canvas.pack()

center_x = 780 / 2
center_y = 580 / 2

my_canvas.create_rectangle(
    center_x - 100,
    center_y - 50,
    center_x + 100,
    center_y + 50,
    fill="white"
)

my_canvas.create_text(
    center_x,
    center_y,
    text="Geralt",
    fill="black"
)

window.mainloop()
