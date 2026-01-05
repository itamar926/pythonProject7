from client import Client
from main_nodes import keys, NODES

client = Client(NODES, keys)
client.send_message("Hello from my Tor-like network!")
