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


