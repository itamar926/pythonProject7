class Packet:
    def __init__(self, sender, target, message):
        self.sender = sender      # מי שולח
        self.target = target      # ALL או שם משתמש
        self.message = message

    def encode(self) -> bytes:
        return f"{self.sender}|{self.target}|{self.message}".encode("utf-8")

    @staticmethod
    def decode(data: bytes):
        text = data.decode("utf-8", errors="ignore")
        parts = text.split("|", 2)
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        return "Unknown", "ALL", text
