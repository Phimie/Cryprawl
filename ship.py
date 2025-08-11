import pygame
import rpath
import math
from pygame.math import Vector2

class Ship:
    STATE_NORMAL = 'normal'
    STATE_HIT = 'hit'
    STATE_DYING = 'dying'
    
    def __init__(self, sf_game):
        self.screen = sf_game.screen
        self.settings = sf_game.settings
        self.screen_rect = sf_game.screen.get_rect()
        
        self.frames = []
        for i in range(8):
            self.frames.append(pygame.image.load(rpath.rpath(f'assets/images/ship/Sprite-000{i}.png')).convert_alpha())
        self.image = self.frames[0]
        
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.center
        self.position = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, 0)
        self.max_speed = self.settings.ship_speed
        self.acceleration = 5.0
        self.deceleration = 0.8
        
        self.hp = self.settings.ship_hp
        self.MaxHp = self.settings.ship_MaxHp
        
        self.state = self.STATE_NORMAL
        self.hit_duration = 0.0
        
        self.collision_cooldown = 0.0
        self.collision_cooldown_duration = 1.0
        
        self.death_frames = []
        for i in range(1, 11):
            self.death_frames.append(pygame.image.load(rpath.rpath(f'assets/images/ship/death/{i}.png')).convert_alpha())
        self.death_start_time = 0
        
        self.animation_timer = 0
        self.animation_speed = 100
        self.current_frame = 0
        
        self.player_pos = [self.screen_rect.centerx, self.screen_rect.centery]

    def center_ship(self):
        self.rect.midbottom = self.screen_rect.center
        self.position = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, 0)
        self.state = self.STATE_NORMAL
        self.hit_duration = 0.0
        self.collision_cooldown = 0.0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        input_vector = pygame.math.Vector2(0, 0)
        
        if keys[pygame.K_d]:
            input_vector.x += 1
        if keys[pygame.K_a]:
            input_vector.x -= 1
        if keys[pygame.K_w]:
            input_vector.y -= 1
        if keys[pygame.K_s]:
            input_vector.y += 1
        
        if input_vector.length() > 0:
            input_vector = input_vector.normalize()
        
        target_velocity = input_vector * self.max_speed
        self.velocity = self.velocity.lerp(target_velocity, self.acceleration * 0.1)
        
        if input_vector.length() == 0:
            self.velocity = self.velocity.lerp(pygame.math.Vector2(0, 0), self.deceleration)

    def update_movement(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position
        # 边界定义
        left_bound = self.screen_rect.centerx - 310
        right_bound = self.screen_rect.centerx + 290
        top_bound = self.screen_rect.centery - 300
        bottom_bound = self.screen_rect.centery + 330
        
        if self.rect.left < left_bound:
            self.rect.left = left_bound
            self.position.x = self.rect.centerx
            self.velocity.x = 0
        
        if self.rect.right > right_bound:
            self.rect.right = right_bound
            self.position.x = self.rect.centerx
            self.velocity.x = 0
        
        if self.rect.top < top_bound:
            self.rect.top = top_bound
            self.position.y = self.rect.centery
            self.velocity.y = 0
        
        if self.rect.bottom > bottom_bound:
            self.rect.bottom = bottom_bound
            self.position.y = self.rect.centery
            self.velocity.y = 0
        
        self.player_pos = [self.position.x, self.position.y]

    def update_animation(self, dt):
        self.animation_timer += dt * 1000
        
        if self.state == self.STATE_DYING:
            if self.death_start_time == 0:
                self.death_start_time = pygame.time.get_ticks()
            
            elapsed = pygame.time.get_ticks() - self.death_start_time
            frame_index = min(9, int(elapsed // 100))
            self.image = self.death_frames[frame_index]
            return
        
        if self.state == self.STATE_HIT:
            self.image = pygame.image.load(rpath.rpath('assets/images/ship/is_hit.png')).convert_alpha()
            return
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def update(self, dt):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= dt
            if self.state != self.STATE_HIT:
                self.state = self.STATE_HIT
        
        if self.state == self.STATE_HIT:
            if self.collision_cooldown <= 0:
                self.state = self.STATE_NORMAL
        
        if self.state == self.STATE_DYING:
            if self.death_start_time == 0:
                self.death_start_time = pygame.time.get_ticks()
            return
        
        self.handle_input()
        self.update_movement(dt)
        
        self.update_animation(dt)

    def blitme(self):
        self.screen.blit(self.image, self.rect)
    
    def take_damage(self, damage):
        if self.collision_cooldown > 0:
            return
        self.hp -= damage
        if self.hp > 0:
            self.state = self.STATE_HIT
            self.collision_cooldown = self.collision_cooldown_duration
        else:
            self.state = self.STATE_DYING
            self.hp = 0
    
    def is_invulnerable(self):
        return self.collision_cooldown > 0