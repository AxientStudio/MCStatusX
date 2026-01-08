import socket
import time


def ping_bedrock(host, port=19132, timeout=3):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    packet = b"\x01" + int(time.time() * 1000).to_bytes(8, "big") + b"\x00" * 16
    start = time.time()

    sock.sendto(packet, (host, port))
    data, _ = sock.recvfrom(2048)

    ping = int((time.time() - start) * 1000)
    sock.close()

    text = data.decode(errors="ignore")
    parts = text.split(";")

    return {
        "edition": "MCPE",
        "motd": parts[1] if len(parts) > 1 else None,
        "version": parts[3] if len(parts) > 3 else None,
        "players": int(parts[4]) if len(parts) > 4 else None,
        "max_players": int(parts[5]) if len(parts) > 5 else None,
        "ping": ping,
    }