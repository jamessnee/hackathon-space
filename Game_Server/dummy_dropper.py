#!/usr/bin/python

"""
Test object for the backend of a dropper player
"""

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


class dummy_dropper(DatagramProtocol):

    def startProtocol(self):

        host = "127.0.0.1"
        port = 9999

        print "Connecting to %s:%d" % (host, port)
        self.transport.connect(host, port)

        self.send("REQ CON D")

    def send(self, data):
        if self.transport:
            print "<-%s" % (data.rstrip(), )
            self.transport.write(data)

    def datagramReceived(self, data, addr):
        print "->%s" % (data.strip(),)

        if data == "PING":
            self.send("PONG")
            return

        if data == "START":
            self.playing = True
            reactor.callLater(0.1, self.drop)

        if data == "STOP":
            self.playing = False

    def connectionRefused(self):
        print "Refused"

    def drop(self):
        if self.playing:
            self.send("DSEND 0")
            reactor.callLater(0.4, self.drop)

reactor.listenUDP(0, dummy_dropper())
reactor.run()
