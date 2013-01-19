#!/usr/bin/python

"""
Test object for the backend of a dropper player
"""

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

from random import randrange

class dummy_dropper(DatagramProtocol):

    def startProtocol(self):

        host = "127.0.0.1"
        port = 9999

        print "Connecting to %s:%d" % (host, port)
        self.transport.connect(host, port)

        self.send("REQ CON D")

    def send(self, data):
        if self.transport:
            if data != "PONG":
                print "<-%s" % (data.rstrip(), )

                self.transport.write(data)

    def datagramReceived(self, data, addr):
        if data != "PING":
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
            self.send("DSEND %d" % (randrange(480),) )
            reactor.callLater(0.4, self.drop)

reactor.listenUDP(0, dummy_dropper())
reactor.run()
