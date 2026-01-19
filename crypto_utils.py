class Crypto:
    @staticmethod
    def xor(data: bytes, key: int) -> bytes:
        return bytes(b ^ key for b in data)
