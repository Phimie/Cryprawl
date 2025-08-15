import sys
import pygame
import random
import rpath
from pygame.math import Vector2
from settings import Settings
from ship import Ship
from bullet import Bullet
from enemy import Enemy
from button import Button
from Batmage import Batmage
from bat import Bat

class Cryprawl:
    STATE_GAMERUNNING = 'gamerunning'
    STATE_MAINMENU = 'mainmenu'
    STATE_SETTING = 'setting'
    STATE_PAUSEMENU = 'pausemenu'
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption("Cryprawl")
        pygame.display.set_icon(pygame.image.load(rpath.rpath("assets/images/icon/CR.ico")).convert_alpha())
        
        # init UI
        self._init_ui_elements()
        
        # game_state
        self.game_state = self.STATE_MAINMENU
        self.is_fullscreen = False
        self.is_sound_off = False
        self.room_number = 0
        self.cur_room_over = False
        self.dying = False
        self.debug_mode = False

        # 游戏对象
        self.enemies = []
        self.dead_enemies = []
        self.dead_enemies_count = 0
        self.enough_dead_enemies_count = 10
        self.dead_batmages_count = 0
        self.enough_dead_batmage_count = 1
        
        self.batmages = []
        self.dead_batmages = []
        
        self.bats = []
        self.dead_bats = []
        
        # player
        self.ship = Ship(self)
        
        # bullets
        self.bullets = pygame.sprite.Group()
        
        # init buttons
        self._init_buttons()
        
        # 游戏数据
        self.game_run_times = 0
        self.score = 0
        self.max_score = 0
        self.all_max_score = 0
        self.bullet_count = self.settings.bullet_count


        # 计时器
        self.wait_ship_death_over_tick = pygame.time.get_ticks()
        self.wait_enemy_spawn_tick = pygame.time.get_ticks()
        self.wait_batmage_spawn_tick = pygame.time.get_ticks()
        self.wait_bat_spawn_tick = pygame.time.get_ticks()

        # digits image
        self.digits = []
        for i in range(10):
            self.digits.append(pygame.image.load(rpath.rpath(f'assets/images/digits/{i}.png')).convert_alpha())
        
        self.bullet_digits = []
        for i in range(10):
            self.bullet_digits.append(pygame.image.load(rpath.rpath(f'assets/images/bullets/bullet_digits/{i}.png')).convert_alpha())
        
        # room digits image
        self.room_digits = []
        for i in range(10):
            self.room_digits.append(pygame.image.load(rpath.rpath(f'assets/images/digits/{i}.png')).convert_alpha())

        # sound
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)
        pygame.mixer.music.load(rpath.rpath("assets/audio/background.mp3"))
        pygame.mixer.music.play(loops=-1, fade_ms=1000)
        pygame.mixer.music.set_volume(self.settings.game_volume)
        
        self.snd_hit = pygame.mixer.Sound(rpath.rpath("assets/audio/hit.wav"))
        self.snd_hit.set_volume(self.settings.game_volume)
        
        self.snd_shoot = pygame.mixer.Sound(rpath.rpath("assets/audio/shoot.wav"))
        self.snd_shoot.set_volume(self.settings.game_volume)
        
        self.snd_explode = pygame.mixer.Sound(rpath.rpath("assets/audio/explode.wav"))
        self.snd_explode.set_volume(self.settings.game_volume)
        
        self.snd_score = pygame.mixer.Sound(rpath.rpath("assets/audio/score.wav"))
        self.snd_score.set_volume(self.settings.game_volume)
        
        self.snd_click = pygame.mixer.Sound(rpath.rpath("assets/audio/click.wav"))
        self.snd_click.set_volume(self.settings.click_volume)
        
        self.snd_gameover = pygame.mixer.Sound(rpath.rpath("assets/audio/gameover.wav"))
        self.snd_gameover.set_volume(self.settings.game_over_volume)
        
        # init UI positions
        self.update_ui_positions()

    def _init_ui_elements(self):
        # main title贴图
        self.main_title_img = pygame.image.load(rpath.rpath("assets/images/background/MainTitle.png")).convert_alpha()
        self.main_title_img_rect = self.main_title_img.get_rect()
        
        # background贴图
        self.bg_img = pygame.image.load(rpath.rpath("assets/images/background/background.png")).convert_alpha()
        self.bg_img_rect = self.bg_img.get_rect()
        
        # game_arena贴图
        self.game_arena_img = pygame.image.load(rpath.rpath("assets/images/background/game_arena.png")).convert_alpha()
        self.game_arena_img_rect = self.game_arena_img.get_rect()
        
        # hp贴图
        self.hp_img = pygame.image.load(rpath.rpath("assets/images/ship/hp.png")).convert_alpha()
        self.hp_img_rect = self.hp_img.get_rect()
        
        # hp bar贴图
        self.hpBar_img = pygame.image.load(rpath.rpath("assets/images/ship/hp_bar.png")).convert_alpha()
        self.hpBar_img_rect = self.hpBar_img.get_rect()
        
        # ui贴图
        self.setting_ui_img = pygame.image.load(rpath.rpath("assets/images/button/settingUI.png")).convert_alpha()
        self.setting_ui_img_rect = self.setting_ui_img.get_rect()
        
        # fullscreen贴图
        self.fullscreen_img = pygame.image.load(rpath.rpath("assets/images/button/fullscreen.png"))
        self.fullscreen_img_rect = self.fullscreen_img.get_rect()
        
        # sound贴图
        self.sound_img = pygame.image.load(rpath.rpath("assets/images/button/sound.png"))
        self.sound_img_rect = self.sound_img.get_rect()

        # hitbox贴图
        self.hitbox_img = pygame.image.load(rpath.rpath("assets/images/button/hitbox.png"))
        self.hitbox_img_rect = self.hitbox_img.get_rect()
        
        # tick贴图
        self.fullscreen_tick_img = pygame.image.load(rpath.rpath("assets/images/button/tick.png"))
        self.fullscreen_tick_img_rect = self.fullscreen_tick_img.get_rect()
        
        self.sound_tick_img = pygame.image.load(rpath.rpath("assets/images/button/tick.png"))
        self.sound_tick_img_rect = self.sound_tick_img.get_rect()

        self.hitbox_tick_img = pygame.image.load(rpath.rpath("assets/images/button/tick.png"))
        self.hitbox_tick_img_rect = self.hitbox_tick_img.get_rect()

        # stair贴图
        self.stair_img = pygame.image.load(rpath.rpath("assets/images/background/stair.png"))
        self.stair_img_rect = self.stair_img.get_rect()

    def _init_buttons(self):
        # play_button
        self.play_button = Button(self)
        self.play_button.image = pygame.image.load(rpath.rpath("assets/images/button/play.png")).convert_alpha()
        
        # setting_button
        self.setting_button = Button(self)
        self.setting_button.image = pygame.image.load(rpath.rpath("assets/images/button/setting.png")).convert_alpha()
        
        # exit_button
        self.exit_button = Button(self)
        self.exit_button.image = pygame.image.load(rpath.rpath("assets/images/button/exit.png")).convert_alpha()
        
        # back_button
        self.back_button = Button(self)
        self.back_button.image = pygame.image.load(rpath.rpath("assets/images/button/back.png")).convert_alpha()
        
        # fullscreen_button
        self.fullscreen_button = Button(self)
        self.fullscreen_button.width = 28
        self.fullscreen_button.height = 28
        self.fullscreen_button.image = pygame.image.load(rpath.rpath("assets/images/button/checkbox.png")).convert_alpha()
        
        # sound_button
        self.sound_button = Button(self)
        self.sound_button.width = 28
        self.sound_button.height = 28
        self.sound_button.image = pygame.image.load(rpath.rpath("assets/images/button/checkbox.png")).convert_alpha()

        # hitbox_button
        self.hitbox_button = Button(self)
        self.hitbox_button.width = 28
        self.hitbox_button.height = 28
        self.hitbox_button.image = pygame.image.load(rpath.rpath("assets/images/button/checkbox.png")).convert_alpha()


    def update_ui_positions(self):
        self.screen_rect = self.screen.get_rect()
        
        # main title贴图
        self.main_title_img_rect.centerx = self.screen_rect.centerx
        self.main_title_img_rect.centery = self.screen_rect.centery - 300
        
        # background贴图
        self.bg_img_rect.centerx = self.screen_rect.centerx
        self.bg_img_rect.centery = self.screen_rect.centery

        # game_arena贴图
        self.game_arena_img_rect.centerx = self.screen_rect.centerx
        self.game_arena_img_rect.centery = self.screen_rect.centery

        # stair贴图
        self.stair_img_rect.centerx = self.game_arena_img_rect.centerx
        self.stair_img_rect.centery = self.game_arena_img_rect.centery
        
        # 设置UI贴图
        self.setting_ui_img_rect.centerx = self.screen_rect.centerx
        self.setting_ui_img_rect.centery = self.screen_rect.centery
        
        # 设置fullscreen贴图
        self.fullscreen_img_rect.centerx = self.setting_ui_img_rect.centerx - 70
        self.fullscreen_img_rect.centery = self.setting_ui_img_rect.centery - 190
        
        # 设置sound贴图
        self.sound_img_rect.centerx = self.setting_ui_img_rect.centerx - 70
        self.sound_img_rect.centery = self.setting_ui_img_rect.centery - 130

        # 设置hitbox贴图
        self.hitbox_img_rect.centerx = self.setting_ui_img_rect.centerx - 70
        self.hitbox_img_rect.centery = self.setting_ui_img_rect.centery - 70
        
        # checkbox位置
        self.play_button.rect.center = self.screen_rect.center
        self.setting_button.rect.centerx = self.screen_rect.centerx
        self.setting_button.rect.centery = self.screen_rect.centery + 80
        self.exit_button.rect.centerx = self.screen_rect.centerx
        self.exit_button.rect.centery = self.screen_rect.centery + 160
        self.back_button.rect.centerx = self.setting_ui_img_rect.centerx - 100
        self.back_button.rect.centery = self.setting_ui_img_rect.centery + 210

        self.fullscreen_button.rect.centerx = self.fullscreen_img_rect.centerx + 230
        self.fullscreen_button.rect.centery = self.fullscreen_img_rect.centery + 20
        self.sound_button.rect.centerx = self.sound_img_rect.centerx + 230
        self.sound_button.rect.centery = self.sound_img_rect.centery + 20
        self.hitbox_button.rect.centerx = self.hitbox_img_rect.centerx + 230
        self.hitbox_button.rect.centery = self.hitbox_img_rect.centery + 20
        
        # tick位置
        self.fullscreen_tick_img_rect.centerx = self.fullscreen_button.rect.centerx - 66
        self.fullscreen_tick_img_rect.centery = self.fullscreen_button.rect.centery - 10
        self.sound_tick_img_rect.centerx = self.sound_button.rect.centerx - 66
        self.sound_tick_img_rect.centery = self.sound_button.rect.centery - 10
        self.hitbox_tick_img_rect.centerx = self.hitbox_button.rect.centerx - 66
        self.hitbox_tick_img_rect.centery = self.hitbox_button.rect.centery - 10
        
        # 更新飞船位置
        self.ship.center_ship()

    # 静音
    def play_sound(self, sound_obj, loops=0, maxtime=0):
        if self.is_sound_off:
            return
        sound_obj.play(loops=loops, maxtime=maxtime)

    # 退出
    def quit_game(self):
        if self.max_score > self.all_max_score:
            self.all_max_score = self.max_score
        print(f"最后一局最大分数为: {self.max_score}")
        print(f"历史最高最大分数为: {self.all_max_score}")
        print(f"游戏局数为: {self.game_run_times}")
        sys.exit()
    
    # 处理事件
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.VIDEORESIZE:
                self.update_ui_positions()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.toggle_hitbox()


            
    

    # 处理鼠标点击
    def handle_mouse_click(self, mouse_pos):
        if self.game_state == self.STATE_MAINMENU:
            self.handle_main_menu_click(mouse_pos)
        elif self.game_state == self.STATE_GAMERUNNING:
            self.fire_bullet()
        elif self.game_state == self.STATE_SETTING:
            self.handle_setting_menu_click(mouse_pos)
    
    # 处理主界面点击
    def handle_main_menu_click(self, mouse_pos):
        if self.play_button.rect.collidepoint(mouse_pos):
            self.start_game()
        elif self.setting_button.rect.collidepoint(mouse_pos):
            self.open_settings()
        elif self.exit_button.rect.collidepoint(mouse_pos):
            self.quit_game()
    
    # 处理设置界面点击
    def handle_setting_menu_click(self, mouse_pos):
        if self.back_button.rect.collidepoint(mouse_pos):
            self.close_settings()
        elif self.fullscreen_button.rect.collidepoint(mouse_pos):
            self.toggle_fullscreen()
        elif self.sound_button.rect.collidepoint(mouse_pos):
            self.toggle_sound()
        elif self.hitbox_button.rect.collidepoint(mouse_pos):
            self.toggle_hitbox()

    
    def start_game(self):
        self.game_state = self.STATE_GAMERUNNING
        self.play_sound(self.snd_click)
    
    def open_settings(self):
        self.game_state = self.STATE_SETTING
        self.play_sound(self.snd_click)
    
    def close_settings(self):
        self.game_state = self.STATE_MAINMENU
        self.play_sound(self.snd_click)
    
    # 开关全屏
    def toggle_fullscreen(self):
        self.play_sound(self.snd_click)
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
            self.is_fullscreen = False
        else:
            self.screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h), pygame.FULLSCREEN)
            self.is_fullscreen = True
        
        # 更新UI位置
        self.update_ui_positions()
    
    # 开关声音
    def toggle_sound(self):
        self.play_sound(self.snd_click)
        if self.is_sound_off:
            self.is_sound_off = False
            pygame.mixer.music.unpause()
        else:
            self.is_sound_off = True
            pygame.mixer.music.pause()

    # 开关hitbox
    def toggle_hitbox(self):
        self.play_sound(self.snd_click)
        if self.debug_mode:
            self.debug_mode = False
        else:
            self.debug_mode = True

    def fire_bullet(self):
        if self.bullet_count > 0:
            mouse_pos = pygame.mouse.get_pos()
            new_bullet = Bullet(self, mouse_pos)
            self.bullets.add(new_bullet)
            self.bullet_count -= 1
            self.play_sound(self.snd_shoot)
    
    def update_bullets(self, dt):
        self.bullets.update(dt)
        
        # 子弹碰撞检测
        for bullet in self.bullets.copy():
            self.check_bullet_collisions(bullet)
    
    def check_bullet_collisions(self, bullet):
        # 与enemy碰撞
        for enemy in self.enemies[:]:
            if bullet.rect.colliderect(enemy.rect):
                self.handle_bullet_enemy_collision(bullet, enemy)
                return
        
        # 与batmage碰撞
        for batmage in self.batmages[:]:
            if bullet.rect.colliderect(batmage.hitbox_rect):
                self.handle_bullet_batmage_collision(bullet, batmage)
                return
        
        # 与bat碰撞
        for bat in self.bats[:]:
            if bullet.rect.colliderect(bat.rect):
                self.handle_bullet_bat_collision(bullet, bat)
                return
    
    def handle_bullet_enemy_collision(self, bullet, enemy):
        dx = enemy.rect.centerx - bullet.rect.centerx
        dy = enemy.rect.centery - bullet.rect.centery
        direction = Vector2(dx, dy)
        
        enemy.take_damage(bullet.damage, direction)
        
        if enemy.enemy_hp <= 0:
            self.handle_enemy_death(bullet, enemy)
        else:
            self.bullets.remove(bullet)
            self.play_sound(self.snd_hit)
    
    def handle_bullet_batmage_collision(self, bullet, batmage):
        dx = batmage.rect.centerx - bullet.rect.centerx
        dy = batmage.rect.centery - bullet.rect.centery
        direction = Vector2(dx, dy)
        
        batmage.take_damage(bullet.damage, direction)
        if batmage.hp <= 0:
            self.handle_batmage_death(bullet, batmage)
        else:
            self.bullets.remove(bullet)
            self.play_sound(self.snd_hit)
    
    def handle_bullet_bat_collision(self, bullet, bat):
        dx = bat.rect.centerx - bullet.rect.centerx
        dy = bat.rect.centery - bullet.rect.centery
        direction = Vector2(dx, dy)
        
        bat.take_damage(bullet.damage, direction)
        if bat.hp <= 0:
            self.handle_bat_death(bullet, bat)
        else:
            self.bullets.remove(bullet)
            self.play_sound(self.snd_hit)
    
    def handle_enemy_death(self, bullet, enemy):
        self.bullets.remove(bullet)
        enemy.state = enemy.STATE_DYING
        enemy.death_start_time = pygame.time.get_ticks()
        self.dead_enemies.append(enemy)
        self.enemies.remove(enemy)
        self.dead_enemies_count += 1
        self.score += 2
        self.bullet_count += 3
        self.play_sound(self.snd_explode)
    
    def handle_batmage_death(self, bullet, batmage):
        self.bullets.remove(bullet)
        batmage.state = batmage.STATE_DYING
        batmage.death_start_time = pygame.time.get_ticks()
        self.dead_batmages.append(batmage)
        self.batmages.remove(batmage)
        self.dead_batmages_count += 1
        self.score += 50
        self.bullet_count += 30
        self.play_sound(self.snd_explode)
    
    def handle_bat_death(self, bullet, bat):
        self.bullets.remove(bullet)
        bat.state = bat.STATE_DYING
        bat.death_start_time = pygame.time.get_ticks()
        self.dead_bats.append(bat)
        self.bats.remove(bat)
        self.score += 3
        self.bullet_count += 3
        self.play_sound(self.snd_explode)

    def create_bat(self):
        new_bat = Bat(self)
        self.bats.append(new_bat)
        
    def update_bats(self, dt):
        for bat in self.bats:
            bat.update(dt)
            if self.ship.rect.colliderect(bat.rect):
                self.handle_ship_bat_collision(bat)
    
    def handle_ship_bat_collision(self, bat):
        if self.ship.is_invulnerable():
            return
        
        if self.ship.hp - 51 > 0:
            self.ship.take_damage(51)
            bat.state = bat.STATE_DYING
            bat.death_start_time = pygame.time.get_ticks()
            self.dead_bats.append(bat)
            self.bats.remove(bat)
            self.play_sound(self.snd_explode)
        else:
            self.handle_ship_death()

    def create_batmage(self):
        new_batmage = Batmage(self)
        self.batmages.append(new_batmage)
        
    def update_batmages(self, dt):
        for batmage in self.batmages:
            batmage.update(dt)

    def create_enemy(self):
        new_enemy = Enemy(self)
        self.enemies.append(new_enemy)

    def update_enemies(self, dt):
        for enemy in self.enemies:
            enemy.update(dt)
            
        for enemy in self.enemies:
            if self.ship.rect.colliderect(enemy.rect):
                self.handle_ship_enemy_collision(enemy)
                
        for batmage in self.batmages:
            if self.ship.rect.colliderect(batmage.hitbox_rect):
                self.handle_ship_batmage_collision(batmage)
    
    def handle_ship_enemy_collision(self, enemy):
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
            self.play_sound(self.snd_explode)
            print(f"现在还剩: {self.ship.hp} 点血量")
        else:
            self.handle_ship_death()
    
    def handle_ship_batmage_collision(self, batmage):
        if self.ship.is_invulnerable():
            return
        
        if self.ship.hp - 100 > 0:
            self.ship.take_damage(100)
            batmage.take_damage(50, Vector2(0, 0))
            if batmage.hp <= 0:
                self.handle_batmage_death(None, batmage)
            if self.score > 0:
                self.score = max(0, self.score - 8)
            self.bullet_count += 10
            self.max_score = self.score
            self.play_sound(self.snd_explode)
            print(f"现在还剩: {self.ship.hp} 点血量")
        else:
            self.handle_ship_death()
    
    def handle_ship_death(self):
        self.ship.take_damage(self.ship.hp)
        self.game_run_times += 1
        self.game_state = self.STATE_MAINMENU
        self.wait_ship_death_over_tick = pygame.time.get_ticks()
        self.enemies.clear()
        self.bullets.empty()
        self.batmages.clear()
        self.bats.clear()
        self.play_sound(self.snd_gameover)

    def render_stair(self):
        # 绘制楼梯
        self.screen.blit(self.stair_img, self.stair_img_rect)


    def render_screen(self):
        # 绘制背景
        self.screen.blit(self.bg_img, self.bg_img_rect)
        self.screen.blit(self.game_arena_img, self.game_arena_img_rect)
        
        # 绘制设置界面
        if self.game_state == self.STATE_SETTING:
            self.render_settings_menu()
        
        # 绘制游戏对象
        self.render_game_objects()
        
        # 绘制UI元素
        self.render_ui_elements()
        
        pygame.display.flip()
    
    def render_settings_menu(self):
        self.screen.blit(self.setting_ui_img, self.setting_ui_img_rect)
        self.screen.blit(self.back_button.image, self.back_button.rect)

        self.screen.blit(self.fullscreen_img, self.fullscreen_img_rect)
        self.screen.blit(self.fullscreen_button.image, self.fullscreen_button.rect)
        if self.is_fullscreen:
            self.screen.blit(self.fullscreen_tick_img, self.fullscreen_tick_img_rect)

        self.screen.blit(self.sound_img, self.sound_img_rect)
        self.screen.blit(self.sound_button.image, self.sound_button.rect)
        if not self.is_sound_off:
            self.screen.blit(self.sound_tick_img, self.sound_tick_img_rect)

        self.screen.blit(self.hitbox_img, self.hitbox_img_rect)
        self.screen.blit(self.hitbox_button.image, self.hitbox_button.rect)
        if self.debug_mode:
            self.screen.blit(self.hitbox_tick_img, self.hitbox_tick_img_rect)
    
    def render_game_objects(self):
        # 绘制玩家
        if not self.ship.state == self.ship.STATE_DYING and self.game_state == self.STATE_GAMERUNNING:
            self.ship.blitme()
            self.hitbox_display(self.ship.rect)

        now = pygame.time.get_ticks()
        self.render_dead_enemies(now)
        self.render_dead_batmages(now)
        self.render_dead_bats(now)
        
        if self.ship.state == self.ship.STATE_DYING:
            self.render_dying_ship(now)

        for bullet in self.bullets.sprites():
            self.screen.blit(bullet.image, bullet.rect)
        
        if self.game_state == self.STATE_GAMERUNNING:
            for enemy in self.enemies:
                self.screen.blit(enemy.image, enemy.rect)
                self.hitbox_display(enemy.rect)
                
            for batmage in self.batmages:
                self.screen.blit(batmage.image, batmage.rect)
                self.hitbox_display(batmage.hitbox_rect)
            
            for bat in self.bats:
                self.screen.blit(bat.image, bat.rect)
                self.hitbox_display(bat.rect)
                
            self.render_game_hud()
            
            # 显示楼梯
            if self.cur_room_over:
                self.render_stair()
    
    def render_dead_enemies(self, now):
        for dead in self.dead_enemies[:]:
            if dead.state == dead.STATE_DYING:
                elapsed = now - dead.death_start_time
                frame_index = min(9, int(elapsed // 50))
                if frame_index < len(dead.death_frames):
                    self.screen.blit(dead.death_frames[frame_index], dead.rect.topleft)
                if elapsed >= dead.death_duration:
                    self.dead_enemies.remove(dead)
    
    def render_dead_batmages(self, now):
        for dead in self.dead_batmages[:]:
            if dead.state == dead.STATE_DYING:
                elapsed = now - dead.death_start_time
                frame_index = min(8, int(elapsed // 50))
                if frame_index < len(dead.frames_death):
                    self.screen.blit(dead.frames_death[frame_index], dead.rect.topleft)
                if elapsed >= 400:
                    self.dead_batmages.remove(dead)
    
    def render_dead_bats(self, now):
        for dead in self.dead_bats[:]:
            if dead.state == dead.STATE_DYING:
                elapsed = now - dead.death_start_time
                frame_index = min(9, int(elapsed // 50))
                if frame_index < len(dead.frames_death):
                    self.screen.blit(dead.frames_death[frame_index], dead.rect.topleft)
                if elapsed >= 400:
                    self.dead_bats.remove(dead)
    
    def render_dying_ship(self, now):
        elapsed = now - self.ship.death_start_time
        frame_index = min(9, int(elapsed // 50))
        if frame_index < len(self.ship.death_frames):
            self.screen.blit(self.ship.death_frames[frame_index], self.ship.rect.topleft)
    
    def render_game_hud(self):
        # 子弹计数
        self.screen.blit(
            pygame.image.load(rpath.rpath('assets/images/bullets/bullet_count.png')).convert_alpha(),
            (10, self.screen_rect.height - 70)
        )
        
        bullet_str = str(self.bullet_count)
        x_num = self.screen_rect.width - 10
        for digit in reversed(bullet_str):
            img = self.bullet_digits[int(digit)]
            x_num -= img.get_width()
            self.screen.blit(img, (x_num, self.screen_rect.height - 56))

        # 血量条
        hp_percent = self.ship.hp / self.ship.MaxHp
        bar_width = int(185 * hp_percent)
        self.screen.blit(self.hp_img, (10, 30))
        self.screen.blit(self.hpBar_img, (78, 35))
        pygame.draw.rect(self.screen, (236, 30, 4), pygame.Rect(82, 38, bar_width, 21))

        # 分数
        score_str = str(self.score)
        x_score = self.screen_rect.width - 10
        for digit in reversed(score_str):
            img = self.digits[int(digit)]
            x_score -= img.get_width()
            self.screen.blit(img, (x_score, 10))
            
        # 房间号
        room_str = str(self.room_number)
        room_width = 0
        for digit in room_str:
            img = self.room_digits[int(digit)]
            room_width += img.get_width()
        
        x_room = self.screen_rect.centerx - room_width // 2
        for digit in room_str:
            img = self.room_digits[int(digit)]
            self.screen.blit(img, (x_room, 10))
            x_room += img.get_width()
    
    def render_ui_elements(self):
        if self.game_state == self.STATE_MAINMENU and not self.dying:
            self.screen.blit(self.main_title_img, self.main_title_img_rect)
            self.screen.blit(self.play_button.image, self.play_button.rect)
            self.screen.blit(self.setting_button.image, self.setting_button.rect)
            self.screen.blit(self.exit_button.image, self.exit_button.rect)

    def game_over(self, now_time):
        self.dying = True
        if now_time - self.wait_ship_death_over_tick >= 700:
            self.reset_game()

    def reset_game(self):
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
        self.room_number = 0
        self.cur_room_over = False

    # 主游戏循环
    def run_game(self):
        clock = pygame.time.Clock()
        last_time = pygame.time.get_ticks()
        
        while True:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time
            
            self.handle_events()
            
            if self.game_state == self.STATE_GAMERUNNING:
                self.update_game_state(dt)
            elif self.game_state == self.STATE_MAINMENU and self.game_run_times >= 1:
                self.game_over(pygame.time.get_ticks())
            
            self.render_screen()
            clock.tick(240)
    
    def update_game_state(self, dt):
        self.ship.update(dt)
        self.update_bullets(dt)
        self.update_room_number()
        
        now = pygame.time.get_ticks()
        
        if not self.cur_room_over:
            if now - self.wait_enemy_spawn_tick >= 700:
                self.create_enemy()
                self.wait_enemy_spawn_tick = now
            
            if self.dead_enemies_count >= self.enough_dead_enemies_count:
                self.create_batmage()
                self.enough_dead_enemies_count += 70
            
            self.update_enemies(dt)
            self.update_batmages(dt)
            self.update_bats(dt)
    
    def update_room_number(self):
        for i in range(100):
            if self.room_number == i and self.dead_batmages_count >= self.enough_dead_batmage_count:
                self.cur_room_over = True

        if self.cur_room_over and self.ship.rect.colliderect(self.stair_img_rect):
            self.room_number += 1
            self.cur_room_over = False
            self.dead_batmages_count = 0
            print(f"现在的层数为:{self.room_number}")

    def hitbox_display(self,rect):
        if self.debug_mode:
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)
        else:
            pass


# 入口
if __name__ == '__main__':
    cr = Cryprawl()
    cr.run_game()