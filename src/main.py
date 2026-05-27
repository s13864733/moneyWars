import pygame
from player import *
from hud import HUD
from scenes import Market
from settings import (
    GAME_WIDTH, GAME_HEIGHT, FULLSCREEN,
    MONEY,
    WHITE
    )

pygame.init()

sceneOpen = False
running = True

if FULLSCREEN:
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
clock = pygame.time.Clock()
dt = 0

player = Player(100, 100, "P1", MONEY)
hud = HUD(player)
market = Market()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not sceneOpen:
        player.update(dt)

        screen.fill((100, 100, 100))
        player.draw(screen)
        player.drawDebug(screen)
    else:
        # market test
        market.draw(screen)
    
    hud.draw(screen, clock)

    pygame.display.flip()
    dt = clock.tick(120) / 1000