import json

class Packet:
    def __init__(self, sender, target, message):
        self.sender = sender
        self.target = target
        self.message = message

    def encode(self) -> bytes:
        """ אריזת ההודעה למבנה JSON והפיכה לבייטים """
        data = {
            "sender": self.sender,
            "target": self.target,
            "message": self.message
        }
        return json.dumps(data).encode('utf-8')

    @staticmethod
    def decode(data_bytes: bytes):
        """ פריסת הבייטים בחזרה למאפייני ההודעה המקוריים """
        data = json.loads(data_bytes.decode('utf-8'))
        return data["sender"], data["target"], data["message"]