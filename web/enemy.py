import pygame
import math
import random
from settings import *
from particles import Particle
from renderer import draw_char


class Enemy:
    def __init__(self, x, y, hp, damage, speed, radius, color, char):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.speed = speed
        self.radius = radius
        self.color = color
        self.char = char
        self.alive = True
        self.vx = 0
        self.vy = 0
        self.hit_flash = 0
        self.spawn_anim = 1.0

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = 0.15
        if self.hp <= 0:
            self.alive = False

    def update(self, dt, player, arena_rect, enemies, particles):
        if not self.alive:
            return
        self.spawn_anim = max(0, self.spawn_anim - dt * 2)
        self.hit_flash = max(0, self.hit_flash - dt)

    def in_range_of_player(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        return math.sqrt(dx * dx + dy * dy)

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if self.hit_flash > 0:
            draw_color = WHITE
        else:
            draw_color = self.color

        if self.spawn_anim > 0:
            alpha = int(100 * (1 - self.spawn_anim))
            draw_char(screen, self.char, tuple(min(255, c) for c in (*draw_color[:3], alpha)), sx, sy)

        hp_pct = self.hp / self.max_hp if self.max_hp > 0 else 0
        if hp_pct < 0.5 and (int(pygame.time.get_ticks() / 200) % 2 == 0):
            draw_char(screen, self.char, WHITE, sx, sy)
        else:
            draw_char(screen, self.char, draw_color, sx, sy)


class LightEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, LIGHT_HP, LIGHT_DAMAGE, LIGHT_SPEED, LIGHT_RADIUS, (180, 100, 255), 'o')
        self.float_phase = random.uniform(0, math.pi * 2)
        self.rise_speed = random.uniform(0.5, 1.5)
        self.float_offset = 0

    def update(self, dt, player, arena_rect, enemies, particles):
        super().update(dt, player, arena_rect, enemies, particles)
        if not self.alive:
            return

        self.float_phase += dt * 2
        self.float_offset = math.sin(self.float_phase) * 20

        target_x = player.x
        target_y = player.y
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed * dt * 60
            self.y += (dy / dist) * self.speed * dt * 60 + self.rise_speed * dt * 10

        self.x = max(arena_rect.left + self.radius, min(arena_rect.right - self.radius, self.x))
        self.y = max(arena_rect.top + self.radius, min(arena_rect.bottom - self.radius, self.y))

        if self.float_phase % (math.pi * 2) < 0.3 and random.random() < 0.3:
            particles.append(Particle(
                self.x + random.uniform(-5, 5),
                self.y + random.uniform(-5, 5),
                random.uniform(-0.3, 0.3),
                random.uniform(-1, -0.3),
                (180, 100, 255),
                random.uniform(0.3, 0.6)
            ))


class MediumEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, MEDIUM_HP, MEDIUM_DAMAGE, MEDIUM_SPEED, MEDIUM_RADIUS, (255, 100, 50), '%')
        self.orbit_center_x = x
        self.orbit_center_y = y
        self.orbit_angle = random.uniform(0, math.pi * 2)
        self.orbit_radius = MEDIUM_ORBIT_RADIUS
        self.orbit_speed = MEDIUM_ORBIT_SPEED
        self.phase = random.uniform(0, math.pi * 2)
        self.pulse_timer = 0

    def update(self, dt, player, arena_rect, enemies, particles):
        super().update(dt, player, arena_rect, enemies, particles)
        if not self.alive:
            return

        self.phase += dt * 2
        self.pulse_timer += dt

        self.orbit_angle += self.orbit_speed * dt

        dx_from_center = player.x - self.orbit_center_x
        dy_from_center = player.y - self.orbit_center_y
        self.orbit_center_x += dx_from_center * 0.002 * dt * 60
        self.orbit_center_y += dy_from_center * 0.002 * dt * 60

        self.orbit_center_x = max(arena_rect.left + self.orbit_radius,
                                   min(arena_rect.right - self.orbit_radius, self.orbit_center_x))
        self.orbit_center_y = max(arena_rect.top + self.orbit_radius,
                                   min(arena_rect.bottom - self.orbit_radius, self.orbit_center_y))

        current_orbit_radius = self.orbit_radius + math.sin(self.phase) * 20
        self.x = self.orbit_center_x + math.cos(self.orbit_angle) * current_orbit_radius
        self.y = self.orbit_center_y + math.sin(self.orbit_angle) * current_orbit_radius


class HeavyEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, HEAVY_HP, HEAVY_DAMAGE, HEAVY_SPEED, HEAVY_RADIUS, (255, 20, 80), 'H')
        self.clone_timer = 0
        self.clone_interval = HEAVY_CLONE_INTERVAL
        self.active_clones = []

    def update(self, dt, player, arena_rect, enemies, particles):
        super().update(dt, player, arena_rect, enemies, particles)
        if not self.alive:
            return

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed * dt * 60
            self.y += (dy / dist) * self.speed * dt * 60

        self.x = max(arena_rect.left + self.radius, min(arena_rect.right - self.radius, self.x))
        self.y = max(arena_rect.top + self.radius, min(arena_rect.bottom - self.radius, self.y))

        self.clone_timer += dt
        if self.clone_timer >= self.clone_interval:
            self.clone_timer = 0
            clone = HeavyClone(self, arena_rect, player)
            if clone:
                enemies.append(clone)
                for _ in range(8):
                    a = random.uniform(0, math.pi * 2)
                    particles.append(Particle(
                        self.x + math.cos(a) * 10,
                        self.y + math.sin(a) * 10,
                        math.cos(a) * random.uniform(1, 3),
                        math.sin(a) * random.uniform(1, 3),
                        (255, 20, 80),
                        random.uniform(0.3, 0.6)
                    ))

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)
        if not self.alive:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        glow_char = 'X' if pulse > 0.5 else 'H'
        draw_char(screen, glow_char, tuple(int(c * (0.5 + pulse * 0.5)) for c in self.color[:3]), sx - 10, sy - 14)


class HeavyClone(Enemy):
    def __init__(self, parent, arena_rect, player):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(80, 150)
        cx = parent.x + math.cos(angle) * dist
        cy = parent.y + math.sin(angle) * dist
        cx = max(arena_rect.left + HEAVY_RADIUS, min(arena_rect.right - HEAVY_RADIUS, cx))
        cy = max(arena_rect.top + HEAVY_RADIUS, min(arena_rect.bottom - HEAVY_RADIUS, cy))
        super().__init__(cx, cy, HEAVY_HP // 2, HEAVY_DAMAGE, HEAVY_SPEED * 1.3, HEAVY_RADIUS - 3, (200, 0, 60), 'h')
        self.lifetime = HEAVY_CLONE_DURATION
        self.age = 0
        self.wobble_phase = random.uniform(0, math.pi * 2)

    def update(self, dt, player, arena_rect, enemies, particles):
        super().update(dt, player, arena_rect, enemies, particles)
        if not self.alive:
            return
        self.age += dt
        self.wobble_phase += dt * 4
        if self.age >= self.lifetime:
            self.alive = False
            for _ in range(6):
                a = random.uniform(0, math.pi * 2)
                particles.append(Particle(
                    self.x, self.y,
                    math.cos(a) * random.uniform(1, 3),
                    math.sin(a) * random.uniform(1, 3),
                    (200, 0, 60),
                    random.uniform(0.2, 0.5)
                ))
            return

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            wobble = math.sin(self.wobble_phase) * 1.5
            self.x += (dx / dist) * self.speed * dt * 60 + math.cos(self.wobble_phase) * wobble * dt * 60
            self.y += (dy / dist) * self.speed * dt * 60 + math.sin(self.wobble_phase) * wobble * dt * 60

        self.x = max(arena_rect.left + self.radius, min(arena_rect.right - self.radius, self.x))
        self.y = max(arena_rect.top + self.radius, min(arena_rect.bottom - self.radius, self.y))

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        flicker = int(self.age * 10) % 2 == 0
        if flicker:
            return
        super().draw(screen, camera_x, camera_y)
