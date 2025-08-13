# Batmage.py
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

        base_rect = self.frames_await[0].get_rect()
        self.rect  = base_rect.inflate(-200, -100)

        self.spawn_xy = random.choice([
            [self.screen_rect.centerx + 100, self.screen_rect.centery + 200],
            [self.screen_rect.centerx - 100, self.screen_rect.centery + 200]
        ])
        self.rect.centerx = self.spawn_xy[0]
        self.rect.centery = self.spawn_xy[1]

        self.target_x, self.target_y = random.choice([
            [self.screen_rect.centerx + 390, self.screen_rect.centery + 400],
            [self.screen_rect.centerx - 500, self.screen_rect.centery + 400],
            [self.screen_rect.centerx + 390, self.screen_rect.centery - 430],
            [self.screen_rect.centerx - 500, self.screen_rect.centery - 430]
        ])

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

        # 边界
        self.left_bound   = 0
        self.right_bound  = self.screen_rect.width
        self.top_bound    = 0
        self.bottom_bound = self.screen_rect.height

    def _update_rect_inflate(self, dx, dy):
        new_rect = self.image.get_rect().inflate(dx, dy)
        new_rect.center = self.rect.center
        self.rect = new_rect

    def _update_target(self):
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
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = Vector2(0, -1)
        self.knockback_velocity = direction * self.knockback_strength
        self.state = self.STATE_HIT
        self.hit_duration = self.knockback_duration
        self.vx = self.vy = 0.0

    def update_movement(self, dt):
        original_x, original_y = self.rect.x, self.rect.y

        if self.state == self.STATE_HIT:
            self.rect.x += self.knockback_velocity.x * dt
            self.rect.y += self.knockback_velocity.y * dt
            bounced = False
            if self.rect.left < self.left_bound:
                self.rect.left = self.left_bound; bounced = True
            if self.rect.right > self.right_bound:
                self.rect.right = self.right_bound; bounced = True
            if self.rect.top < self.top_bound:
                self.rect.top = self.top_bound; bounced = True
            if self.rect.bottom > self.bottom_bound:
                self.rect.bottom = self.bottom_bound; bounced = True
            if bounced:
                if self.rect.left < self.left_bound or self.rect.right > self.right_bound:
                    self.knockback_velocity.x *= -0.5
                if self.rect.top < self.top_bound or self.rect.bottom > self.bottom_bound:
                    self.knockback_velocity.y *= -0.5
            self.knockback_velocity *= 0.85
            return

        if self.state == self.STATE_MOVING:
            dx = self.target_x - self.rect.x
            dy = self.target_y - self.rect.y
            length = max(1.0, math.sqrt(dx*dx + dy*dy))
            if length > 0:
                self.vx = dx / length * self.speed
                self.vy = dy / length * self.speed
                self.rect.x += self.vx * dt
                self.rect.y += self.vy * dt
            bounced = False
            if self.rect.left < self.left_bound:
                self.rect.left = self.left_bound; bounced = True
            if self.rect.right > self.right_bound:
                self.rect.right = self.right_bound; bounced = True
            if self.rect.top < self.top_bound:
                self.rect.top = self.top_bound; bounced = True
            if self.rect.bottom > self.bottom_bound:
                self.rect.bottom = self.bottom_bound; bounced = True
            if bounced:
                if self.rect.left < self.left_bound or self.rect.right > self.right_bound:
                    self.vx *= -1
                if self.rect.top < self.top_bound or self.rect.bottom > self.bottom_bound:
                    self.vy *= -1
            if length <= self.speed:
                self.state = self.STATE_AWAITING
                self.await_start_time = pygame.time.get_ticks()
                self._summon_bat()

    def update_animation(self, dt):
        self.animation_timer += dt * 1000

        if self.state == self.STATE_DYING:
            if self.death_start_time == 0:
                self.death_start_time = pygame.time.get_ticks()
            elapsed = pygame.time.get_ticks() - self.death_start_time
            idx = min(8, int(elapsed // 50))
            if idx < len(self.frames_death):
                self.image = self.frames_death[idx]
            self._update_rect_inflate(-200, -100)
            return

        if self.state == self.STATE_HIT:
            if not hasattr(self, 'hit_start_time'):
                self.hit_start_time = pygame.time.get_ticks()
            elapsed = pygame.time.get_ticks() - self.hit_start_time
            if elapsed <= 150:
                idx = min(4, int(elapsed // 50))
                if idx < len(self.frames_hitted):
                    self.image = self.frames_hitted[idx]
            self._update_rect_inflate(-200, -100)
            return

        if self.state == self.STATE_SUMMONING:
            elapsed = pygame.time.get_ticks() - self.summon_start_time - 600
            idx = min(12, int(elapsed // 85))
            if idx < len(self.frames_summon):
                self.image = self.frames_summon[idx]
            self._update_rect_inflate(-200, -100)
            return

        if self.state == self.STATE_MOVING:
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames_move)
                self.image = self.frames_move[self.current_frame]
            self._update_rect_inflate(-200, -100)
            return

        if self.state == self.STATE_AWAITING:
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames_await)
                self.image = self.frames_await[self.current_frame]
            self._update_rect_inflate(-200, -100)

    def update(self, dt):
        now = pygame.time.get_ticks()

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

        if self.state == self.STATE_HIT:
            self.hit_duration -= dt
            if self.hit_duration <= 0:
                self.state = getattr(self, 'state_before_hit', self.STATE_AWAITING)
                self.knockback_velocity = Vector2(0, 0)
                if hasattr(self, 'hit_start_time'):
                    del self.hit_start_time

        if self.state == self.STATE_SUMMONING:
            elapsed = (now - self.summon_start_time) / 1000.0
            if elapsed >= self.summon_duration:
                self.state = self.STATE_AWAITING
                self.await_start_time = now

        if self.state == self.STATE_AWAITING:
            elapsed = (now - self.await_start_time) / 1000.0
            if elapsed >= self.await_duration:
                self.state = self.STATE_MOVING
                self._update_target()

        self.update_movement(dt)
        self.update_animation(dt)
        self.rect.x = round(self.rect.x)
        self.rect.y = round(self.rect.y)

    def take_damage(self, damage, direction):
        self.hp -= damage
        if self.state != self.STATE_HIT:
            self.state_before_hit = self.state
        self.hit_start_time = pygame.time.get_ticks()
        self.apply_knockback(direction)
        if self.hp <= 0:
            self.state = self.STATE_DYING
            self.death_start_time = pygame.time.get_ticks()