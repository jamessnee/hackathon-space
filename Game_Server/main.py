#!/usr/bin/python

import sys

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.web.websocket import WebSocketHandler, WebSocketSite
from twisted.web.static import File

import game

gl = None

class UDPDemux(DatagramProtocol):

    def __init__(self, nh):
        self.nh = nh

    def datagramReceived(self, data, addr):
        # print "UDP %s:%d -> %s" % (addr[0], addr[1], data.rstrip())
        self.nh.received(self.transport, data, addr)

class WebSocketDemux(WebSocketHandler):
    
    nh = None
    _id = 0
    
    def write(self, data, addr):
        self.transport.write(data)

    def frameReceived(self, data):
        # check if data comes from a web socket dropper
        if data.startswith("ID:"):
            space_index = data.find(" ")
            id_string = data[3:space_index]
            data = data[space_index + 1:]
            
            # check if this is a new request
            if int(id_string) == 0:
                # generate new id
                self._id = self._id + 1
                id_string = str(self._id)
                # notify dropper of their id
                self.transport.write("ID " + id_string)

        self.nh.received(self, data, id_string)
        
    def closeReceived(self, code, msg):
        print code, msg
        
    def connectionLost(self, reason):
        print "connection lost", reason
        

class NetworkHandler(object):

    def __init__(self):

        self.players = {}

    def listen(self):

        self.udp = UDPDemux(self)
        print "Listening on 9999 for UDP players"
        reactor.listenUDP(9999, self.udp)

        root = File("../Browser_App")
        site = WebSocketSite(root)
        handler = WebSocketDemux
        handler.nh = self
        site.addHandler("/drop", handler)
        print "Listening on 8080 for WebSocket droppers"
        reactor.listenTCP(8080, site)

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
