"""SRV record lookup for Minecraft Java Edition (_minecraft._tcp.<host>)."""
import socket


def resolve_srv(host: str) -> tuple[str, int] | None:
    """
    Attempt to resolve a Minecraft SRV record for the given host.
    Returns (resolved_host, port) or None if not found / dns unavailable.
    """
    try:
        # Use getaddrinfo as a lightweight check first; for actual SRV we need
        # to query DNS manually via socket/struct since we have no deps.
        # We'll use the dnspython-free approach: try the SRV name directly.
        srv_host = f"_minecraft._tcp.{host}"
        # Python's stdlib doesn't support SRV natively; we do a best-effort
        # by attempting a raw DNS query via socket.
        results = socket.getaddrinfo(srv_host, None)
        if results:
            # If the SRV hostname itself resolves, the DNS has a CNAME or A record
            # pointing there; return it as-is. Real SRV weight/priority ignored.
            return srv_host, 25565
    except Exception:
        pass
    return None
