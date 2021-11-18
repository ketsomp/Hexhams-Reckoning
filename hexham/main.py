import pygame
from pygame import *
import tkinter

pygame.init()

screen=pygame.display.set_mode((1000,800))
pygame.display.set_caption("Hexham's Reckoning")

#define position of sprites, render objects on screen here
def draw_window():
	screen.fill((255,0,0))
	pygame.display.flip()


#main loop
running=True
while running:
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			running=False
	draw_window()

