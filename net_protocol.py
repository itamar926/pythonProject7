# net_protocol.py

def send_data(sock, data):
    """שליחת נתונים עם קידומת אורך של 4 בתים"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    length = len(data)
    sock.sendall(length.to_bytes(4, byteorder='big') + data)

def recv_data(sock):
    """קריאת נתונים על בסיס קידומת האורך שהתקבלה"""
    raw_length = sock.recv(4)
    if not raw_length: 
        return b""
    length = int.from_bytes(raw_length, byteorder='big')
    data = b""
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet: 
            return b""
        data += packet
    return data