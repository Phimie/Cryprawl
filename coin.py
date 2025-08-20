import pygame
import rpath

class Coin:
    def __init__(self, cr_game):
        self.screen = cr_game.screen
        self.settings = cr_game.settings
        self.screen_rect = cr_game.screen.get_rect()
        self.frames = []
        for i in range(7):
            self.frames.append(pygame.image.load(rpath.rpath(f'assets/images/coin{i}.png')).convert_alpha())
        self.image = self.frames[0]
        self.rect = self.image.get_rect()

        # 动画加载相关
        self.animation_timer = 0
        self.animation_speed = 100
        self.current_frame = 0

    def update_animation (self, dt):
        self.animation_timer += dt * 1000
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def update(self, dt):
        self.update_animation(dt)

