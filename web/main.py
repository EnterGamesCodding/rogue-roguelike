import pygame
import math
import random
import sys
import os
import asyncio
from settings import *
from renderer import init_ascii_font, draw_char, draw_chars
from player import Player
from enemy import LightEnemy, MediumEnemy, HeavyEnemy
from particles import Particle
from ui import HUD, StartScreen, draw_text, FONT_SM, FONT_MD, FONT_LG, FONT_XL
from touch import TouchControls


class Game:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        flags = pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
        pygame.display.set_caption(TITLE)
        pygame.event.set_grab(False)
        self.clock = pygame.time.Clock()
        self.running = True
        init_ascii_font(20)

        self.touch = TouchControls()

        self.hud = HUD()
        self.start_screen = StartScreen()

        self.arena_rect = pygame.Rect(
            ARENA_PADDING, ARENA_PADDING,
            ARENA_WIDTH, ARENA_HEIGHT
        )

        self.state = "start"
        self.player = None
        self.enemies = []
        self.particles = []
        self.all_particles = []
        self.wave = 0
        self.wave_timer = 0
        self.enemies_spawned = 0
        self.enemies_per_wave = 0
        self.wave_delay_timer = 0
        self.game_over_delay = 0
        self.kill_count = 0

        self.shake_amount = 0
        self.shake_offset = [0, 0]

        self.upgrade_options = []
        self.upgrade_selected = -1

        self.grid_surf = self.create_grid_surface()

        self.last_time = pygame.time.get_ticks()

    def create_grid_surface(self):
        surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        from renderer import _FONT_W, _FONT_H
        grid_cw = max(1, _FONT_W // 2)
        grid_ch = max(1, _FONT_H // 2)
        for x in range(0, WINDOW_WIDTH, grid_cw * 8):
            draw_char(surf, '\u2502', (10, 15, 30), x, 0, False)
        for y in range(0, WINDOW_HEIGHT, grid_ch * 8):
            draw_char(surf, '\u2500', (10, 15, 30), 0, y, False)

        border_color = (30, 60, 120)
        dx = ARENA_PADDING
        dy = ARENA_PADDING
        draw_char(surf, '\u250C', border_color, dx, dy, False)
        draw_char(surf, '\u2510', border_color, WINDOW_WIDTH - dx - _FONT_W, dy, False)
        draw_char(surf, '\u2514', border_color, dx, WINDOW_HEIGHT - dy - _FONT_H, False)
        draw_char(surf, '\u2518', border_color, WINDOW_WIDTH - dx - _FONT_W, WINDOW_HEIGHT - dy - _FONT_H, False)

        for x in range(dx + _FONT_W, WINDOW_WIDTH - dx - _FONT_W, _FONT_W):
            draw_char(surf, '\u2500', border_color, x, dy, False)
            draw_char(surf, '\u2500', border_color, x, WINDOW_HEIGHT - dy - _FONT_H, False)
        for y in range(dy + _FONT_H, WINDOW_HEIGHT - dy - _FONT_H, _FONT_H):
            draw_char(surf, '\u2502', border_color, dx, y, False)
            draw_char(surf, '\u2502', border_color, WINDOW_WIDTH - dx - _FONT_W, y, False)

        return surf

    def start_game(self):
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.enemies.clear()
        self.all_particles.clear()
        self.wave = 0
        self.wave_timer = 0
        self.enemies_spawned = 0
        self.enemies_per_wave = 0
        self.wave_delay_timer = 0
        self.game_over_delay = 0
        self.kill_count = 0
        self.shake_amount = 0
        self.state = "playing"
        self.start_wave(1)

    def start_wave(self, wave_num):
        self.wave = wave_num
        self.enemies_spawned = 0
        self.enemies_per_wave = ENEMIES_PER_WAVE_BASE + wave_num + wave_num // 3
        self.wave_timer = 0.5

        for _ in range(5):
            self.all_particles.append(Particle(
                random.uniform(self.arena_rect.left, self.arena_rect.right),
                random.uniform(self.arena_rect.top, self.arena_rect.bottom),
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                NEON_YELLOW,
                random.uniform(0.5, 1.0)
            ))

    def generate_upgrades(self):
        pool = [u for u in UPGRADES]
        random.shuffle(pool)
        self.upgrade_options = pool[:3]
        self.upgrade_selected = -1

    def spawn_enemy(self):
        wave = self.wave

        if wave < 5:
            weights = {"light": 0.8, "medium": 0.2, "heavy": 0}
        elif wave < 10:
            weights = {"light": 0.5, "medium": 0.4, "heavy": 0.1}
        elif wave < 15:
            weights = {"light": 0.3, "medium": 0.4, "heavy": 0.3}
        else:
            weights = {"light": 0.2, "medium": 0.4, "heavy": 0.4}

        r = random.random()
        cumulative = 0
        enemy_type = "light"
        for t, w in weights.items():
            cumulative += w
            if r <= cumulative:
                enemy_type = t
                break

        margin = 40
        spawn_attempts = 0
        while spawn_attempts < 20:
            spawn_attempts += 1
            side = random.randint(0, 3)
            if side == 0:
                x = random.uniform(self.arena_rect.left + margin, self.arena_rect.right - margin)
                y = self.arena_rect.top - 20
            elif side == 1:
                x = random.uniform(self.arena_rect.left + margin, self.arena_rect.right - margin)
                y = self.arena_rect.bottom + 20
            elif side == 2:
                x = self.arena_rect.left - 20
                y = random.uniform(self.arena_rect.top + margin, self.arena_rect.bottom - margin)
            else:
                x = self.arena_rect.right + 20
                y = random.uniform(self.arena_rect.top + margin, self.arena_rect.bottom - margin)

            if not self.player:
                break

            dx = x - self.player.x
            dy = y - self.player.y
            if math.sqrt(dx * dx + dy * dy) < 100:
                continue

            if enemy_type == "light":
                enemy = LightEnemy(x, y)
            elif enemy_type == "medium":
                enemy = MediumEnemy(x, y)
            else:
                enemy = HeavyEnemy(x, y)
            self.enemies.append(enemy)
            break

    def update(self, dt):
        if self.state == "start":
            return

        if self.state == "playing":
            if not self.player or not self.player.alive:
                self.state = "gameover"
                self.game_over_delay = 2.0
                return

            if self.wave > TOTAL_WAVES:
                self.state = "victory"
                return

            if self.state == "upgrade":
                for particle in self.all_particles[:]:
                    particle.update(dt)
                    if not particle.alive:
                        self.all_particles.remove(particle)
                return

            if self.player and self.player.shield_active:
                dt *= SLOW_MOTION_FACTOR

            keys = pygame.key.get_pressed()
            touch_keys = self.touch.get_pressed()
            merged_keys = {k: (keys[k] or touch_keys.get(k, False)) for k in range(512)}
            self.player.update(dt, merged_keys, self.enemies, self.arena_rect, self.all_particles)

            if self.wave_delay_timer > 0:
                self.wave_delay_timer -= dt
                if self.wave_delay_timer <= 0:
                    self.start_wave(self.wave)

            if self.wave_timer > 0:
                self.wave_timer -= dt
                if self.wave_timer <= 0 and self.enemies_spawned < self.enemies_per_wave:
                    self.spawn_enemy()
                    self.enemies_spawned += 1
                    self.wave_timer = max(0.1, 0.5 - self.wave * 0.01)

            for enemy in self.enemies[:]:
                enemy.update(dt, self.player, self.arena_rect, self.enemies, self.all_particles)
                if not enemy.alive:
                    self.kill_count += 1
                    if self.player:
                        self.player.battery = min(self.player.max_battery,
                                                   self.player.battery + BATTERY_KILL_REGEN * 0.5)
                    for _ in range(10):
                        a = random.uniform(0, math.pi * 2)
                        s = random.uniform(2, 5)
                        self.all_particles.append(Particle(
                            enemy.x, enemy.y,
                            math.cos(a) * s,
                            math.sin(a) * s,
                            random.choice([enemy.color, WHITE, NEON_YELLOW]),
                            random.uniform(0.3, 0.8)
                        ))
                    self.enemies.remove(enemy)

            for particle in self.all_particles[:]:
                particle.update(dt)
                if not particle.alive:
                    self.all_particles.remove(particle)

            self.check_enemy_collisions()

            if len(self.enemies) == 0 and self.enemies_spawned >= self.enemies_per_wave:
                if self.wave_delay_timer <= 0 and self.wave_timer <= 0:
                    self.wave += 1
                    if self.wave > TOTAL_WAVES:
                        self.state = "victory"
                    else:
                        self.state = "upgrade"
                        self.generate_upgrades()

            if self.shake_amount > 0:
                self.shake_amount *= 0.9
                if self.shake_amount < 0.5:
                    self.shake_amount = 0
                self.shake_offset[0] = random.uniform(-self.shake_amount, self.shake_amount)
                self.shake_offset[1] = random.uniform(-self.shake_amount, self.shake_amount)
            else:
                self.shake_offset = [0, 0]

        elif self.state == "gameover":
            self.game_over_delay -= dt
            for particle in self.all_particles[:]:
                particle.update(dt)
                if not particle.alive:
                    self.all_particles.remove(particle)

        elif self.state == "victory":
            for particle in self.all_particles[:]:
                particle.update(dt)
                if not particle.alive:
                    self.all_particles.remove(particle)
            if random.random() < 0.1 and self.player:
                a = random.uniform(0, math.pi * 2)
                r = random.uniform(30, 100)
                self.all_particles.append(Particle(
                    self.player.x + math.cos(a) * r,
                    self.player.y + math.sin(a) * r,
                    math.cos(a) * random.uniform(-0.5, 0.5),
                    math.sin(a) * random.uniform(-0.5, 0.5),
                    random.choice([NEON_CYAN, NEON_YELLOW, NEON_MAGENTA]),
                    random.uniform(1.0, 2.0)
                ))

    def check_enemy_collisions(self):
        if not self.player or not self.player.alive:
            return

        for enemy in self.enemies[:]:
            if not enemy.alive:
                continue
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < self.player.radius + enemy.radius:
                self.player.take_damage(enemy.damage)
                self.shake_amount = max(self.shake_amount, 5)

                kb_angle = math.atan2(self.player.y - enemy.y, self.player.x - enemy.x)
                kb = 15
                if self.player.weakness_multiplier < 1.0:
                    kb *= 1.5
                self.player.x += math.cos(kb_angle) * kb
                self.player.y += math.sin(kb_angle) * kb
                self.player.x = max(self.arena_rect.left + self.player.radius,
                                     min(self.arena_rect.right - self.player.radius, self.player.x))
                self.player.y = max(self.arena_rect.top + self.player.radius,
                                     min(self.arena_rect.bottom - self.player.radius, self.player.y))

                for _ in range(5):
                    a = random.uniform(0, math.pi * 2)
                    s = random.uniform(2, 4)
                    self.all_particles.append(Particle(
                        self.player.x, self.player.y,
                        math.cos(a) * s,
                        math.sin(a) * s,
                        NEON_RED,
                        random.uniform(0.2, 0.5)
                    ))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            self.touch.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if self.state == "start":
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                    return

                if self.state == "playing":
                    if event.key == pygame.K_q:
                        if self.player and self.player.can_attack():
                            self.player.attack(self.enemies, self.all_particles)
                    elif event.key == pygame.K_e:
                        if self.player and self.player.can_shield():
                            self.player.activate_shield(self.all_particles)
                    elif event.key == pygame.K_r:
                        if self.player and self.player.can_teleport():
                            self.player.teleport(self.arena_rect, self.all_particles)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "start"

                if self.state == "upgrade":
                    if event.key == pygame.K_1 and len(self.upgrade_options) > 0:
                        self.player.apply_upgrade(self.upgrade_options[0][0])
                        self.wave_delay_timer = WAVE_DELAY
                        self.state = "playing"
                    elif event.key == pygame.K_2 and len(self.upgrade_options) > 1:
                        self.player.apply_upgrade(self.upgrade_options[1][0])
                        self.wave_delay_timer = WAVE_DELAY
                        self.state = "playing"
                    elif event.key == pygame.K_3 and len(self.upgrade_options) > 2:
                        self.player.apply_upgrade(self.upgrade_options[2][0])
                        self.wave_delay_timer = WAVE_DELAY
                        self.state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "start"

                if self.state in ("gameover", "victory"):
                    if event.key == pygame.K_r:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "start"

    def draw_background(self):
        self.screen.fill(DARK_BG)
        self.screen.blit(self.grid_surf, (0, 0))

        if self.player and self.player.shield_active:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(20)
            overlay.fill((255, 255, 0))
            self.screen.blit(overlay, (0, 0))

    def draw(self):
        self.draw_background()

        if self.state == "start":
            self.start_screen.draw(self.screen)
            self.touch.draw(self.screen)
            pygame.display.flip()
            return

        camera_x = 0
        camera_y = 0
        if self.shake_amount > 0:
            camera_x += self.shake_offset[0]
            camera_y += self.shake_offset[1]

        for particle in self.all_particles:
            particle.draw(self.screen, camera_x, camera_y)

        for enemy in self.enemies:
            enemy.draw(self.screen, camera_x, camera_y)

        if self.player:
            self.player.draw(self.screen, camera_x, camera_y)

        self.hud.draw(self.screen, self.player, self.wave, TOTAL_WAVES, self.state)

        if self.state == "upgrade":
            self.draw_upgrade_screen()

        if self.state == "playing" and self.wave_delay_timer > 0:
            draw_text(self.screen, f"WAVE {self.wave}",
                     FONT_XL, NEON_YELLOW, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
            draw_text(self.screen, "PREPARE",
                     FONT_MD, NEON_CYAN, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        if self.state in ("playing", "upgrade"):
            self.touch.draw(self.screen)

        scanline = pygame.Surface((WINDOW_WIDTH, 2))
        scanline.set_alpha(20)
        scanline.fill((0, 0, 0))
        for sy in range(0, WINDOW_HEIGHT, 3):
            self.screen.blit(scanline, (0, sy))

        corner_vignette = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for i in range(100, 0, -1):
            alpha = max(0, 2 - i // 30)
            pygame.draw.rect(corner_vignette, (0, 0, 0, alpha),
                           (i, i, WINDOW_WIDTH - i * 2, WINDOW_HEIGHT - i * 2), 1)
        self.screen.blit(corner_vignette, (0, 0))

        pygame.display.flip()

    def draw_upgrade_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        center_x = WINDOW_WIDTH // 2
        start_y = WINDOW_HEIGHT // 2 - 90

        draw_text(self.screen, "LEVEL UP!", FONT_XL, NEON_YELLOW, center_x, start_y)
        draw_text(self.screen, "Choose an upgrade:", FONT_MD, WHITE, center_x, start_y + 60)

        box_w = 300
        box_h = 140
        gap = 30
        total_w = len(self.upgrade_options) * box_w + (len(self.upgrade_options) - 1) * gap
        start_x = center_x - total_w // 2

        for i, (uid, name, desc, icon) in enumerate(self.upgrade_options):
            bx = start_x + i * (box_w + gap)
            by = start_y + 100

            pygame.draw.rect(self.screen, (20, 25, 40), (bx, by, box_w, box_h))
            pygame.draw.rect(self.screen, NEON_CYAN, (bx, by, box_w, box_h), 2)

            draw_char(self.screen, icon, NEON_CYAN, bx + box_w // 2, by + 30)
            draw_text(self.screen, name, FONT_SM, NEON_GREEN, bx + box_w // 2, by + 55)
            draw_text(self.screen, desc, pygame.font.Font(None, 18), WHITE, bx + box_w // 2, by + 80)
            draw_text(self.screen, f"[{i+1}]", FONT_SM, GRAY, bx + box_w // 2, by + box_h - 15)

    async def run(self):
        print("ROGALIK: The Ascension - Web version")
        while self.running:
            now = pygame.time.get_ticks()
            dt = (now - self.last_time) / 1000.0
            self.last_time = now
            if dt > 0.05:
                dt = 0.05

            self.handle_events()
            self.update(dt)
            self.draw()

            await asyncio.sleep(0)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    asyncio.run(Game().run())
