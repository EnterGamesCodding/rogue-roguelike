import pygame
import math
from settings import *
from renderer import draw_char, draw_chars, draw_bar

pygame.font.init()
FONT_SM = pygame.font.Font(None, 22)
FONT_MD = pygame.font.Font(None, 32)
FONT_LG = pygame.font.Font(None, 44)
FONT_XL = pygame.font.Font(None, 64)


def draw_text(screen, text, font, color, x, y, center=True):
    surf = font.render(text, True, color)
    if center:
        rect = surf.get_rect(center=(x, y))
    else:
        rect = surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)


class HUD:
    def draw(self, screen, player, wave, total_waves, game_state):
        if game_state == "gameover":
            self.draw_game_over(screen, wave)
            return
        if game_state == "victory":
            self.draw_victory(screen)
            return

        margin = 16
        bar_len = 15

        hp_x = margin
        hp_y = 10
        draw_chars(screen, "HP:", NEON_GREEN, hp_x, hp_y, centered=False)
        hp_pct = player.hp / player.max_hp if player.max_hp > 0 else 0
        draw_bar(screen, hp_x + 28, hp_y, bar_len, hp_pct, NEON_GREEN)
        draw_chars(screen, f"{int(player.hp)}%", WHITE, hp_x + 28 + bar_len * 12 + 4, hp_y, centered=False)

        bat_x = margin
        bat_y = hp_y + 20
        draw_chars(screen, "SH:", NEON_CYAN, bat_x, bat_y, centered=False)
        bat_pct = player.battery / player.max_battery if player.max_battery > 0 else 0
        bat_color = NEON_GREEN if bat_pct > 0.5 else (NEON_YELLOW if bat_pct > 0.25 else NEON_RED)
        draw_bar(screen, bat_x + 28, bat_y, bar_len, bat_pct, bat_color)
        draw_chars(screen, f"{int(player.battery)}%", WHITE, bat_x + 28 + bar_len * 12 + 4, bat_y, centered=False)

        wave_x = margin
        wave_y = bat_y + 20
        draw_chars(screen, f"WAVE [{wave}/{total_waves}]", NEON_YELLOW, wave_x, wave_y, centered=False)

        self.draw_abilities(screen, player, margin, wave_y + 26)

        life_y = 10
        life_x = WINDOW_WIDTH - 160
        hp_pct = max(0, player.hp / player.max_hp * 100)
        life_color = NEON_GREEN if hp_pct > 50 else (NEON_YELLOW if hp_pct > 25 else NEON_RED)
        draw_chars(screen, f"HP: {int(hp_pct)}%", life_color, life_x, life_y, centered=False)

    def draw_abilities(self, screen, player, x, y):
        abilities = [
            ("Q:ATK", player.can_attack(), player.attack_timer, ATTACK_COOLDOWN, NEON_CYAN),
            ("E:SHIELD", player.can_shield(), player.shield_cooldown_timer, SHIELD_COOLDOWN, NEON_YELLOW),
            ("R:TELE", player.can_teleport(), player.teleport_cooldown_timer, TELEPORT_COOLDOWN, NEON_MAGENTA),
        ]

        for i, (name, ready, cooldown, max_cd, color) in enumerate(abilities):
            ay = y + i * 22
            c = color if ready else GRAY
            draw_chars(screen, name, c, x, ay, centered=False)

            if not ready and max_cd > 0:
                cd_pct = int((cooldown / max_cd) * 10)
                cd_bar = '\u2588' * (10 - cd_pct) + '\u2591' * cd_pct
                draw_chars(screen, f"[{cd_bar}]", GRAY, x + 65, ay, centered=False)

    def draw_game_over(self, screen, wave):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        draw_text(screen, "GAME OVER", FONT_XL, NEON_RED, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)
        draw_text(screen, f"Survived {wave} waves", FONT_LG, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
        draw_text(screen, "Press R to restart", FONT_MD, GRAY, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)

    def draw_victory(self, screen):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        draw_text(screen, "VICTORY", FONT_XL, NEON_YELLOW, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)
        draw_text(screen, f"You survived {TOTAL_WAVES} waves!", FONT_LG, NEON_GREEN, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
        draw_text(screen, "ROGALIK: The Ascension Complete", FONT_MD, NEON_CYAN, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
        draw_text(screen, "Press R to restart", FONT_MD, GRAY, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 110)


class StartScreen:
    def draw(self, screen):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_y = WINDOW_HEIGHT // 2 - 120

        draw_text(screen, "ROGALIK", FONT_XL, NEON_CYAN, WINDOW_WIDTH // 2, title_y)
        draw_text(screen, "The Ascension", FONT_LG, NEON_MAGENTA, WINDOW_WIDTH // 2, title_y + 55)

        lines = [
            "SURVIVE 30 WAVES OF ENEMIES",
            "",
            "[WASD] Move  |  [Q] Attack  |  [E] Shield  |  [R] Teleport",
            "Attack: 0% HP cost    |    Shield: 5s invulnerability    |    Teleport: -20% weakness 6s",
            "",
            "Battery drains over time. Kill enemies to recharge.",
            "Lose all HP or Battery = GAME OVER",
        ]
        for i, line in enumerate(lines):
            if line:
                draw_text(screen, line, pygame.font.Font(None, 20), WHITE, WINDOW_WIDTH // 2, title_y + 100 + i * 22)

        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        color = tuple(int(NEON_YELLOW[i] * (0.5 + pulse * 0.5)) for i in range(3))
        draw_text(screen, "Press SPACE to start", pygame.font.Font(None, 36), color, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80)
