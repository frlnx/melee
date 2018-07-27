from engine.engine import Engine
from engine.network.update_protocol import UpdateProtocol


class UpdateServerProtocol(UpdateProtocol):

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.addresses = []
        self.engine.schedule_interval(self.update, interval=1)

    def register_address(self, ip, port):
        self.addresses.append((ip, port))

    def unregister_address(self, ip, port):
        self.addresses.remove((ip, port))

    def datagramReceived(self, datagram, addr):
        super(UpdateServerProtocol, self).datagramReceived(datagram, addr)
        self.broadcast(datagram, ignore=addr)

    def send(self, data):
        ser = self.serialize(data)
        self.broadcast(ser)

    def broadcast(self, ser: bytes, ignore=None):
        for address in self.addresses:
            if ignore and ignore == address:
                continue
            self.transport.write(ser, address)