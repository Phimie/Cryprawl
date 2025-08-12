import pygame
import random
import rpath
import math
from pygame.math import Vector2

class Enemy:
    STATE_IDLE = 'idle'
    STATE_MOVING = 'moving'
    STATE_HIT = 'hit'
    STATE_DYING = 'dying'
    
    def __init__(self, sf_game):
        self.screen = sf_game.screen
        self.settings = sf_game.settings
        self.screen_rect = sf_game.screen.get_rect()
        
        self.frames = []
        for i in range(8):
            self.frames.append(pygame.image.load(rpath.rpath(f'assets/images/enemy/Sprite-000{i}.png')).convert_alpha())
        self.image = self.frames[0]
        
        self.rect = self.image.get_rect()
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        
        self.max_speed = random.choice([100.0,200.0,220.0,110.0,120.0,130.0,140.0,150.0,160.0,170.0,180.0,190.0,210.0,230.0,240.0,250.0])
        
        self.acceleration = 5.0
        
        self.direction_change_timer = 0
        self.direction_change_interval = random.randint(1000, 3000)
        # 边界定义
        self.left_bound = self.screen_rect.centerx - 390
        self.right_bound = self.screen_rect.centerx + 390
        self.top_bound = self.screen_rect.centery - 400
        self.bottom_bound = self.screen_rect.centery + 380
        
        safe_spawn_options = [
            [random.uniform(self.left_bound + 50, self.right_bound - 50), self.top_bound + 50],
            [random.uniform(self.left_bound + 50, self.right_bound - 50), self.bottom_bound - 50],
            [self.left_bound + 50, random.uniform(self.top_bound + 50, self.bottom_bound - 50)],
            [self.right_bound - 50, random.uniform(self.top_bound + 50, self.bottom_bound - 50)]
        ]
        
        self.position = Vector2(*random.choice(safe_spawn_options))
        self.rect.center = self.position
        
        self.enemy_hp = 100
        self.max_hp = self.enemy_hp
        
        self.state = self.STATE_MOVING
        self.hit_duration = 0.0
        
        self.knockback_strength = 500.0
        self.knockback_decay = 0.95
        self.knockback_velocity = Vector2(0, 0)
        
        self.death_frames = []
        for i in range(1, 11):
            self.death_frames.append(pygame.image.load(rpath.rpath(f'assets/images/enemy/death/{i}.png')).convert_alpha())
        self.death_start_time = 0
        self.death_duration = 400
        
        self.animation_timer = 0
        self.animation_speed = 100
        self.current_frame = 0
        
        self.hitted_image = pygame.image.load(rpath.rpath('assets/images/enemy/hitted.png')).convert_alpha()
        
        self.update_direction(force=True)

    def update_direction(self, force=False):
        now = pygame.time.get_ticks()
        if force or now - self.direction_change_timer > self.direction_change_interval:
            self.direction_change_timer = now
            self.direction_change_interval = random.randint(1000, 3000)
            
            angle = random.uniform(0, 2 * math.pi)
            target_velocity = Vector2(math.cos(angle), math.sin(angle)) * self.max_speed
            
            self.velocity = target_velocity
            return True
        return False

    def apply_knockback(self, direction):
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = Vector2(0, -1)
        
        self.knockback_velocity = direction * self.knockback_strength
        self.state = self.STATE_HIT
        self.hit_duration = 0.15
        
        self.velocity = Vector2(0, 0)

    def update_movement(self, dt):
        if self.state == self.STATE_HIT:
            self.position += self.knockback_velocity * dt
            self.rect.center = self.position
            
            bounced = False
            
            if self.rect.left < self.left_bound:
                self.rect.left = self.left_bound
                bounced = True
            if self.rect.right > self.right_bound:
                self.rect.right = self.right_bound
                bounced = True
            if self.rect.top < self.top_bound:
                self.rect.top = self.top_bound
                bounced = True
            if self.rect.bottom > self.bottom_bound:
                self.rect.bottom = self.bottom_bound
                bounced = True
            
            if bounced:
                if self.rect.left < self.left_bound or self.rect.right > self.right_bound:
                    self.knockback_velocity.x *= -0.5
                if self.rect.top < self.top_bound or self.rect.bottom > self.bottom_bound:
                    self.knockback_velocity.y *= -0.5
            
            self.knockback_velocity *= self.knockback_decay
            
            return
        
        if self.state == self.STATE_MOVING:
            self.position += self.velocity * dt
            self.rect.center = self.position
            
            bounced = False
            
            if self.rect.left < self.left_bound:
                self.rect.left = self.left_bound
                self.position.x = self.rect.centerx
                self.velocity.x = abs(self.velocity.x)
                bounced = True
            
            if self.rect.right > self.right_bound:
                self.rect.right = self.right_bound
                self.position.x = self.rect.centerx
                self.velocity.x = -abs(self.velocity.x)
                bounced = True
            
            if self.rect.top < self.top_bound:
                self.rect.top = self.top_bound
                self.position.y = self.rect.centery
                self.velocity.y = abs(self.velocity.y)
                bounced = True
            
            if self.rect.bottom > self.bottom_bound:
                self.rect.bottom = self.bottom_bound
                self.position.y = self.rect.centery
                self.velocity.y = -abs(self.velocity.y)
                bounced = True
            
            if bounced:
                self.velocity = self.velocity.rotate(random.uniform(-30, 30))

    def update_animation(self, dt):
        self.animation_timer += dt * 1000
        
        if self.state == self.STATE_DYING:
            if self.death_start_time == 0:
                self.death_start_time = pygame.time.get_ticks()
            
            elapsed = pygame.time.get_ticks() - self.death_start_time
            frame_index = min(9, int(elapsed / (self.death_duration / 10)))
            self.image = self.death_frames[frame_index]
            return
        
        if self.state == self.STATE_HIT:
            self.image = self.hitted_image
            return
        
        if self.state == self.STATE_MOVING:
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

    def update(self, dt):
        if self.state == self.STATE_HIT:
            self.hit_duration -= dt
            if self.hit_duration <= 0:
                self.state = self.STATE_MOVING
                self.knockback_velocity = Vector2(0, 0)
                self.update_direction(force=True)
        
        if self.state == self.STATE_DYING:
            return
        
        if not self.state == self.STATE_HIT:
            self.update_direction()
        
        self.update_movement(dt)
        
        self.update_animation(dt)

    def take_damage(self, damage, direction):
        self.enemy_hp -= damage
        self.apply_knockback(direction)
        
        if self.enemy_hp <= 0:
            self.state = self.STATE_DYING
            self.death_start_time = pygame.time.get_ticks()