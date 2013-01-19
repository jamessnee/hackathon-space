#!/usr/bin/python

import sys

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

import game

gl = None

class UDPDemux(DatagramProtocol):

    def __init__(self, nh):
        self.nh = nh

    def datagramReceived(self, data, addr):
        # print "UDP %s:%d -> %s" % (addr[0], addr[1], data.rstrip())
        self.nh.received(self.transport, data, addr)

class NetworkHandler(object):

    def __init__(self):

        self.players = {}

    def listen(self):

        self.udp = UDPDemux(self)
        print "Listening on 9999 for UDP players"
        reactor.listenUDP(9999, self.udp)

    # Received data from the network
    def received(self, trans, data, addr):

        # If known, pass on to player
        if addr in self.players:
            self.players[addr].received(data)
            return

        # If new, try to create new player
        elif data.startswith("REQ CON"):
            ptype = data[7:].strip()

            if ptype == "K":
                p = game.Kplayer(self, trans, addr, gl)
                gl.add_kplayer(p)
                return
            elif ptype == "D":
                p = game.Dropper(self, trans, addr, gl)
                gl.add_dropper(p)
                return

        # Or give up
        trans.write("ERROR", addr)

    def add(self, player):
        assert player.addr not in self.players
        self.players[player.addr] = player

    def remove(self, player):
        assert player.addr in self.players
        del self.players[player.addr]


if __name__ == "__main__":

    nh = NetworkHandler()
    gl = game.Logic()

    nh.listen()

    reactor.run()
