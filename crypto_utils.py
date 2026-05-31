# crypto_utils.py

class Crypto:
    @staticmethod
    def xor(data: bytes, key: int) -> bytes:
        """מבצע הצפנת/פענוח XOR סימטרית על מערך בתים באמצעות מפתח קבוע"""
        return bytes([b ^ (key % 256) for b in data])