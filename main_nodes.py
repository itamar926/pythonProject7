from node import Node
import threading

SERVER_IP = "172.16.15.49"

nodes = [
    Node("Node-1", "0.0.0.0", 9010, "172.16.15.49", 9020, 11),
    Node("Node-2", "0.0.0.0", 9020, "172.16.15.49", 9030, 22),
    Node("Node-3", "0.0.0.0", 9030, None, None, 33)
]

for n in nodes:
    threading.Thread(target=n.start, daemon=True).start()

print("All Tor nodes are running.")
input("Press Enter to exit...\n")
