import pygame
import math
import random
from settings import *
from renderer import draw_char

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True
        self.chars = ['.', '*', '+', '\u2219', '\u00B7']

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        pct = self.lifetime / self.max_lifetime
        char_idx = min(len(self.chars) - 1, int(pct * len(self.chars)))
        char = self.chars[char_idx]
        color = tuple(min(255, int(c * (0.3 + pct * 0.7))) for c in self.color[:3])
        draw_char(screen, char, color, sx, sy)


class Emitter:
    def __init__(self):
        self.particles = []

    def emit_circle(self, x, y, color, count=10, speed=3, lifetime=0.5):
        for _ in range(count):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(1, speed)
            self.particles.append(Particle(
                x, y,
                math.cos(a) * s,
                math.sin(a) * s,
                color,
                random.uniform(lifetime * 0.5, lifetime)
            ))

    def emit_burst(self, x, y, color, count=15, speed=5, lifetime=0.8):
        for _ in range(count):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(1, speed)
            self.particles.append(Particle(
                x, y,
                math.cos(a) * s,
                math.sin(a) * s,
                color,
                random.uniform(lifetime * 0.3, lifetime)
            ))

    def emit_trail(self, x, y, color, count=2):
        for _ in range(count):
            self.particles.append(Particle(
                x + random.uniform(-3, 3),
                y + random.uniform(-3, 3),
                random.uniform(-0.5, 0.5),
                random.uniform(-0.5, 0.5),
                color,
                random.uniform(0.2, 0.4)
            ))

    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if not p.alive:
                self.particles.remove(p)

    def draw(self, screen, camera_x, camera_y):
        for p in self.particles:
            p.draw(screen, camera_x, camera_y)

    def clear(self):
        self.particles.clear()
