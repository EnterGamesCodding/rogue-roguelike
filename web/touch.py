import pygame
import math
from settings import *

BTN_RADIUS = 30
BTN_MARGIN = 20
JOYSTICK_RADIUS = 50

class TouchControls:
    def __init__(self):
        self.keys = {
            pygame.K_w: False,
            pygame.K_s: False,
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_q: False,
            pygame.K_e: False,
            pygame.K_r: False,
            pygame.K_SPACE: False,
        }
        self.joystick_center = (BTN_MARGIN + JOYSTICK_RADIUS, WINDOW_HEIGHT - BTN_MARGIN - JOYSTICK_RADIUS)
        self.joystick_touch = -1
        self.joystick_offset = [0, 0]

        self.btn_q = self._btn_rect(WINDOW_WIDTH - BTN_MARGIN - BTN_RADIUS * 3 - BTN_MARGIN)
        self.btn_e = self._btn_rect(WINDOW_WIDTH - BTN_MARGIN - BTN_RADIUS * 2 - BTN_MARGIN // 2)
        self.btn_r = self._btn_rect(WINDOW_WIDTH - BTN_MARGIN - BTN_RADIUS)
        self.btn_start = pygame.Rect(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 + 100, 120, 40)

        self.buttons = {
            'q': {'rect': self.btn_q, 'key': pygame.K_q, 'label': 'Q'},
            'e': {'rect': self.btn_e, 'key': pygame.K_e, 'label': 'E'},
            'r': {'rect': self.btn_r, 'key': pygame.K_r, 'label': 'R'},
        }

    def _btn_rect(self, cx):
        return pygame.Rect(cx - BTN_RADIUS, WINDOW_HEIGHT - BTN_MARGIN - BTN_RADIUS, BTN_RADIUS * 2, BTN_RADIUS * 2)

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            fx, fy = int(event.x * WINDOW_WIDTH), int(event.y * WINDOW_HEIGHT)
            if self._in_joystick_area(fx, fy):
                self.joystick_touch = event.finger_id
                self._update_joystick(fx, fy)
            for bid, btn in self.buttons.items():
                if btn['rect'].collidepoint(fx, fy):
                    self.keys[btn['key']] = True

        elif event.type == pygame.FINGERMOTION:
            if event.finger_id == self.joystick_touch:
                fx, fy = int(event.x * WINDOW_WIDTH), int(event.y * WINDOW_HEIGHT)
                self._update_joystick(fx, fy)

        elif event.type == pygame.FINGERUP:
            if event.finger_id == self.joystick_touch:
                self.joystick_touch = -1
                self.joystick_offset = [0, 0]
                self.keys[pygame.K_w] = False
                self.keys[pygame.K_s] = False
                self.keys[pygame.K_a] = False
                self.keys[pygame.K_d] = False
            for bid, btn in self.buttons.items():
                self.keys[btn['key']] = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self._in_joystick_area(mx, my):
                self.joystick_touch = 0
                self._update_joystick(mx, my)
            for bid, btn in self.buttons.items():
                if btn['rect'].collidepoint(mx, my):
                    self.keys[btn['key']] = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.joystick_touch == 0:
                self.joystick_touch = -1
                self.joystick_offset = [0, 0]
                self.keys[pygame.K_w] = False
                self.keys[pygame.K_s] = False
                self.keys[pygame.K_a] = False
                self.keys[pygame.K_d] = False
            for bid, btn in self.buttons.items():
                self.keys[btn['key']] = False

        elif event.type == pygame.MOUSEMOTION:
            if self.joystick_touch == 0:
                self._update_joystick(*event.pos)

    def _in_joystick_area(self, x, y):
        dx = x - self.joystick_center[0]
        dy = y - self.joystick_center[1]
        return dx * dx + dy * dy < (JOYSTICK_RADIUS * 3) ** 2

    def _update_joystick(self, x, y):
        dx = x - self.joystick_center[0]
        dy = y - self.joystick_center[1]
        dist = math.sqrt(dx * dx + dy * dy)
        max_dist = JOYSTICK_RADIUS
        if dist > max_dist:
            dx = dx / dist * max_dist
            dy = dy / dist * max_dist
        self.joystick_offset = [dx, dy]

        deadzone = 10
        self.keys[pygame.K_w] = dy < -deadzone
        self.keys[pygame.K_s] = dy > deadzone
        self.keys[pygame.K_a] = dx < -deadzone
        self.keys[pygame.K_d] = dx > deadzone

    def get_pressed(self):
        return self.keys

    def draw(self, screen):
        alpha = 80
        jx, jy = self.joystick_center
        joy_surf = pygame.Surface((JOYSTICK_RADIUS * 4, JOYSTICK_RADIUS * 4), pygame.SRCALPHA)
        pygame.draw.circle(joy_surf, (*NEON_CYAN[:3], alpha // 2), (JOYSTICK_RADIUS * 2, JOYSTICK_RADIUS * 2), JOYSTICK_RADIUS + 10, 2)
        screen.blit(joy_surf, (jx - JOYSTICK_RADIUS * 2, jy - JOYSTICK_RADIUS * 2))
        pygame.draw.circle(screen, (*NEON_CYAN[:3], alpha), (jx, jy), JOYSTICK_RADIUS, 2)
        knob_x = int(jx + self.joystick_offset[0])
        knob_y = int(jy + self.joystick_offset[1])
        pygame.draw.circle(screen, (*NEON_CYAN[:3], alpha + 40), (knob_x, knob_y), 12)

        for bid, btn in self.buttons.items():
            bx, by = btn['rect'].center
            pressed = self.keys[btn['key']]
            color = NEON_YELLOW if pressed else (*NEON_CYAN[:3], alpha)
            if not pressed:
                c = tuple(min(255, c) for c in color[:3])
                pygame.draw.circle(screen, c, (bx, by), BTN_RADIUS, 2)
            else:
                s = pygame.Surface((BTN_RADIUS * 2, BTN_RADIUS * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*NEON_YELLOW[:3], 100), (BTN_RADIUS, BTN_RADIUS), BTN_RADIUS)
                screen.blit(s, (bx - BTN_RADIUS, by - BTN_RADIUS))

            label_surf = pygame.font.Font(None, 28).render(btn['label'], True, (*WHITE[:3], 200))
            screen.blit(label_surf, (bx - label_surf.get_width() // 2, by - label_surf.get_height() // 2))
