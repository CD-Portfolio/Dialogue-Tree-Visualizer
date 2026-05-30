import tkinter as tk
window = tk.Tk()
window.geometry("800x600")
window.title("DTV - Dialogue Editor")
my_canvas = tk.Canvas(window, width=780, height=580, bg="lightblue")
my_canvas.pack()
my_canvas.create_rectangle(290, 240, 490, 340, fill="white")
my_canvas.create_text(390, 290, text="Geralt", fill="black")
window.mainloop()