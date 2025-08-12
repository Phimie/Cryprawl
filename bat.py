import pygame
import random
import rpath
import math
from pygame.math import Vector2

class Bat:
    # 状态常量
    STATE_MOVING = 'moving'
    STATE_HIT = 'hit'
    STATE_DYING = 'dying'
    
    def __init__(self, sf_game):
        self.screen = sf_game.screen
        self.settings = sf_game.settings
        self.sf_game = sf_game
        self.screen_rect = sf_game.screen.get_rect()

        # 加载image
        self.frames_move = []
        self.frames_hitted = []
        self.frames_death = []
        for i in range(1, 5):
            self.frames_move.append(pygame.transform.smoothscale(pygame.image.load(rpath.rpath(f'assets/images/bat/{i}.png')).convert_alpha(), (64, 64)))
        self.frames_hitted.append(pygame.transform.smoothscale(pygame.image.load(rpath.rpath('assets/images/bat/hitted.png')).convert_alpha(), (64, 64)))
        for i in range(1, 11):
            self.frames_death.append(pygame.transform.smoothscale(pygame.image.load(rpath.rpath(f'assets/images/bat/death/{i}.png')).convert_alpha(), (64, 64)))
        self.rect = self.frames_move[0].get_rect()

        # spawn
        self.spawn_xy = random.choice([
            [self.screen_rect.centerx + 350, self.screen_rect.centery + 350],
            [self.screen_rect.centerx - 350, self.screen_rect.centery + 350],
            [self.screen_rect.centerx + 350, self.screen_rect.centery - 350],
            [self.screen_rect.centerx - 350, self.screen_rect.centery - 350]
        ])
        self.rect.x = self.spawn_xy[0]
        self.rect.y = self.spawn_xy[1]
        
        # move
        self.speed = 200.0
        self.max_speed = 250.0
        self.acceleration = 5.0
        self.deceleration = 0.8
        
        self.vx = 0.0
        self.vy = 0.0

        # hp
        self.hp = 78
        self.max_hp = self.hp

        # state
        self.state = self.STATE_MOVING
        self.hit_duration = 0.0

        # knockback
        self.knockback_strength = 500.0
        self.knockback_velocity = Vector2(0, 0)

        # image
        self.image = self.frames_move[0]
        self.last_update = pygame.time.get_ticks()
        self.animation_interval = 100
        self.current_frame = 0

    def apply_knockback(self, direction):
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = Vector2(0, -1)
        
        self.knockback_velocity = direction * self.knockback_strength
        self.state = self.STATE_HIT
        self.hit_duration = 0.15
        
        self.vx = 0
        self.vy = 0

    def update_knockback_movement(self, dt):
        # 获取当前边界
        left_bound = self.sf_game.screen_rect.centerx - 390
        right_bound = self.sf_game.screen_rect.centerx + 390
        top_bound = self.sf_game.screen_rect.centery - 400
        bottom_bound = self.sf_game.screen_rect.centery + 380
        
        # 保存原始位置用于碰撞后回退
        original_x = self.rect.x
        original_y = self.rect.y
        
        # 应用击退速度
        self.rect.x += self.knockback_velocity.x * dt
        self.rect.y += self.knockback_velocity.y * dt
        
        bounced = False
        
        # 边界碰撞检测
        if self.rect.left < left_bound:
            self.rect.x = original_x
            self.rect.left = left_bound
            bounced = True
        if self.rect.right > right_bound:
            self.rect.x = original_x
            self.rect.right = right_bound
            bounced = True
        if self.rect.top < top_bound:
            self.rect.y = original_y
            self.rect.top = top_bound
            bounced = True
        if self.rect.bottom > bottom_bound:
            self.rect.y = original_y
            self.rect.bottom = bottom_bound
            bounced = True
        
        # 碰撞反弹
        if bounced:
            if self.rect.left < left_bound or self.rect.right > right_bound:
                self.knockback_velocity.x *= -0.5
            if self.rect.top < top_bound or self.rect.bottom > bottom_bound:
                self.knockback_velocity.y *= -0.5
            
            self.hit_duration = 0.1
        
        # 击退速度衰减
        self.knockback_velocity *= 0.85

    def update_normal_movement(self, dt):
        # 获取当前边界
        left_bound = self.sf_game.screen_rect.centerx - 390
        right_bound = self.sf_game.screen_rect.centerx + 390
        top_bound = self.sf_game.screen_rect.centery - 400
        bottom_bound = self.sf_game.screen_rect.centery + 380
        
        # 目标位置
        target_x, target_y = float(self.sf_game.ship.player_pos[0]), float(self.sf_game.ship.player_pos[1])
        dx = target_x - self.rect.x
        dy = target_y - self.rect.y
        length = max(1.0, math.sqrt(dx*dx + dy*dy))
        
        # 计算目标速度
        target_vx = dx / length * self.speed
        target_vy = dy / length * self.speed
        
        # 加速/减速
        if self.vx < target_vx:
            self.vx = min(self.vx + self.acceleration, target_vx)
        elif self.vx > target_vx:
            self.vx = max(self.vx - self.deceleration, target_vx)
        
        if self.vy < target_vy:
            self.vy = min(self.vy + self.acceleration, target_vy)
        elif self.vy > target_vy:
            self.vy = max(self.vy - self.deceleration, target_vy)
        
        # 速度限制
        current_speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
        if current_speed > self.max_speed:
            scale = self.max_speed / current_speed
            self.vx *= scale
            self.vy *= scale
        
        # 应用速度
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt
        
        bounced = False
        
        # 边界碰撞检测
        if self.rect.left < left_bound:
            self.rect.left = left_bound
            self.vx = abs(self.vx)
            bounced = True
        
        if self.rect.right > right_bound:
            self.rect.right = right_bound
            self.vx = -abs(self.vx)
            bounced = True
        
        if self.rect.top < top_bound:
            self.rect.top = top_bound
            self.vy = abs(self.vy)
            bounced = True
        
        if self.rect.bottom > bottom_bound:
            self.rect.bottom = bottom_bound
            self.vy = -abs(self.vy)
            bounced = True
        
        # 碰撞后随机改变速度方向
        if bounced:
            self.vx = self.vx * random.uniform(0.8, 1.2)
            self.vy = self.vy * random.uniform(0.8, 1.2)

    def update_animation(self, dt):
        now = pygame.time.get_ticks()
        
        if now - self.last_update > self.animation_interval:
            self.last_update = now
            
            if self.state == self.STATE_DYING:
                self.current_frame = (self.current_frame + 1) % len(self.frames_death)
                self.image = self.frames_death[self.current_frame]
            elif self.state == self.STATE_HIT:
                self.image = self.frames_hitted[0]
            else:
                self.current_frame = (self.current_frame + 1) % len(self.frames_move)
                self.image = self.frames_move[self.current_frame]

    def update(self, dt):
        now = pygame.time.get_ticks()

        # 死亡状态处理
        if self.state == self.STATE_DYING:
            if self.death_start_time == 0:
                self.death_start_time = now
            
            if now - self.death_start_time >= 400:
                self.sf_game.dead_bats.append(self)
                self.sf_game.bats.remove(self)
            return
        
        # 击退状态处理
        if self.state == self.STATE_HIT:
            self.hit_duration -= dt
            if self.hit_duration <= 0:
                self.state = self.STATE_MOVING
                self.knockback_velocity = Vector2(0, 0)
                self.vx = 0
                self.vy = 0
        
        # 根据状态更新移动
        if self.state == self.STATE_HIT:
            self.update_knockback_movement(dt)
        elif self.state == self.STATE_MOVING:
            self.update_normal_movement(dt)
        
        # 更新动画
        self.update_animation(dt)
        
        self.rect.x = round(self.rect.x)
        self.rect.y = round(self.rect.y)

    def take_damage(self, damage, direction):
        self.hp -= damage
        self.apply_knockback(direction)
        
        if self.hp <= 0:
            self.state = self.STATE_DYING
            self.death_start_time = pygame.time.get_ticks()