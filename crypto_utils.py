class Crypto:
    @staticmethod
    def xor_encrypt(data: bytes, key: bytes) -> bytes:
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

    @staticmethod
    def xor_decrypt(data: bytes, key: bytes) -> bytes:
        return Crypto.xor_encrypt(data, key)

    @staticmethod
    def generate_key(length=16) -> bytes:
        from random import randint
        return bytes([randint(0, 255) for _ in range(length)])
