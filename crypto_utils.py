class Crypto:
    @staticmethod
    def xor(data: bytes, key: int) -> bytes:
        """ ביצוע הצפנת XOR פשוטה באמצעות מפתח בגודל בייט אחד """
        return bytes([b ^ key for b in data])