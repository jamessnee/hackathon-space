#!/usr/bin/python

from time import time

from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall


class Player(object):

    def __init__(self, nh, trans, addr):
        self.nh = nh
        self.trans = trans
        self.addr = addr

        self.timestamp = time()

        self.pinger = LoopingCall(self.ping)

    def cleanup(self):
        self.pinger.stop()

    # Send data
    def send(self, data):
        print "%s:%d <- %s" % (self.addr[0], self.addr[1], data.rstrip())
        self.trans.write(data, self.addr)

    def received(self, data):
        self.timestamp = time()

        if data == "PONG":
            return

        self.recv_data(data)

    def ping(self):

        now = time()

        if (now - self.timestamp) > 1:
            self.send("PING")

        if (now - self.timestamp) > 3:
            self.die()

    def accept(self):
        self.nh.add(self)
        self.send("REQ OK")
        self.pinger.start(0.5)

    def reject(self):
        self.send("REQ REJECT")

    def error(self, e = ""):
        self.send("ERROR %s")
        self.nh.remove(self)
        self.die()

##########################################################################

class Dropper(Player):

    def __init__(self, nh, trans, addr, gl):
        Player.__init__(self, nh, trans, addr)
        self.gl = gl

    def recv_data(self, data):

        if not data.startswith("DSEND"):
            self.error()

        self.gl.dropper_drop(self)

    def die(self):
        self.gl.rm_dropper(self)
        self.cleanup()


class Kplayer(Player):

    def __init__(self, nh, trans, addr, gl):
        Player.__init__(self, nh, trans, addr)
        self.gl = gl

    def recv_data(self, data):

        if not data.startswith("KSEND"):
            self.error()

        try:
            pos = int(data[6:])
        except StandardError:
            self.error()

        self.gl.kplayer_move(pos)

    def die(self):
        self.gl.rm_kplayer()
        self.cleanup()

##########################################################################

class Logic(object):

    STATE_WAITING = 0
    STATE_PLAYING = 1

    def __init__(self):

        self.kplayer = None
        self.droppers = []

        self.state = Logic.STATE_WAITING

    def broadcast(self, data):
        if self.kplayer:
            self.kplayer.send(data)
        for d in self.droppers:
            d.send(data)

#####

    def start(self):
        self.state = Logic.STATE_PLAYING
        self.broadcast("START")
        print "Starting Game"

    def stop(self):
        self.state = Logic.STATE_WAITING
        self.broadcast("STOP")
        print "Stopping Game"

    def possibly_start(self):
        if self.state == Logic.STATE_PLAYING:
            return
        if ( self.kplayer is not None and len(self.droppers) > 0 ):
            self.start()

    def possibly_stop(self):
        if self.state == Logic.STATE_WAITING:
            return
        if ( self.kplayer is None or len(self.droppers) == 0 ):
            self.stop()

#####
    def add_kplayer(self, kplayer):
        if self.kplayer is None:
            self.kplayer = kplayer
            self.kplayer.accept()
            self.possibly_start()
        else:
            kplayer.reject()

    def rm_kplayer(self):
        self.kplayer = None
        print "Kplayer died :("
        self.stop()

    def kplayer_move(self, pos):
        print "Kplayer is now at %d" % (pos, )

#####

    def add_dropper(self, dropper):
        self.droppers.append(dropper)
        dropper.accept()
        self.possibly_start()
        print "New dropper"

    def rm_dropper(self, dropper):
        self.droppers.remove(dropper)
        self.possibly_stop()
        print "Lost dropper"

    def dropper_drop(self, dropper):
        print "Dropper dropped something..."
