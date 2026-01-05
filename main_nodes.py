from node import Node
from crypto_utils import Crypto
from config import NODES
import threading

# מפתחות לכל Node
keys = [Crypto.generate_key() for _ in NODES]

# יצירת Node objects והרצה ב-Threads
nodes = []
threads = []

for i, (ip, port) in enumerate(NODES):
    n = Node(ip, port, keys[i], name=f"Node-{i+1}")
    t = threading.Thread(target=n.start, daemon=True)
    t.start()
    nodes.append(n)
    threads.append(t)

print("All nodes are running. Ready to receive messages...")

# תעשה פקודה שמחזיקה את התוכנית חיה
import time
while True:
    time.sleep(1)
