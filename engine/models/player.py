from engine.models.ship import ShipModel
from engine.network.server.event_protocol import BroadcastProtocol
from engine.network.server.update_protocol import UpdateServerProtocol


class Player(object):

    def __init__(self, callsign, ship: ShipModel):
        self.callsign = callsign
        self.ship = ship


class ServerPlayer(Player):

    def __init__(self, callsign, ship: ShipModel, tcp_protocol: BroadcastProtocol, udp_protocol: UpdateServerProtocol):
        super().__init__(callsign, ship)
        self.tcp_protocol = tcp_protocol
        self.udp_protocol = udp_protocol
