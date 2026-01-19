import tkinter as tk
from client import Client
from tkinter import simpledialog

# שואל שם משתמש
root_prompt = tk.Tk()
root_prompt.withdraw()
username = simpledialog.askstring("Username", "Enter your username:")
if not username:
    username = "User"
root_prompt.destroy()

# רשת
ENTRY_IP = "127.0.0.1"
ENTRY_PORT = 9010
LISTEN_PORT = 9100
KEYS = [11, 22, 33]

# פורט יעד של משתמש אחר
target_port_input = simpledialog.askinteger("Target Port", "Enter the target port of the other user:")
if not target_port_input:
    target_port_input = 9101

class ChatGUI:
    def __init__(self, name, entry_ip, entry_port, listen_port, keys, target_port):
        self.name = name
        self.target_port = target_port

        self.client = Client(name, entry_ip, entry_port, listen_port, keys)
        self.client.on_message = self.display_message

        self.root = tk.Tk()
        self.root.title(f"Tor Chat - {name}")

        self.chat_box = tk.Text(self.root, height=15, width=50, state="disabled")
        self.chat_box.pack(padx=10, pady=10)

        self.entry = tk.Entry(self.root, width=40)
        self.entry.pack(side=tk.LEFT, padx=10)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=10)

        self.root.mainloop()

    def display_message(self, sender, message):
        self.chat_box.config(state="normal")
        self.chat_box.insert(tk.END, f"{sender}: {message}\n")
        self.chat_box.config(state="disabled")

    def send_message(self, event=None):
        msg = self.entry.get()
        if not msg:
            return
        self.entry.delete(0, tk.END)
        self.display_message(self.name, msg)
        self.client.send(msg, self.target_port)

ChatGUI(username, ENTRY_IP, ENTRY_PORT, LISTEN_PORT, KEYS, target_port_input)
