# mcstatusx.py
import socket
import struct
import json
from dataclasses import dataclass
from typing import List, Optional


# =========================
# Exceptions (mcstatus-like)
# =========================

class MCStatusError(Exception):
    """Base exception for mcstatus"""


class DNSLookupFailed(MCStatusError):
    pass


class ConnectionRefused(MCStatusError):
    pass


class ConnectionTimeout(MCStatusError):
    pass


class InvalidResponse(MCStatusError):
    pass


# =========================
# Data models
# =========================

@dataclass
class PlayerSample:
    name: str
    uuid: str


@dataclass
class Players:
    online: int
    max: int
    sample: Optional[List[PlayerSample]]


@dataclass
class Version:
    name: str
    protocol: int


@dataclass
class StatusResponse:
    version: Version
    players: Players
    description: str
    favicon: Optional[str]
    raw: dict  # full raw json (minh bạch)


# =========================
# Low-level protocol utils
# =========================

def _varint_encode(value: int) -> bytes:
    out = b""
    while True:
        byte = value & 0x7F
        value >>= 7
        out += struct.pack("B", byte | (0x80 if value > 0 else 0))
        if value == 0:
            break
    return out


def _varint_decode(sock) -> int:
    num = 0
    shift = 0
    while True:
        b = sock.recv(1)
        if not b:
            raise InvalidResponse("Connection closed while reading VarInt")
        val = b[0]
        num |= (val & 0x7F) << shift
        if not (val & 0x80):
            return num
        shift += 7
        if shift > 35:
            raise InvalidResponse("VarInt too large")


def _recv_exact(sock, length: int) -> bytes:
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise InvalidResponse("Connection closed early")
        data += chunk
    return data


def _send_packet(sock, packet_id: int, data: bytes):
    packet = _varint_encode(packet_id) + data
    sock.sendall(_varint_encode(len(packet)) + packet)


# =========================
# High-level API
# =========================

def _parse_address(address: str, default_port: int):
    if ":" in address:
        host, port_str = address.rsplit(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            raise DNSLookupFailed("Invalid port number")
        return host, port
    return address, default_port

def ping(
    address: str,
    port: int = 25565,
    timeout: float = 3.0
) -> StatusResponse:
    # ---- Parse host:port n?u ng??i d?ng d?n IP:PORT ----
    host, port = _parse_address(address, port)

    try:
        sock = socket.create_connection((host, port), timeout=timeout)
    except socket.gaierror:
        raise DNSLookupFailed("Failed to resolve hostname")
    except ConnectionRefusedError:
        raise ConnectionRefused("Connection refused by server")
    except socket.timeout:
        raise ConnectionTimeout("Connection timed out")

    try:
        # ---- Handshake (STATUS) ----
        handshake_data = (
            _varint_encode(754) +  # protocol version (dummy but valid)
            _varint_encode(len(host)) + host.encode("utf-8") +
            struct.pack(">H", port) +
            _varint_encode(1)  # next state = STATUS
        )
        _send_packet(sock, 0x00, handshake_data)

        # ---- Status request ----
        _send_packet(sock, 0x00, b"")

        # ---- Read response ----
        _varint_decode(sock)        # packet length
        packet_id = _varint_decode(sock)
        if packet_id != 0x00:
            raise InvalidResponse("Invalid status response")

        json_length = _varint_decode(sock)
        raw_json = _recv_exact(sock, json_length)
        data = json.loads(raw_json.decode("utf-8"))

    except socket.timeout:
        raise ConnectionTimeout("Connection timed out while reading data")
    except json.JSONDecodeError:
        raise InvalidResponse("Server returned malformed JSON")
    finally:
        sock.close()

    # ---- Parse structured result ----
    version = Version(
        name=data["version"]["name"],
        protocol=data["version"]["protocol"]
    )

    sample = None
    if "sample" in data["players"]:
        sample = [
            PlayerSample(p["name"], p["id"])
            for p in data["players"]["sample"]
        ]

    players = Players(
        online=data["players"]["online"],
        max=data["players"]["max"],
        sample=sample
    )

    description = (
        data["description"]["text"]
        if isinstance(data["description"], dict)
        else data["description"]
    )

    return StatusResponse(
        version=version,
        players=players,
        description=description,
        favicon=data.get("favicon"),
        raw=data
    )
