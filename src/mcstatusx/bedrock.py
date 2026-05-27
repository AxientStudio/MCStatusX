import socket
import struct
import time
from .errors import PacketError, ProtocolError

# RakNet magic bytes (16-byte GUID)
_RAKNET_MAGIC = b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78"

# Unconnected Ping packet ID
_ID_UNCONNECTED_PING = 0x01
# Unconnected Pong packet ID
_ID_UNCONNECTED_PONG = 0x1c


def ping_bedrock(host: str, port: int = 19132, timeout: float = 3) -> dict:
    """
    Ping a Bedrock (MCPE/MCEE) server using the RakNet Unconnected Ping protocol.
    Returns a dict with parsed server info.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        # Build Unconnected Ping packet
        timestamp = int(time.time() * 1000)
        packet = (
            bytes([_ID_UNCONNECTED_PING])
            + struct.pack(">Q", timestamp)   # 8-byte time
            + _RAKNET_MAGIC                  # 16-byte magic
            + struct.pack(">Q", 0)           # client GUID (0 for status)
        )

        start = time.time()
        sock.sendto(packet, (host, port))
        data, _ = sock.recvfrom(4096)
        ping_ms = int((time.time() - start) * 1000)

        if not data or data[0] != _ID_UNCONNECTED_PONG:
            raise ProtocolError("Expected Unconnected Pong, got unexpected packet ID")

        # Pong layout:
        #   1 byte  — packet ID (0x1c)
        #   8 bytes — timestamp
        #   8 bytes — server GUID
        #  16 bytes — magic
        #   2 bytes — string length (big-endian unsigned short)
        #   N bytes — MOTD string (semicolon-delimited)

        if len(data) < 35:
            raise PacketError("Pong packet too short")

        str_len = struct.unpack_from(">H", data, 33)[0]
        motd_bytes = data[35:35 + str_len]

        try:
            motd_raw = motd_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            raise PacketError(f"Failed to decode MOTD string: {e}")

        parts = motd_raw.split(";")
        # MCPE;motd;protocol;version;online;max;server_id;sub_motd;gamemode_str;gamemode_int;port4;port6
        def _get(i, cast=str, default=None):
            try:
                return cast(parts[i]) if len(parts) > i else default
            except (ValueError, IndexError):
                return default

        return {
            "edition":     _get(0) or "MCPE",
            "motd":        _get(1),
            "protocol":    _get(2, int),
            "version":     _get(3),
            "players":     _get(4, int, 0),
            "max_players": _get(5, int, 0),
            "server_id":   _get(6),
            "sub_motd":    _get(7),
            "gamemode":    _get(8),
            "ping":        ping_ms,
        }

    finally:
        sock.close()
