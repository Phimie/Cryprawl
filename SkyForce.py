import sys
import pygame
import random
import os
import rpath
from time import sleep
from settings import Settings
from ship import Ship
from bullet import Bullet
from enemy import Enemy
from button import Button
from Batmage import Batmage
from bat import Bat
from pygame.math import Vector2

class SkyForce:
    STATE_GAMERUNNING = 'gamerunning'
    STATE_MAINMENU = 'mainmenu'
    STATE_SETTING = 'setting'
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.screen_rect = self.screen.get_rect()
        pygame.event.pump()
        pygame.display.set_allow_screensaver(False)
        pygame.display.set_caption("SkyForce")
        pygame.display.set_icon(pygame.image.load(rpath.rpath("assets/images/icon/SF.ico")).convert_alpha())
        self.bg_img = pygame.image.load(rpath.rpath("assets/images/background/background.png")).convert_alpha()
        self.hp_img = pygame.image.load(rpath.rpath("assets/images/ship/hp.png")).convert_alpha()
        self.hpBar_img = pygame.image.load(rpath.rpath("assets/images/ship/hp_bar.png")).convert_alpha()
        self.setting_ui_img = pygame.image.load(rpath.rpath("assets/images/button/settingUI.png")).convert_alpha()
        
        #游戏状态
        self.game_state = self.STATE_MAINMENU
        # 游戏对象
        self.enemies = []
        self.dead_enemies = []
        self.dead_enemies_count = 0
        self.enough_dead_enemies_count = 40
        
        self.batmages = []
        self.dead_batmages = []
        
        self.bats = []
        self.dead_bats = []
        
        # 玩家飞船
        self.ship = Ship(self)
        
        # 子弹
        self.bullets = pygame.sprite.Group()
        
        # Button相关
        self.play_button = Button(self)
        self.setting_button = Button(self)
        self.setting_button.rect.y = self.screen_rect.centery + 40
        self.setting_button.image = pygame.image.load(rpath.rpath("assets/images/button/setting.png")).convert_alpha()
        self.exit_button = Button(self)
        self.exit_button.rect.y = self.screen_rect.centery + 120
        self.exit_button.image = pygame.image.load(rpath.rpath("assets/images/button/exit.png")).convert_alpha()

        # 游戏数据
        self.game_run_times = 0
        self.score = 0
        self.max_score = 0
        self.all_max_score = 0
        self.bullet_count = self.settings.bullet_count
        self.dying = False

        # 计时器
        self.wait_ship_death_over_tick = 0
        self.wait_enemy_spawn_tick = 0
        self.wait_batmage_spawn_tick = 0
        self.wait_bat_spawn_tick = 0

        # 数字图像
        self.digits = []
        for i in range(10):
            self.digits.append(pygame.image.load(rpath.rpath(f'assets/images/digits/{i}.png')).convert_alpha())
        
        self.bullet_digits = []
        for i in range(10):
            self.bullet_digits.append(pygame.image.load(rpath.rpath(f'assets/images/bullets/bullet_digits/{i}.png')).convert_alpha())
        
        # 音频
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)
        pygame.mixer.music.load(rpath.rpath("assets/audio/background.mp3"))
        pygame.mixer.music.play(loops=-1, fade_ms=1000)
        pygame.mixer.music.set_volume(0.2)
        
        self.snd_hit = pygame.mixer.Sound(rpath.rpath("assets/audio/hit.wav"))
        self.snd_hit.set_volume(0.1)
        
        self.snd_shoot = pygame.mixer.Sound(rpath.rpath("assets/audio/shoot.wav"))
        self.snd_shoot.set_volume(0.1)
        
        self.snd_explode = pygame.mixer.Sound(rpath.rpath("assets/audio/explode.wav"))
        self.snd_explode.set_volume(0.1)
        
        self.snd_score = pygame.mixer.Sound(rpath.rpath("assets/audio/score.wav"))
        self.snd_score.set_volume(0.2)
        
        self.snd_click = pygame.mixer.Sound(rpath.rpath("assets/audio/click.wav"))
        self.snd_click.set_volume(0.6)
        
        self.snd_gameover = pygame.mixer.Sound(rpath.rpath("assets/audio/gameover.wav"))
        self.snd_gameover.set_volume(0.5)
        
        self.explode_channel = pygame.mixer.Channel(0)

    # 事件处理
    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.max_score > self.all_max_score:
                    self.all_max_score = self.max_score
                print(f"最后一局最大分数为: {self.max_score}")
                print(f"历史最高最大分数为: {self.all_max_score}")
                print(f"游戏局数为: {self.game_run_times}")
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.game_state == self.STATE_MAINMENU:
                    self._check_play_button(mouse_pos)
                    self._check_exit_button(mouse_pos)
                    self._check_setting_button(mouse_pos)
                elif self.game_state == self.STATE_GAMERUNNING:
                    self._fire_bullet()
    #Button相关
    def _check_play_button(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        button_rect = self.play_button.rect
        if (button_rect.x <= mouse_x <= button_rect.x + button_rect.width and
            button_rect.y <= mouse_y <= button_rect.y + button_rect.height and
            self.game_state == self.STATE_MAINMENU and not self.dying):
            self.game_state = self.STATE_GAMERUNNING
            self.snd_click.play()
    def _check_setting_button(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        button_rect = self.setting_button.rect
        if (button_rect.x <= mouse_x <= button_rect.x + button_rect.width and
            button_rect.y <= mouse_y <= button_rect.y + button_rect.height and
            self.game_state == self.STATE_MAINMENU and not self.dying):
            self.game_state = self.STATE_SETTING
            self.snd_click.play()
    def _check_exit_button(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        button_rect = self.exit_button.rect
        if (button_rect.x <= mouse_x <= button_rect.x + button_rect.width and
            button_rect.y <= mouse_y <= button_rect.y + button_rect.height and
            self.game_state == self.STATE_MAINMENU and not self.dying):
            self.snd_click.play()
            if self.max_score > self.all_max_score:
                self.all_max_score = self.max_score
            print(f"最后一局最大分数为: {self.max_score}")
            print(f"历史最高最大分数为: {self.all_max_score}")
            print(f"游戏局数为: {self.game_run_times}")
            sys.exit()

    # 子弹相关
    def _fire_bullet(self):
        if self.bullet_count > 0:
            mouse_pos = pygame.mouse.get_pos()
            new_bullet = Bullet(self, mouse_pos)
            self.bullets.add(new_bullet)
            self.bullet_count -= 1
            self.snd_shoot.play(maxtime=0)

    def _update_bullets(self, dt):
        self.bullets.update(dt)
        
        # 子弹碰撞检测
        for bullet in self.bullets.copy():
            # 与敌人碰撞
            for enemy in self.enemies[:]:
                if self._check_collision(bullet, enemy):
                    dx = enemy.rect.centerx - bullet.rect.centerx
                    dy = enemy.rect.centery - bullet.rect.centery
                    direction = pygame.math.Vector2(dx, dy)
                    
                    enemy.take_damage(bullet.damage, direction)
                    
                    if enemy.enemy_hp <= 0:
                        self._handle_enemy_death(bullet, enemy)
                    else:
                        self.bullets.remove(bullet)
                        self.snd_hit.play(maxtime=0)
                    break
            
            # 与batmage碰撞
            for batmage in self.batmages[:]:
                if self._check_collision(bullet, batmage):
                    dx = batmage.rect.centerx - bullet.rect.centerx
                    dy = batmage.rect.centery - bullet.rect.centery
                    direction = pygame.math.Vector2(dx, dy)
                    
                    batmage.take_damage(bullet.damage, direction)
                    if batmage.hp <= 0:
                        self._handle_batmage_death(bullet, batmage)
                    else:
                        self.bullets.remove(bullet)
                        self.snd_hit.play(maxtime=0)
                    break

            # 与蝙蝠碰撞
            for bat in self.bats[:]:
                if self._check_collision(bullet, bat):
                    dx = bat.rect.centerx - bullet.rect.centerx
                    dy = bat.rect.centery - bullet.rect.centery
                    direction = pygame.math.Vector2(dx, dy)
                    
                    bat.take_damage(bullet.damage, direction)
                    if bat.hp <= 0:
                        self._handle_bat_death(bullet, bat)
                    else:
                        self.bullets.remove(bullet)
                        self.snd_hit.play(maxtime=0)
                    break

    def _check_collision(self, obj1, obj2):
        return (obj1.rect.right >= obj2.rect.left and
                obj1.rect.left <= obj2.rect.right and
                obj1.rect.bottom >= obj2.rect.top and
                obj1.rect.top <= obj2.rect.bottom)

    def _handle_enemy_death(self, bullet, enemy):
        self.bullets.remove(bullet)
        enemy.state = enemy.STATE_DYING
        enemy.death_start_time = pygame.time.get_ticks()
        self.dead_enemies.append(enemy)
        self.enemies.remove(enemy)
        self.dead_enemies_count += 1
        self.score += 2
        self.bullet_count += 3
        self.explode_channel.play(self.snd_explode)

    def _handle_batmage_death(self, bullet, batmage):
        self.bullets.remove(bullet)
        batmage.state = batmage.STATE_DYING
        batmage.death_start_time = pygame.time.get_ticks()
        self.dead_batmages.append(batmage)
        self.batmages.remove(batmage)
        self.score += 50
        self.bullet_count += 30
        self.explode_channel.play(self.snd_explode)

    def _handle_bat_death(self, bullet, bat):
        self.bullets.remove(bullet)
        bat.state = bat.STATE_DYING
        bat.death_start_time = pygame.time.get_ticks()
        self.dead_bats.append(bat)
        self.bats.remove(bat)
        self.score += 3
        self.bullet_count += 3
        self.explode_channel.play(self.snd_explode)

    # 蝙蝠相关
    def _create_bat(self):
        new_bat = Bat(self)
        self.bats.append(new_bat)
        
    def _update_bats(self, dt):
        for bat in self.bats:
            bat.update(dt)
            if self._check_collision(self.ship, bat):
                self._handle_ship_bat_collision(bat)

    def _handle_ship_bat_collision(self, bat):
        if self.ship.is_invulnerable():
            return
        
        if self.ship.hp - 51 > 0:
            self.ship.take_damage(51)
            bat.state = bat.STATE_DYING
            bat.death_start_time = pygame.time.get_ticks()
            self.dead_bats.append(bat)
            self.bats.remove(bat)
            self.explode_channel.play(self.snd_explode)
        else:
            self.ship.take_damage(51)
            self._handle_ship_death()

    # batmage相关
    def _create_batmage(self):
        new_batmage = Batmage(self)
        self.batmages.append(new_batmage)
        
    def _update_batmages(self, dt):
        for batmage in self.batmages:
            batmage.update(dt)

    # 敌人相关
    def _create_enemy(self):
        new_enemy = Enemy(self)
        self.enemies.append(new_enemy)

    def _update_enemies(self, dt):
        for enemy in self.enemies:
            enemy.update(dt)
            
        for enemy in self.enemies:
            if self._check_collision(self.ship, enemy):
                self._handle_ship_enemy_collision(enemy)
                
        for batmage in self.batmages:
            if self._check_collision(self.ship, batmage):
                self._handle_ship_batmage_collision(batmage)

    def _handle_ship_enemy_collision(self, enemy):
        if self.ship.is_invulnerable():
            return
        
        if self.ship.hp - 51 > 0:
            self.ship.take_damage(51)
            enemy.state = enemy.STATE_DYING
            enemy.death_start_time = pygame.time.get_ticks()
            self.dead_enemies.append(enemy)
            self.enemies.remove(enemy)
            if self.score > 0:
                self.score = max(0, self.score - 7)
            self.bullet_count += 3
            self.max_score = self.score
            self.explode_channel.play(self.snd_explode)
            print(f"现在还剩: {self.ship.hp} 点血量")
        else:
            self._handle_ship_death()

    def _handle_ship_batmage_collision(self, batmage):
        if self.ship.is_invulnerable():
            return
        
        if self.ship.hp - 100 > 0:
            self.ship.take_damage(100)
            batmage.take_damage(50, Vector2(0, 0))
            if batmage.hp <= 0:
                self._handle_batmage_death(None, batmage)
            if self.score > 0:
                self.score = max(0, self.score - 8)
            self.bullet_count += 10
            self.max_score = self.score
            self.explode_channel.play(self.snd_explode)
            print(f"现在还剩: {self.ship.hp} 点血量")
        else:
            self._handle_ship_death()

    def _handle_ship_death(self):
        self.ship.take_damage(self.ship.hp)
        self.game_run_times += 1
        self.game_state = self.STATE_MAINMENU
        self.wait_ship_death_over_tick = pygame.time.get_ticks()
        self.enemies.clear()
        self.bullets.empty()
        self.batmages.clear()
        self.bats.clear()
        self.snd_gameover.play()

    #主屏幕绘制
    def _update_screen(self):
        self.screen.blit(self.bg_img, (0, -260))        
        if self.game_state == self.STATE_SETTING:
            self.screen.blit(self.setting_ui_img,(self.screen_rect.centerx - 250,self.screen_rect.centery - 250))
        if not self.ship.state == self.ship.STATE_DYING and self.game_state == self.STATE_GAMERUNNING:
            self.ship.blitme()

        now = pygame.time.get_ticks()
        for dead in self.dead_enemies[:]:
            if dead.state == dead.STATE_DYING:
                elapsed = now - dead.death_start_time
                frame_index = min(9, int(elapsed // 50))
                if frame_index < len(dead.death_frames):
                    self.screen.blit(dead.death_frames[frame_index], dead.rect.topleft)
                if elapsed >= dead.death_duration:
                    self.dead_enemies.remove(dead)

        for dead in self.dead_batmages[:]:
            if dead.state == dead.STATE_DYING:
                elapsed = now - dead.death_start_time
                frame_index = min(8, int(elapsed // 50))
                if frame_index < len(dead.frames_death):
                    self.screen.blit(dead.frames_death[frame_index], dead.rect.topleft)
                if elapsed >= 400:
                    self.dead_batmages.remove(dead)

        for dead in self.dead_bats[:]:
            if dead.state == dead.STATE_DYING:
                elapsed = now - dead.death_start_time
                frame_index = min(9, int(elapsed // 50))
                if frame_index < len(dead.frames_death):
                    self.screen.blit(dead.frames_death[frame_index], dead.rect.topleft)
                if elapsed >= 400:
                    self.dead_bats.remove(dead)

        if self.ship.state == self.ship.STATE_DYING:
            elapsed = now - self.ship.death_start_time
            frame_index = min(9, int(elapsed // 50))
            if frame_index < len(self.ship.death_frames):
                self.screen.blit(self.ship.death_frames[frame_index], self.ship.rect.topleft)

        for bullet in self.bullets.sprites():
            self.screen.blit(bullet.image, bullet.rect)
        
        if self.game_state == self.STATE_GAMERUNNING:
            for enemy in self.enemies:
                self.screen.blit(enemy.image, enemy.rect)
                
            for batmage in self.batmages:
                self.screen.blit(batmage.image, batmage.rect)
            
            for bat in self.bats:
                self.screen.blit(bat.image, bat.rect)
                
            self.screen.blit(
                pygame.image.load(rpath.rpath('assets/images/bullets/bullet_count.png')).convert_alpha(),
                (10, self.settings.screen_height - 70)
            )
            
            bullet_str = str(self.bullet_count)
            x_num = self.settings.screen_width - 10
            for digit in reversed(bullet_str):
                img = self.bullet_digits[int(digit)]
                x_num -= img.get_width()
                self.screen.blit(img, (x_num, self.settings.screen_height - 56))

            hp_percent = self.ship.hp / self.ship.MaxHp
            bar_width = int(185 * hp_percent)
            self.screen.blit(self.hp_img, (10, 30))
            self.screen.blit(self.hpBar_img, (78, 35))
            pygame.draw.rect(self.screen, (236, 30, 4), pygame.Rect(82, 38, bar_width, 21))

            score_str = str(self.score)
            x_score = self.settings.screen_width - 10
            for digit in reversed(score_str):
                img = self.digits[int(digit)]
                x_score -= img.get_width()
                self.screen.blit(img, (x_score, 10))

        if self.game_state == self.STATE_MAINMENU and not self.dying:
            self.play_button.draw_button()
            self.setting_button.draw_button()
            self.exit_button.draw_button()

        pygame.display.flip()

    def _game_over(self, now_time):
        self.dying = True
        if now_time - self.wait_ship_death_over_tick >= 700:
            self._reset_game()

    def _reset_game(self):
        self.ship.center_ship()
        self.score = 0
        self.bullet_count = 20
        self.ship.hp = self.ship.MaxHp
        self.ship.state = self.ship.STATE_NORMAL
        self.ship.death_start_time = 0
        self.ship.hit_duration = 0
        if self.max_score > self.all_max_score:
            self.all_max_score = self.max_score
        self.dying = False
        self.enemies.clear()
        self.bullets.empty()
        self.batmages.clear()
        self.bats.clear()
        self.dead_enemies.clear()
        self.dead_batmages.clear()
        self.dead_bats.clear()

    # 主游戏循环
    def run_game(self):
        clock = pygame.time.Clock()
        last_time = pygame.time.get_ticks()
        
        while True:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time
            
            self._check_events()
            
            if self.game_state == self.STATE_GAMERUNNING:
                self.ship.update(dt)
                
                self._update_bullets(dt)
                
                self._update_enemies(dt)
                
                now = pygame.time.get_ticks()
                if now - self.wait_enemy_spawn_tick >= 700:
                    self._create_enemy()
                    self.wait_enemy_spawn_tick = now
                
                if self.dead_enemies_count >= self.enough_dead_enemies_count:
                    self._create_batmage()
                    self.enough_dead_enemies_count += 70
                
                self._update_batmages(dt)
                
                self._update_bats(dt)
                
            elif self.game_state == self.STATE_MAINMENU and self.game_run_times >= 1:
                self._game_over(pygame.time.get_ticks())
            
            self._update_screen()
            clock.tick(240)

# 入口
if __name__ == '__main__':
    sf = SkyForce()
    sf.run_game()