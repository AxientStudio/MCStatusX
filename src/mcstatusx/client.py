import socket
import json
import struct
import time
from .errors import PacketError, ProtocolError


# ── VarInt helpers ────────────────────────────────────────────────────────────

def _encode_varint(value: int) -> bytes:
    """Encode an integer as a Minecraft VarInt."""
    out = b""
    for _ in range(5):
        part = value & 0x7F
        value >>= 7
        if value:
            part |= 0x80
        out += bytes([part])
        if not value:
            break
    return out


def _decode_varint(sock: socket.socket) -> int:
    """Read and decode a VarInt from a socket."""
    num = 0
    for i in range(5):
        raw = sock.recv(1)
        if not raw:
            raise PacketError("Connection closed while reading VarInt")
        b = raw[0]
        num |= (b & 0x7F) << (7 * i)
        if not (b & 0x80):
            return num
    raise PacketError("VarInt too long (>5 bytes)")


def _read_packet(sock: socket.socket) -> bytes:
    """Read a length-prefixed packet from the socket."""
    length = _decode_varint(sock)
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise PacketError("Connection closed mid-packet")
        data += chunk
    return data


def _build_handshake(host: str, port: int) -> bytes:
    """Build SLP handshake + status request packets."""
    host_bytes = host.encode("utf-8")

    # Packet 0x00 — Handshake
    payload = (
        _encode_varint(0x00)          # Packet ID
        + _encode_varint(47)           # Protocol version (any; server ignores for status)
        + _encode_varint(len(host_bytes))
        + host_bytes
        + struct.pack(">H", port)
        + _encode_varint(1)            # Next state: 1 = Status
    )
    handshake = _encode_varint(len(payload)) + payload

    # Packet 0x00 — Status Request
    status_req = b"\x01\x00"

    return handshake + status_req


# ── Java ping ─────────────────────────────────────────────────────────────────

def ping_java(host: str, port: int, timeout: float = 3) -> tuple[dict, int]:
    """
    Perform SLP (Server List Ping) against a Java Edition server.
    Returns (parsed_json_dict, ping_ms).
    Raises PacketError or ProtocolError on bad responses.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        start = time.time()
        sock.connect((host, port))
        sock.send(_build_handshake(host, port))

        raw_packet = _read_packet(sock)
        ping_ms = int((time.time() - start) * 1000)

        # Strip packet ID byte (0x00)
        if not raw_packet or raw_packet[0] != 0x00:
            raise ProtocolError("Unexpected packet ID in status response")

        # Read string length (VarInt) then the JSON string
        idx = 1
        str_len = 0
        shift = 0
        while idx < len(raw_packet):
            b = raw_packet[idx]
            idx += 1
            str_len |= (b & 0x7F) << shift
            shift += 7
            if not (b & 0x80):
                break

        json_bytes = raw_packet[idx:idx + str_len]

        try:
            data = json.loads(json_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ProtocolError(f"Invalid JSON in status response: {e}")

        return data, ping_ms

    finally:
        sock.close()
