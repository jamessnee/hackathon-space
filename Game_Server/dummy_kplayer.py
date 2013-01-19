#!/usr/bin/python

"""
Test object for the backend of the kplayer
"""

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


class dummy_kplayer(DatagramProtocol):

    def startProtocol(self):

        host = "127.0.0.1"
        port = 9998

        print "Connecting to %s:%d" % (host, port)
        self.transport.connect(host, port)

        self.transport.write("Yay")

    def datagramReceived(self, data, (host, port)):
        print "Got '%s' from %s:%d" % (data.strip(), host, port)

    def connectionRefused(self):
        print "Refused"


reactor.listenUDP(0, dummy_kplayer())
reactor.run()
