import pygame
from settings import GAME_WIDTH, GAME_HEIGHT
from settings import BLUE
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, name, money):
        pygame.sprite.Sprite.__init__(self)
        self.size = 50
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.name = name
        self.money = money
        self.speed = 100
        self.location = "street"
    
    def handleMovement(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.pos.y > 0:
            self.pos.y -= dt * self.speed
        if keys[pygame.K_s] and self.pos.y < GAME_HEIGHT - self.size:
            self.pos.y += dt * self.speed
        if keys[pygame.K_a] and self.pos.x > 0:
            self.pos.x -= dt * self.speed
        if keys[pygame.K_d] and self.pos.x < GAME_WIDTH - self.size:
            self.pos.x += dt * self.speed

    def update(self, dt):
        self.handleMovement(dt)

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)
    
    def drawDebug(self, screen):
        screen.blit(pygame.font.SysFont("Arial", 12).render(f"{self.pos} ${self.rect}", True, (0, 0, 0)), (self.pos.x - 25, self.pos.y - 25))
