#!/usr/bin/python
from __future__ import division

from time import time
from collections import deque

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall

from random import randrange
from copy import deepcopy as _dc


### Constants to tweak
# Initial items to be dropped
INITIAL_DROPQ = deque([0, 0, 0])
# New item to drop every # seconds
REFILL_EVERY = 1.5

# Drop speed random between # and # px per gameloop
DROP_SPEED_MIN = 3
DROP_SPEED_MAX = 10

# Kplayer initial lives
KPLAYER_LIVES = 3

# Game loop every # seconds
GAME_LOOP = 0.05


### Constants not to tweak
KPLAYER_DIM = 64.0
DROP_DIM = [ 20.0 ]

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
        # print "%s:%d <- %s" % (self.addr[0], self.addr[1], data.rstrip())
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
        self.send("ERROR %s" % (e,))
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

        try:
            pos = int(data[6:])
        except StandardError:
            self.error()

        self.gl.dropper_drop(pos)

    def die(self):
        self.gl.rm_dropper(self)
        self.cleanup()


class Kplayer(Player):

    def __init__(self, nh, trans, addr, gl):
        Player.__init__(self, nh, trans, addr)
        self.gl = gl

        self.lives = 0
        self.pos = 0

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

class Drop(object):

    def __init__(self, i, x, y, v):
        self.id = i
        self.x = x
        self.y = y
        self.v = v

##########################################################################

class Logic(object):

    STATE_WAITING = 0
    STATE_PLAYING = 1

    def __init__(self):

        self.kplayer = None
        self.droppers = []

        self.dropq = deque()
        self.drops = []

        self.state = Logic.STATE_WAITING

        self.loop = LoopingCall(self.game_loop)
        self.refill_loop = LoopingCall(self.refill_dropq)

    def broadcast(self, data):
        if self.kplayer:
            self.kplayer.send(data)
        for d in self.droppers:
            d.send(data)

    def possible_collision(self, drop):

        KDIM = KPLAYER_DIM / 2.0

        KC_X = float(self.kplayer.pos) + KDIM
        KC_Y = KDIM

        DDIM = DROP_DIM[drop.id] / 2.0

        DC_X = float(drop.x) + DDIM
        DC_Y = float(drop.y) - DDIM

        if ( (KC_X - DC_X)**2 + (KC_Y - DC_Y)**2 ) <= ( KDIM + DDIM )**2 :

            self.kplayer.lives -= 1
            # Call possibly stop after this game loop has completed
            reactor.callLater(0, self.possibly_stop)

            return True
        else:
            return False

    def game_loop(self):

        drops = self.drops[:]
        self.drops = []

        for drop in drops:
            if drop.y < 1:
                continue
            drop.y -= drop.v

            if drop.y < KPLAYER_DIM + DROP_DIM[drop.id]:
                # Destroy objects which have collided
                if self.possible_collision(drop):
                    continue

            self.drops.append(drop)

        def drops2str(d):
            return "%d:%d,%d" % (d.id, d.x, d.y)

        Q = ','.join((str(x) for x in self.dropq))
        DS = (drops2str(x) for x in self.drops)

        self.broadcast("STATE K:%d Q:%s L:%d %s"
                       % (self.kplayer.pos, Q,
                          self.kplayer.lives, ' '.join(DS)) )

    def refill_dropq(self):
        if len(self.dropq) < 5: # Eventually dynamic
            self.dropq.append(0) # Eventually item ID

#####

    def _start(self):
        self.state = Logic.STATE_PLAYING
        self.broadcast("START")
        print "Starting Game"

        self.dropq = _dc(INITIAL_DROPQ)
        self.drops = []

        self.kplayer.lives = _dc(KPLAYER_LIVES)

        self.refill_loop.start(_dc(REFILL_EVERY))

        # Call immediatly afterwards
        reactor.callLater(0, self.loop.start, _dc(GAME_LOOP), True)


    def _stop(self):
        self.state = Logic.STATE_WAITING
        self.broadcast("STOP")
        print "Stopping Game"

        try:
            self.loop.stop()
            self.refill_loop.stop()
        except AssertionError:
            # I REALLY WANT THESE DAM LOOPS TO STOP!!!
            pass


    def possibly_start(self):
        if self.state == Logic.STATE_PLAYING:
            return
        if ( self.kplayer is not None and len(self.droppers) > 0 ):
            self._start()

    def possibly_stop(self):
        if self.state == Logic.STATE_WAITING:
            return
        if ( self.kplayer is None or self.kplayer.lives == 0 or
             len(self.droppers) == 0 ):
            self._stop()

#####
    def add_kplayer(self, kplayer):
        if self.kplayer is None:
            self.kplayer = kplayer
            self.kplayer.accept()
            self.possibly_start()
            print "Got Kplayer"
        else:
            kplayer.reject()

    def rm_kplayer(self):
        self.kplayer = None
        print "Lost Kplayer"
        self.possibly_stop()

    def kplayer_move(self, pos):

        if not ( 0 <= pos <= 640 ):
            print "Kplayer invalid position %d" % (pos,)
            self.possibly_stop()
        else:
            self.kplayer.pos = pos

#####

    def add_dropper(self, dropper):
        self.droppers.append(dropper)
        dropper.accept()
        self.possibly_start()
        print "New dropper.  Got %d" % (len(self.droppers), )

    def rm_dropper(self, dropper):
        self.droppers.remove(dropper)
        self.possibly_stop()
        print "Lost dropper.  Got %d" % (len(self.droppers), )

    def dropper_drop(self, drop_pos):

        if not ( 0 <= drop_pos <= 640 ):
            print "Kplayer invalid position %d" % (drop_pos,)
            return

        if len(self.dropq) == 0:
            return # nothing to drop

        d_id = self.dropq.pop()
	print "Dropping id %d at pos %d" % (d_id, drop_pos)

        D = Drop(d_id, drop_pos, 480,
                 randrange(_dc(DROP_SPEED_MIN), _dc(DROP_SPEED_MAX)))
        self.drops.append(D)
