import pygame
import rpath
import math
from pygame.sprite import Sprite

class Bullet(Sprite):
    def __init__(self, cr_game, target_pos):
        super().__init__()
        self.screen   = cr_game.screen
        self.settings = cr_game.settings
        self.damage   = 51
        self.origin_image = pygame.image.load(
            rpath.rpath("assets/images/bullets/bullet.png")
        ).convert_alpha()

        start_x = float(cr_game.ship.rect.centerx)
        start_y = float(cr_game.ship.rect.centery)
        target_x = float(target_pos[0])
        target_y = float(target_pos[1])
        dx = target_x - start_x
        dy = target_y - start_y
        length = max(1.0, (dx * dx + dy * dy) ** 0.5)
        bullet_speed = float(self.settings.bullet_speed)
        self.vx = (dx / length) * bullet_speed
        self.vy = (dy / length) * bullet_speed

        angle = (math.atan2(-dx, -dy)) * 180 / math.pi
        self.image = pygame.transform.rotozoom(self.origin_image, angle, 1)

        self.rect = self.image.get_rect(center=(int(round(start_x)), int(round(start_y))))

        self.x = start_x
        self.y = start_y

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (int(round(self.x)), int(round(self.y)))
        if (self.rect.bottom < 0 or self.rect.top > self.screen.get_height() or 
            self.rect.right < 0 or self.rect.left > self.screen.get_width()):
            self.kill()