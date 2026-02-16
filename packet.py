class Packet:

    def __init__(self, sender, target, message):
        self.sender = sender
        self.target = target
        self.message = message

    def encode(self):
        return f"{self.sender}|{self.target}|{self.message}".encode()

    @staticmethod
    def decode(data):
        text = data.decode()
        sender, target, message = text.split("|", 2)
        return sender, target, message
