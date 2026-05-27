class MCStatusError(Exception):
    code = "UNKNOWN_ERROR"

    def __init__(self, message=None):
        self.message = message or self.code
        super().__init__(self.message)


class ResolveError(MCStatusError):
    code = "Failed to resolve hostname"


class TimeoutError(MCStatusError):
    code = "Connection timed out"


class OfflineError(MCStatusError):
    code = "Server is offline"


class InvalidAddressError(MCStatusError):
    code = "Invalid address format"


class ProtocolError(MCStatusError):
    code = "Protocol handshake failed"


class PacketError(MCStatusError):
    code = "Malformed packet received"
