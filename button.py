import pygame
import rpath
class Button:
    def __init__(self,sf_game):
        self.screen = sf_game.screen
        self.screen_rect = self.screen.get_rect()
        self.width, self.height = 192, 74
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.centerx = self.screen_rect.centerx
        self.rect.centery = self.screen_rect.centery
        self.image = pygame.image.load(rpath.rpath("assets/images/button/play.png")).convert_alpha()


    def draw_button(self):
        self.screen.blit(self.image, self.rect)
