import threading
import time
from node import Node
from config import NODES, KEYS

if __name__ == "__main__":
    for i, (ip, port) in enumerate(NODES):
        next_node = NODES[i + 1] if i + 1 < len(NODES) else None
        node = Node(
            host=ip,
            port=port,
            key=KEYS[i],
            next_node=next_node,
            name=f"Node-{i+1}"
        )
        t = threading.Thread(target=node.start, daemon=True)
        t.start()

    print("All nodes are running.")
    while True:
        time.sleep(1)
