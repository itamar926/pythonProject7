from node import Node
import threading

# שימוש בכתובת מקומית לבדיקות (127.0.0.1)
nodes = [
    Node("Node-1", "0.0.0.0", 9010, "127.0.0.1", 9020, 11),
    Node("Node-2", "0.0.0.0", 9020, "127.0.0.1", 9030, 22),
    Node("Node-3", "0.0.0.0", 9030, None, None, 33)
]

for n in nodes:
    threading.Thread(target=n.start, daemon=True).start()

print("All Tor nodes are running on Localhost.")
input("Press Enter to exit...\n")