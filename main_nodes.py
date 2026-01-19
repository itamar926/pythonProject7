from node import Node
from visualizer import Visualizer
import threading

vis = Visualizer()

nodes = [
    Node("Node-1", "0.0.0.0", 9010, "127.0.0.1", 9020, 11, vis),
    Node("Node-2", "0.0.0.0", 9020, "127.0.0.1", 9030, 22, vis),
    Node("Node-3", "0.0.0.0", 9030, None, None, 33, vis),
]

for n in nodes:
    threading.Thread(target=n.start, daemon=True).start()

print("All Tor nodes are running")
vis.start()
