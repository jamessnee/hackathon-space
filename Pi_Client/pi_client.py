import pygame
from pygame.locals import *

if __name__ == "__main__" :
	screen = pygame.display.set_mode((640,480))
	background = pygame.image.load("Images/background.png").convert()
	screen.blit(background,(0,0))
	while 1:
		screen.blit(background,(0,0))
		pygame.display.update()
		pygame.time.delay(100)