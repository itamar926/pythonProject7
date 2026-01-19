from client import Client

client = Client(
    name="Bob",
    entry_ip="127.0.0.1",
    entry_port=9010,
    listen_port=9102,
    keys=[11, 22, 33]
)

while True:
    msg = input("Bob> ")
    client.send(msg, target_port=9101)
