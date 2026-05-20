import pygame
import math
import random
from settings import *
from particles import Particle
from renderer import draw_char

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.battery = BATTERY_MAX
        self.max_battery = BATTERY_MAX
        self.speed = PLAYER_SPEED
        self.radius = PLAYER_RADIUS
        self.alive = True
        self.angle = 0

        self.attack_timer = 0
        self.attack_cooldown = ATTACK_COOLDOWN
        self.attack_active = False
        self.attack_anim_timer = 0
        self.attack_hit_enemies = []
        self.attack_damage = ATTACK_DAMAGE
        self.attack_range = ATTACK_RANGE
        self.attack_arc = ATTACK_ARC
        self.attack_knockback = ATTACK_KNOCKBACK
        self.attack_hp_cost = ATTACK_HP_COST

        self.shield_active = False
        self.shield_timer = 0
        self.shield_max_duration = SHIELD_DURATION
        self.shield_cooldown_timer = 0
        self.shield_cooldown_max = SHIELD_COOLDOWN

        self.teleport_cooldown_timer = 0
        self.teleport_cooldown_max = TELEPORT_COOLDOWN
        self.weakness_timer = 0
        self.weakness_duration = TELEPORT_WEAKNESS_DURATION
        self.weakness_multiplier = 1.0
        self.teleport_flash_timer = 0
        self.teleport_weakness_pct = TELEPORT_WEAKNESS

        self.battery_drain_mod = 1.0

        self.invulnerable = False
        self.invulnerable_timer = 0
        self.hit_flash_timer = 0

        self.trail_positions = []
        self.trail_timer = 0

    def update(self, dt, keys, enemies, arena_rect, particles):
        if not self.alive:
            return

        effective_dt = dt

        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1

        if dx != 0 or dy != 0:
            magnitude = math.sqrt(dx * dx + dy * dy)
            dx /= magnitude
            dy /= magnitude
            self.angle = math.atan2(dy, dx)

        move_speed = self.speed * effective_dt * 60
        self.x += dx * move_speed
        self.y += dy * move_speed

        self.x = max(arena_rect.left + self.radius, min(arena_rect.right - self.radius, self.x))
        self.y = max(arena_rect.top + self.radius, min(arena_rect.bottom - self.radius, self.y))

        self.trail_timer += effective_dt
        if self.trail_timer > 0.05:
            self.trail_timer = 0
            self.trail_positions.append((self.x, self.y))
            if len(self.trail_positions) > 15:
                self.trail_positions.pop(0)

        self.battery = min(self.max_battery, self.battery + BATTERY_REGEN * effective_dt)
        self.battery -= BATTERY_DRAIN * effective_dt * self.battery_drain_mod

        self.attack_timer = max(0, self.attack_timer - effective_dt)
        self.shield_cooldown_timer = max(0, self.shield_cooldown_timer - effective_dt)
        self.teleport_cooldown_timer = max(0, self.teleport_cooldown_timer - effective_dt)

        if self.shield_active:
            self.shield_timer -= effective_dt
            if self.shield_timer <= 0:
                self.shield_active = False
                self.shield_cooldown_timer = self.shield_cooldown_max

        if self.attack_active:
            self.attack_anim_timer -= effective_dt
            if self.attack_anim_timer <= 0:
                self.attack_active = False
                self.attack_hit_enemies.clear()

        if self.weakness_timer > 0:
            self.weakness_timer -= effective_dt
            if self.weakness_timer <= 0:
                self.weakness_multiplier = 1.0

        if self.invulnerable:
            self.invulnerable_timer -= effective_dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= effective_dt

        if self.teleport_flash_timer > 0:
            self.teleport_flash_timer -= effective_dt

    def attack(self, enemies, particles):
        if self.attack_timer > 0 or not self.alive:
            return

        self.hp = max(0, self.hp - self.attack_hp_cost)
        self.attack_timer = self.attack_cooldown
        self.attack_active = True
        self.attack_anim_timer = 0.3
        self.attack_hit_enemies.clear()

        cx = self.x + math.cos(self.angle) * 20
        cy = self.y + math.sin(self.angle) * 20

        for enemy in enemies[:]:
            ex, ey = enemy.x, enemy.y
            dist = math.sqrt((ex - cx) ** 2 + (ey - cy) ** 2)
            if dist > self.attack_range:
                continue
            angle_to_enemy = math.atan2(ey - cy, ex - cx)
            angle_diff = abs(math.atan2(math.sin(angle_to_enemy - self.angle), math.cos(angle_to_enemy - self.angle)))
            if angle_diff > math.radians(self.attack_arc / 2):
                continue

            dmg = self.attack_damage * self.weakness_multiplier
            enemy.take_damage(dmg)
            self.attack_hit_enemies.append(enemy)

            kb_angle = math.atan2(ey - self.y, ex - self.x)
            enemy.vx += math.cos(kb_angle) * self.attack_knockback
            enemy.vy += math.sin(kb_angle) * self.attack_knockback

            for _ in range(8):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 5)
                particles.append(Particle(
                    ex, ey,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    random.choice([NEON_CYAN, WHITE]),
                    random.uniform(0.2, 0.5)
                ))

        for _ in range(15):
            arc_start = self.angle - math.radians(self.attack_arc / 2)
            arc_end = self.angle + math.radians(self.attack_arc / 2)
            a = random.uniform(arc_start, arc_end)
            r = random.uniform(10, self.attack_range)
            px = self.x + math.cos(a) * r
            py = self.y + math.sin(a) * r
            particles.append(Particle(
                px, py,
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                NEON_CYAN,
                random.uniform(0.3, 0.8)
            ))

    def activate_shield(self, particles):
        if self.shield_active or self.shield_cooldown_timer > 0 or not self.alive:
            return False
        self.shield_active = True
        self.shield_timer = self.shield_max_duration
        for _ in range(20):
            a = random.uniform(0, math.pi * 2)
            r = random.uniform(self.radius, self.radius + 30)
            px = self.x + math.cos(a) * r
            py = self.y + math.sin(a) * r
            particles.append(Particle(
                px, py,
                math.cos(a) * random.uniform(-0.5, 0.5),
                math.sin(a) * random.uniform(-0.5, 0.5),
                NEON_YELLOW,
                random.uniform(0.5, 1.5)
            ))
        return True

    def teleport(self, arena_rect, particles):
        if self.teleport_cooldown_timer > 0 or not self.alive:
            return False

        for _ in range(20):
            nx = random.uniform(arena_rect.left + self.radius, arena_rect.right - self.radius)
            ny = random.uniform(arena_rect.top + self.radius, arena_rect.bottom - self.radius)

            for _ in range(10):
                a = random.uniform(0, math.pi * 2)
                r = random.uniform(5, 15)
                particles.append(Particle(
                    self.x + math.cos(a) * r,
                    self.y + math.sin(a) * r,
                    random.uniform(-2, 2),
                    random.uniform(-2, 2),
                    NEON_MAGENTA,
                    random.uniform(0.3, 0.8)
                ))

            old_x, old_y = self.x, self.y
            self.x = nx
            self.y = ny
            self.teleport_cooldown_timer = self.teleport_cooldown_max
            self.weakness_timer = self.weakness_duration
            self.weakness_multiplier = 1.0 - self.teleport_weakness_pct
            self.teleport_flash_timer = 0.3

            for _ in range(10):
                a = random.uniform(0, math.pi * 2)
                r = random.uniform(5, 15)
                particles.append(Particle(
                    self.x + math.cos(a) * r,
                    self.y + math.sin(a) * r,
                    random.uniform(-2, 2),
                    random.uniform(-2, 2),
                    NEON_MAGENTA,
                    random.uniform(0.3, 0.8)
                ))
            return True
        return False

    def take_damage(self, amount):
        if self.invulnerable or not self.alive:
            return 0
        if self.shield_active:
            return 0

        if self.battery > 0:
            self.battery = max(0, self.battery - amount)
            self.invulnerable = True
            self.invulnerable_timer = 0.2
            self.hit_flash_timer = 0.1
            return 0
        else:
            actual_damage = amount
            self.hp = max(0, self.hp - actual_damage)
            self.invulnerable = True
            self.invulnerable_timer = 0.3
            self.hit_flash_timer = 0.2
            if self.hp <= 0:
                self.alive = False
            return actual_damage

    def apply_upgrade(self, upgrade_id):
        if upgrade_id == "dmg":
            self.attack_damage += 10
        elif upgrade_id == "range":
            self.attack_range += 30
        elif upgrade_id == "atk_cd":
            self.attack_cooldown = max(0.3, self.attack_cooldown - 0.3)
        elif upgrade_id == "hp_cost":
            from settings import BATTERY_REGEN
            self.battery = min(self.max_battery, self.battery + 10)
        elif upgrade_id == "shd_dur":
            self.shield_max_duration += 2.0
        elif upgrade_id == "shd_cd":
            self.shield_cooldown_max = max(2.0, self.shield_cooldown_max - 2.0)
        elif upgrade_id == "tp_cd":
            self.teleport_cooldown_max = max(1.0, self.teleport_cooldown_max - 1.5)
        elif upgrade_id == "tp_weak":
            self.teleport_weakness_pct = max(0.0, self.teleport_weakness_pct - 0.1)
        elif upgrade_id == "speed":
            self.speed += 0.5
        elif upgrade_id == "hp_max":
            self.max_hp += 20
            self.hp = min(self.hp + 20, self.max_hp)
        elif upgrade_id == "regen":
            self.hp = min(self.hp + 2, self.max_hp)
        elif upgrade_id == "battery":
            self.max_battery += 25
            self.battery = min(self.battery + 25, self.max_battery)

    def can_attack(self):
        return self.attack_timer <= 0 and self.alive

    def can_shield(self):
        return not self.shield_active and self.shield_cooldown_timer <= 0 and self.alive

    def can_teleport(self):
        return self.teleport_cooldown_timer <= 0 and self.alive

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return

        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if self.weakness_multiplier < 1.0:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            body_color = tuple(int(NEON_MAGENTA[i] * pulse + NEON_CYAN[i] * (1 - pulse)) for i in range(3))
        else:
            body_color = NEON_CYAN

        if self.hit_flash_timer > 0:
            if int(self.hit_flash_timer * 20) % 2 == 0:
                body_color = WHITE

        for i, (tx, ty) in enumerate(self.trail_positions):
            alpha = 50 + int(80 * (i / len(self.trail_positions)))
            tsx = int(tx - camera_x)
            tsy = int(ty - camera_y)
            draw_char(screen, '.', tuple(min(255, c) for c in (*body_color[:3], alpha)), tsx, tsy)

        if self.teleport_flash_timer > 0:
            draw_char(screen, '*', NEON_MAGENTA, sx, sy)

        draw_char(screen, '@', body_color, sx, sy)

        if self.shield_active:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.004))
            shield_char = 'O' if pulse > 0.5 else '#'
            shield_color = tuple(int(NEON_YELLOW[i] * (0.4 + pulse * 0.6)) for i in range(3))
            offset = 14
            for a_offset in [0, 45, 90, 135, 180, 225, 270, 315]:
                a = math.radians(a_offset)
                dx = int(math.cos(a) * offset)
                dy = int(math.sin(a) * offset)
                draw_char(screen, shield_char, shield_color, sx + dx, sy + dy)

        if self.attack_active:
            anim_pct = self.attack_anim_timer / 0.3
            count = int(7 * anim_pct)
            for i in range(count):
                a = self.angle - math.radians(self.attack_arc / 2) + math.radians(self.attack_arc * i / max(1, count - 1))
                r = 30 + int(70 * (1 - anim_pct))
                px = sx + int(math.cos(a) * r)
                py = sy + int(math.sin(a) * r)
                draw_char(screen, '#', NEON_CYAN, px, py)
