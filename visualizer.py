import tkinter as tk

class Visualizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tor Network Visualization")

        self.canvas = tk.Canvas(self.root, width=600, height=200, bg="white")
        self.canvas.pack()

        self.nodes = {}
        self._create_node("Node-1", 100)
        self._create_node("Node-2", 300)
        self._create_node("Node-3", 500)

    def _create_node(self, name, x):
        y = 100
        circle = self.canvas.create_oval(
            x-30, y-30, x+30, y+30, fill="gray"
        )
        self.canvas.create_text(x, y+50, text=name)
        self.nodes[name] = circle

    def flash(self, node_name):
        circle = self.nodes[node_name]
        self.canvas.itemconfig(circle, fill="green")
        self.root.after(
            300,
            lambda: self.canvas.itemconfig(circle, fill="gray")
        )

    def start(self):
        self.root.mainloop()
