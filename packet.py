# packet.py

class Packet:
    def __init__(self, sender, target, msg):
        self.sender = sender
        self.target = target
        self.msg = msg

    def encode(self):
        """הפיכת אובייקט החבילה למחרוזת בתים מוכנה למשלוח"""
        return f"{self.sender}|{self.target}|{self.msg}".encode('utf-8')

    @staticmethod
    def decode(data_bytes):
        """פירוח בתים חזרה לשולח, יעד ותוכן ההודעה"""
        parts = data_bytes.decode('utf-8', errors='ignore').split("|", 2)
        return parts[0], parts[1], parts[2]