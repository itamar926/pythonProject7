class Packet:
    def __init__(self, sender, message):
        self.sender = sender
        self.message = message

    def encode(self) -> bytes:
        return f"{self.sender}:{self.message}".encode("utf-8")

    @staticmethod
    def decode(data: bytes):
        text = data.decode("utf-8", errors="ignore")
        sender, msg = text.split(":", 1)
        return sender, msg
