import pygame
import math
from settings import *

_ASCII_FONT = None
_FONT_W = 12
_FONT_H = 18

def init_ascii_font(size=20):
    global _ASCII_FONT, _FONT_W, _FONT_H
    try:
        _ASCII_FONT = pygame.font.SysFont('Courier New', size, bold=False)
    except:
        _ASCII_FONT = pygame.font.Font(None, size)
    _FONT_W, _FONT_H = _ASCII_FONT.size('@')

def get_font():
    global _ASCII_FONT
    if _ASCII_FONT is None:
        init_ascii_font()
    return _ASCII_FONT

def draw_char(screen, char, color, x, y, centered=True):
    f = get_font()
    surf = f.render(char, True, color)
    if centered:
        screen.blit(surf, (x - surf.get_width() // 2, y - surf.get_height() // 2))
    else:
        screen.blit(surf, (x, y))

def draw_chars(screen, string, color, x, y, centered=False):
    f = get_font()
    surf = f.render(string, True, color)
    if centered:
        screen.blit(surf, (x - surf.get_width() // 2, y - surf.get_height() // 2))
    else:
        screen.blit(surf, (x, y))

def draw_box(screen, x, y, w, h, color):
    tl = '+'
    tr = '+'
    bl = '+'
    br = '+'
    h_line = '-'
    v_line = '|'

    f = get_font()
    surf = pygame.Surface((w * _FONT_W, h * _FONT_H), pygame.SRCALPHA)

    for px in range(1, w - 1):
        draw_char(surf, h_line, color, (px + 0.5) * _FONT_W, 0.5 * _FONT_H, False)
        draw_char(surf, h_line, color, (px + 0.5) * _FONT_W, (h - 0.5) * _FONT_H, False)

    for py in range(1, h - 1):
        draw_char(surf, v_line, color, 0.5 * _FONT_W, (py + 0.5) * _FONT_H, False)
        draw_char(surf, v_line, color, (w - 0.5) * _FONT_W, (py + 0.5) * _FONT_H, False)

    draw_char(surf, tl, color, 0.5 * _FONT_W, 0.5 * _FONT_H, False)
    draw_char(surf, tr, color, (w - 0.5) * _FONT_W, 0.5 * _FONT_H, False)
    draw_char(surf, bl, color, 0.5 * _FONT_W, (h - 0.5) * _FONT_H, False)
    draw_char(surf, br, color, (w - 0.5) * _FONT_W, (h - 0.5) * _FONT_H, False)

    screen.blit(surf, (x, y))

CHAR_BLOCKS = [' ', '\u2591', '\u2592', '\u2593', '\u2588']

def draw_bar(screen, x, y, w, pct, fg, bg=(20, 20, 30)):
    filled = int(w * max(0, min(1, pct)))
    text = ''
    for i in range(w):
        if i < filled:
            text += '\u2588'
        else:
            text += '\u2591'
    draw_chars(screen, text, fg, x, y, centered=False)

def draw_glow(screen, char, color, x, y):
    draw_char(screen, char, tuple(min(255, c * 2) for c in color[:3]), x, y)
