import pygame
import random
import rpath
import math
from pygame.math import Vector2

class Batmage:
    STATE_AWAITING  = 'awaiting'
    STATE_MOVING    = 'moving'
    STATE_SUMMONING = 'summoning'
    STATE_HIT       = 'hit'
    STATE_DYING     = 'dying'

    def __init__(self, sf_game):
        self.screen      = sf_game.screen
        self.screen_rect = sf_game.screen.get_rect()
        self.settings    = sf_game.settings
        self.sf_game     = sf_game

        # 加载并缩放动画帧
        self.frames_await  = [pygame.transform.smoothscale(
            pygame.image.load(rpath.rpath(f'assets/images/batmage/batmage{i}.png')).convert_alpha(),
            (400, 320)) for i in range(8)]
        self.frames_move   = [pygame.transform.smoothscale(
            pygame.image.load(rpath.rpath(f'assets/images/batmage/batmage{i}.png')).convert_alpha(),
            (400, 320)) for i in range(17, 25)]
        self.frames_summon = [pygame.transform.smoothscale(
            pygame.image.load(rpath.rpath(f'assets/images/batmage/batmage{i}.png')).convert_alpha(),
            (400, 320)) for i in range(34, 47)]
        self.frames_hitted = [pygame.transform.smoothscale(
            pygame.image.load(rpath.rpath(f'assets/images/batmage/batmage{i}.png')).convert_alpha(),
            (400, 320)) for i in range(86, 90)]
        self.frames_death  = [pygame.transform.smoothscale(
            pygame.image.load(rpath.rpath(f'assets/images/batmage/batmage{i}.png')).convert_alpha(),
            (400, 320)) for i in range(102, 111)]
        
        # 初始化精灵矩形
        self.rect = self.frames_await[0].get_rect()
        
        # 随机选择出生点
        self.spawn_xy = random.choice([
            [self.screen_rect.centerx + 100, self.screen_rect.centery + 200],
            [self.screen_rect.centerx - 100, self.screen_rect.centery + 200]
        ])
        self.rect.center = self.spawn_xy

        # 加载碰撞箱图片并缩放
        self.hitbox_img = pygame.image.load(rpath.rpath(f'assets/images/batmage/hitbox.png')).convert_alpha()
        self.hitbox_scale = 1  # 碰撞箱缩放比例
        self.hitbox_img = pygame.transform.smoothscale(
            self.hitbox_img,
            (int(self.hitbox_img.get_width() * self.hitbox_scale),
             int(self.hitbox_img.get_height() * self.hitbox_scale))
        )
        self.hitbox_rect = self.hitbox_img.get_rect()
        self.hitbox_rect.centerx = self.rect.centerx
        self.hitbox_rect.centery = self.rect.centery + 60

        # 随机选择目标位置 
        self.target_x, self.target_y = random.choice([
            [self.screen_rect.centerx + 390, self.screen_rect.centery + 400],
            [self.screen_rect.centerx - 500, self.screen_rect.centery + 400],
            [self.screen_rect.centerx + 390, self.screen_rect.centery - 430],
            [self.screen_rect.centerx - 500, self.screen_rect.centery - 430]
        ])

        # 状态和属性
        self.speed  = 300.0
        self.vx = self.vy = 0.0
        self.hp = 2000
        self.state = self.STATE_MOVING
        self.hit_duration = 0.0
        self.knockback_strength = 500.0
        self.knockback_duration = 0.2
        self.knockback_velocity = Vector2(0, 0)
        self.death_start_time = 0
        self.summon_start_time = 0
        self.summon_duration = 1.5
        self.update_target_tick = pygame.time.get_ticks()
        self.summon_cooldown_tick = pygame.time.get_ticks()
        self.await_start_time = 0
        self.await_duration = 5.0

        # 动画
        self.image = self.frames_await[0]
        self.animation_timer = 0
        self.animation_speed = 100
        self.current_frame = 0

        # 边界设置（基于碰撞箱大小）
        self.left_bound   = self.hitbox_rect.width // 2
        self.right_bound  = self.screen_rect.width - self.hitbox_rect.width // 2
        self.top_bound    = self.hitbox_rect.height // 2
        self.bottom_bound = self.screen_rect.height - self.hitbox_rect.height // 2

    def _update_target(self):
        """更新移动目标位置"""
        now = pygame.time.get_ticks()
        if now - self.update_target_tick >= 8000:
            self.target_x, self.target_y = random.choice([
                [self.screen_rect.centerx + 390, self.screen_rect.centery + 300],
                [self.screen_rect.centerx - 490, self.screen_rect.centery + 300],
                [self.screen_rect.centerx + 390, self.screen_rect.centery - 430],
                [self.screen_rect.centerx - 490, self.screen_rect.centery - 430]
            ])
            self.update_target_tick = now

    def _summon_bat(self):
        """召唤蝙蝠"""
        now = pygame.time.get_ticks()
        if now - self.summon_cooldown_tick >= 3000 and self.state != self.STATE_DYING:
            self.state = self.STATE_SUMMONING
            self.summon_start_time = now
            self.sf_game.Batmage_is_summoning = True
            for _ in range(8):
                self.sf_game.create_bat()
            self.sf_game.Batmage_is_summoning = False
            self.summon_cooldown_tick = now

    def apply_knockback(self, direction):
        """应用击退效果"""
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = Vector2(0, -1)  # 默认向上击退
        
        self.knockback_velocity = direction * self.knockback_strength
        self.state = self.STATE_HIT
        self.hit_duration = self.knockback_duration
        self.vx = self.vy = 0.0
        # 重置状态标记
        if hasattr(self, 'state_before_hit'):
            del self.state_before_hit

    def update_movement(self, dt):
        """更新移动逻辑"""
        if self.state == self.STATE_HIT:
            # 击退状态
            self.rect.x += self.knockback_velocity.x * dt
            self.rect.y += self.knockback_velocity.y * dt
            bounced = False
            
            # 边界检查（使用碰撞箱尺寸）
            if self.rect.centerx - self.hitbox_rect.width/2 < 0:
                self.rect.centerx = self.hitbox_rect.width/2
                bounced = True
            if self.rect.centerx + self.hitbox_rect.width/2 > self.screen_rect.width:
                self.rect.centerx = self.screen_rect.width - self.hitbox_rect.width/2
                bounced = True
            if self.rect.centery - self.hitbox_rect.height/2 < 0:
                self.rect.centery = self.hitbox_rect.height/2
                bounced = True
            if self.rect.centery + self.hitbox_rect.height/2 > self.screen_rect.height:
                self.rect.centery = self.screen_rect.height - self.hitbox_rect.height/2
                bounced = True
            
            # 反弹效果
            if bounced:
                if self.rect.centerx <= self.hitbox_rect.width/2 or self.rect.centerx >= self.screen_rect.width - self.hitbox_rect.width/2:
                    self.knockback_velocity.x *= -0.5
                if self.rect.centery <= self.hitbox_rect.height/2 or self.rect.centery >= self.screen_rect.height - self.hitbox_rect.height/2:
                    self.knockback_velocity.y *= -0.5
            
            # 阻尼效果
            self.knockback_velocity *= 0.85
            return

        if self.state == self.STATE_MOVING:
            # 移动到目标位置
            dx = self.target_x - self.rect.x
            dy = self.target_y - self.rect.y
            length = max(1.0, math.sqrt(dx*dx + dy*dy))
            
            if length > 0:
                # 计算速度分量
                self.vx = dx / length * self.speed
                self.vy = dy / length * self.speed
                
                # 应用移动
                self.rect.x += self.vx * dt
                self.rect.y += self.vy * dt
            
            bounced = False
            
            # 边界检查（使用碰撞箱尺寸）
            if self.rect.centerx - self.hitbox_rect.width/2 < 0:
                self.rect.centerx = self.hitbox_rect.width/2
                bounced = True
            if self.rect.centerx + self.hitbox_rect.width/2 > self.screen_rect.width:
                self.rect.centerx = self.screen_rect.width - self.hitbox_rect.width/2
                bounced = True
            if self.rect.centery - self.hitbox_rect.height/2 < 0:
                self.rect.centery = self.hitbox_rect.height/2
                bounced = True
            if self.rect.centery + self.hitbox_rect.height/2 > self.screen_rect.height:
                self.rect.centery = self.screen_rect.height - self.hitbox_rect.height/2
                bounced = True
            
            # 碰到边界时反弹
            if bounced:
                if self.rect.centerx <= self.hitbox_rect.width/2 or self.rect.centerx >= self.screen_rect.width - self.hitbox_rect.width/2:
                    self.vx *= -1
                if self.rect.centery <= self.hitbox_rect.height/2 or self.rect.centery >= self.screen_rect.height - self.hitbox_rect.height/2:
                    self.vy *= -1
            
            # 到达目标位置
            if length <= self.speed:
                self.state = self.STATE_AWAITING
                self.await_start_time = pygame.time.get_ticks()
                self._summon_bat()

    def update_animation(self, dt):
        """更新动画状态"""
        self.animation_timer += dt * 1000

        if self.state == self.STATE_DYING:
            # 死亡动画
            if self.death_start_time == 0:
                self.death_start_time = pygame.time.get_ticks()
            elapsed = pygame.time.get_ticks() - self.death_start_time
            idx = min(8, int(elapsed // 50))
            if idx < len(self.frames_death):
                self.image = self.frames_death[idx]
            return

        if self.state == self.STATE_HIT:
            # 被击中动画
            if not hasattr(self, 'hit_start_time'):
                self.hit_start_time = pygame.time.get_ticks()
            elapsed = pygame.time.get_ticks() - self.hit_start_time
            if elapsed <= 150:
                idx = min(4, int(elapsed // 50))
                if idx < len(self.frames_hitted):
                    self.image = self.frames_hitted[idx]
            return

        if self.state == self.STATE_SUMMONING:
            # 召唤动画
            elapsed = pygame.time.get_ticks() - self.summon_start_time - 600
            idx = min(12, int(elapsed // 85))
            if idx < len(self.frames_summon):
                self.image = self.frames_summon[idx]
            return

        if self.state == self.STATE_MOVING:
            # 移动动画
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames_move)
                self.image = self.frames_move[self.current_frame]
            return

        if self.state == self.STATE_AWAITING:
            # 待机动画
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames_await)
                self.image = self.frames_await[self.current_frame]

    def update(self, dt):
        """更新蝙蝠法师状态"""
        now = pygame.time.get_ticks()

        # 死亡状态处理
        if self.state == self.STATE_DYING:
            if self.death_start_time == 0:
                self.death_start_time = now
            elapsed = now - self.death_start_time
            idx = min(8, int(elapsed // 50))
            if idx < len(self.frames_death):
                self.image = self.frames_death[idx]
            if elapsed >= 400:
                self.sf_game.dead_batmages.append(self)
                if self in self.sf_game.batmages:
                    self.sf_game.batmages.remove(self)
            return

        # 被击中状态处理
        if self.state == self.STATE_HIT:
            self.hit_duration -= dt
            if self.hit_duration <= 0:
                # 恢复之前的活动状态
                self.state = getattr(self, 'state_before_hit', self.STATE_AWAITING)
                self.knockback_velocity = Vector2(0, 0)
                if hasattr(self, 'hit_start_time'):
                    del self.hit_start_time

        # 召唤状态处理
        if self.state == self.STATE_SUMMONING:
            elapsed = (now - self.summon_start_time) / 1000.0
            if elapsed >= self.summon_duration:
                self.state = self.STATE_AWAITING
                self.await_start_time = now

        # 待机状态处理
        if self.state == self.STATE_AWAITING:
            elapsed = (now - self.await_start_time) / 1000.0
            if elapsed >= self.await_duration:
                self.state = self.STATE_MOVING
                self._update_target()

        # 更新移动和动画
        self.update_movement(dt)
        self.update_animation(dt)
        
        # 四舍五入位置以消除浮点精度问题
        self.rect.x = round(self.rect.x)
        self.rect.y = round(self.rect.y)
        
        # 同步碰撞箱位置
        self.hitbox_rect.centerx = self.rect.centerx
        self.hitbox_rect.centery = self.rect.centery + 60

    def take_damage(self, damage, direction):
        """受到伤害"""
        self.hp -= damage
        
        # 如果不是被击中状态，保存当前状态
        if self.state != self.STATE_HIT:
            self.state_before_hit = self.state
            
        # 设置被击中状态
        self.hit_start_time = pygame.time.get_ticks()
        self.apply_knockback(direction)
        
        # 检查是否死亡
        if self.hp <= 0:
            self.state = self.STATE_DYING
            self.death_start_time = pygame.time.get_ticks()