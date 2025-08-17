import pygame
import random
import rpath
import math
from pygame.math import Vector2

class EnemyBase:
    # 状态常量
    _BASE_STATES = {
        'IDLE' : 0,
        'WALK' : 1,
        'ATTACK' : 2,
        'DEAD' : 3,
    }

    def __init__(self, cr_game):
        self.screen = cr_game.screen
        self.settings = cr_game.settings
        self.cr_game = cr_game
        self.screen_rect = cr_game.screen.get_rect()

        