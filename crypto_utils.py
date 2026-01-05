class Crypto:
    @staticmethod
    def xor(data: bytes, key: bytes) -> bytes:
        return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

    @staticmethod
    def encode_message(message: str) -> bytes:
        return message.encode("utf-8")

    @staticmethod
    def decode_message(data: bytes) -> str:
        return data.decode("utf-8")
