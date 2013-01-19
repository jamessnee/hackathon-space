#!/usr/bin/python

import sys

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

class Echo(DatagramProtocol):

    def datagramReceived(self, data, (host, port)):
        print "Got '%s' from %s:%d" % (data.strip(), host, port)
        self.transport.write(data, (host, port))


if __name__ == "__main__":
    reactor.listenUDP(9999, Echo())
    reactor.run()
