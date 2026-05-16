import pygame
import sys
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("rect 개이념이해")
clock = pygame.time.Clock()
player=pygame.Rect()
player=pygame.Rect(100,100,200,150)
wall=pygame.re