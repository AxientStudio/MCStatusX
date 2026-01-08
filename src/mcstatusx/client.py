import socket
import json
import struct
import time


def _varint(sock):
    num = 0
    for i in range(5):
        byte = sock.recv(1)
        if not byte:
            raise RuntimeError
        b = byte[0]
        num |= (b & 0x7F) << (7 * i)
        if not (b & 0x80):
            return num
    raise RuntimeError


def _read(sock):
    length = _varint(sock)
    data = b""
    while len(data) < length:
        data += sock.recv(length - len(data))
    return data


def ping_java(host, port, timeout=3):
    sock = socket.socket()
    sock.settimeout(timeout)

    start = time.time()
    sock.connect((host, port))

    # Handshake
    data = b"\x00" + b"\x00" + struct.pack(">H", port) + b"\x01"
    data = struct.pack(">b", len(host)) + host.encode() + data
    packet = b"\x00" + data
    packet = struct.pack(">b", len(packet)) + packet
    sock.send(packet)

    sock.send(b"\x01\x00")  # Status request

    raw = _read(sock)
    ping = int((time.time() - start) * 1000)

    sock.close()
    return json.loads(raw.decode()), ping