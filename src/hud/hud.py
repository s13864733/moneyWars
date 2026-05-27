import pygame
from settings import WHITE

class HUD:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.SysFont("Arial", 16)

    def draw(self, screen, clk):
        fps = clk.get_fps()
        screen.blit(self.font.render(f"FPS: {fps:.0f}", True, WHITE), (10, 10))

        screen.blit(self.font.render(f"Money: {self.player.money}$", True, WHITE), (160, 10))

        screen.blit(self.font.render(f"Location: {self.player.location}", True, WHITE), (310, 10))