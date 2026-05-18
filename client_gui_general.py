import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import random
from server_gui import Client

ENTRY_IP = "127.0.0.1"
ENTRY_PORT = 9010

class ChatGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        username = simpledialog.askstring("Username", "Enter username:", parent=self.root)
        if not username:
            messagebox.showerror("Error", "Username is required!")
            self.root.destroy()
            return

        self.root.deiconify()
        self.root.title(f"Onion Chat - {username}")
        self.root.geometry("500x600")
        self.root.configure(bg="#1e1e1e")

        listen_port = random.randint(10000, 50000)

        self.client = Client(
            name=username,
            server_host=ENTRY_IP,
            server_port=ENTRY_PORT,
            listen_port=listen_port,
            client_ip="127.0.0.1",
            keys=[33, 22, 11]
        )
        self.client.on_message = self.display_message
        self.client.start()

        self.chat_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, bg="#2b2b2b", fg="white", font=("Arial", 12)
        )
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state="disabled")

        bottom_frame = tk.Frame(self.root, bg="#1e1e1e")
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        self.message_entry = tk.Entry(bottom_frame, font=("Arial", 12))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)

        send_button = tk.Button(
            bottom_frame, text="Send", command=self.send_message,
            bg="#007acc", fg="white", font=("Arial", 11)
        )
        send_button.pack(side=tk.RIGHT)

        self.root.mainloop()

    def send_message(self, event=None):
        msg = self.message_entry.get().strip()
        if not msg:
            return

        # כדי לשלוח למישהו ספציפי אפשר לעשות פה פיצול בדומה ל-main_client.
        # כרגע זה פשוט שולח לכולם (ברודקאסט)
        self.client.send_message("ALL", msg)
        self.display_message("Me", msg)
        self.message_entry.delete(0, tk.END)

    def display_message(self, sender, message):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state="disabled")

if __name__ == "__main__":
    ChatGUI()