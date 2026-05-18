import socket

HEADER_SIZE = 8


def send_data(sock, data_bytes):
    """ שולח נתונים בתוספת כותרת של גודל החבילה (Length Prefix) """
    try:
        msg_length = len(data_bytes)
        # יוצר כותרת באורך קבוע של 8 תווים וממלא ברווחים
        header = f"{msg_length:<{HEADER_SIZE}}".encode('utf-8')
        sock.sendall(header + data_bytes)
    except Exception as e:
        print(f"[Protocol Error] Failed to send: {e}")


def recv_data(sock):
    """ קורא את הכותרת, מבין מה הגודל המדויק, וקורא את כל החבילה """
    try:
        # קוראים קודם כל את הכותרת (8 בייטים)
        header = b""
        while len(header) < HEADER_SIZE:
            chunk = sock.recv(HEADER_SIZE - len(header))
            if not chunk: return None
            header += chunk

        # מחלצים את הגודל מתוך הכותרת
        msg_length = int(header.decode('utf-8').strip())

        # קוראים את הנתונים עצמם בדיוק לפי הגודל שחולץ
        data = b""
        while len(data) < msg_length:
            chunk = sock.recv(msg_length - len(data))
            if not chunk: break
            data += chunk

        return data
    except Exception as e:
        return None