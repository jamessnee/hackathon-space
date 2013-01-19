#!/usr/bin/python

import sys

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

class Echo(DatagramProtocol):

    def datagramReceived(self, data, (host, port)):
        print "Got '%s' from %s:%d" % (data.strip(), host, port)
        self.transport.write(data, (host, port))


if __name__ == "__main__":
    print "Listening on port 9999"
    reactor.listenUDP(9999, Echo())

    print "Listening on port 9998"
    reactor.listenUDP(9998, Echo())

    reactor.run()
