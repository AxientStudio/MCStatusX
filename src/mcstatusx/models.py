class Version:
    def __init__(self, name=None, protocol=None):
        self.name = name
        self.protocol = protocol


class Players:
    def __init__(self, online=0, max=0, sample=None):
        self.online = online
        self.max = max
        self.sample = sample or []


class Status:
    def __init__(self, online=False, version=None, players=None, motd=None, ping=None, raw=None):
        self.online = online
        self.version = version
        self.players = players
        self.motd = motd
        self.ping = ping
        self.raw = raw