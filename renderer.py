import pygame
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



def draw_bar(screen, x, y, w, pct, fg, bg=(20, 20, 30)):
    filled = int(w * max(0, min(1, pct)))
    text = ''
    for i in range(w):
        if i < filled:
            text += '\u2588'
        else:
            text += '\u2591'
    draw_chars(screen, text, fg, x, y, centered=False)


