#! /usr/bin/env python
import pygame

IMAGE_DIR = "Images/"
IMAGE_SPACESHIP = IMAGE_DIR+"hajo1.png"



def parse_server_message(message):
	print "Parsing the server's message"

def draw_screen(player,dropped_items):
	print "Drawing the player"
	print "Drawing the dropped items"

if __name__=="__main__":
	print "Do that funky thing!"
	screen = pygame.display.set_mode((640,480))
	spaceship = pygame.image.load(IMAGE_SPACESHIP)
	background = pygame.image.load("Images/background.png")
	screen.blit(background,(0,0))
