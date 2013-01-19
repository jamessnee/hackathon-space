#! /usr/bin/env python

import pygame
import freenect
import frame_convert
from pygame.locals import *
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import DatagramProtocol


class kplayer(DatagramProtocol):
	def __init__(self):
		self.x_pos = 0
		self.lives = 1
		self.dropping_objects = [(10,10)]
		self.connection = False

	def move(self,delta):
		self.x_pos = self.x_pos + delta
		print "Sending players new position"
		to_send = "KSEND "+str(self.x_pos)
		self.transport.write(to_send)

	def startProtocol(self):
		host = "131.111.179.97"
		port = 9999
		
		print "Opening connection"
		self.transport.connect(host,port)
		self.transport.write("REQ CON K")

	def datagramReceived(self, data, (host,port)):
		data_strip = data.strip()
		if data_strip == "PING":
			print "Ping > PONG"
			self.transport.write("PONG")
		elif data_strip == "REQ OK":
			print "Connection accepted"
		elif data_strip == "START":
			print "Game Started"
			self.connection = True
		elif data_strip == "REQ REJECT":
			print "Connection rejected"
			self.connection = False
		else:
			print "Couldn't parse:",data.strip()

	def connectionRefused(self):
		print "Refused"


def get_depth():
    return frame_convert.pretty_depth(freenect.sync_get_depth()[0])

def to_len(ar):
    for x in range(1, len(ar)-1):
        ar[x] = ar[x-1] * ar[x] + ar[x]
    return ar
        
def max_run(ar):
    max = i = pos = 0
    for x in ar:
        i += 1
        if x > max:
            max = x
            pos = i
    return pos - max / 2


def get_kplayer_pos_from_kinect():
    x = get_depth()[200]
    y = map (lambda x : 1 if x < 200 else 0, x)
    return max_run(to_len(y)) / 10


def pygame_loop():
	"""Draw the background"""
	window.blit(background,(0,0))

	"""Draw the kplayer"""
	window.blit(spaceship,(player.x_pos,410))

	"""Draw a dropping object"""
	for dropped in player.dropping_objects:
		carrot = pygame.image.load("Images/carrot.png").convert()
		window.blit(carrot,(dropped[0],dropped[1]))

	"""Do some collision detection"""

	pygame.display.update()
	if player.connection:
	player.move(get_kplayer_pos_from_kinect())


if __name__ == "__main__" :
	pygame.init()
	window = pygame.display.set_mode((640, 480))
	background = pygame.image.load("Images/background.png").convert()
	spaceship = pygame.image.load("Images/hajo1.png").convert()

	player = kplayer()

	window.blit(background,(0,0))

	reactor.listenUDP(0,player)	
	lp = LoopingCall(pygame_loop)
	lp.start(1)
	reactor.run()

