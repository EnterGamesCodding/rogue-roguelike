# Display
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
TITLE = "ROGALIK: The Ascension"

# Colors
BLACK = (0, 0, 0)
DARK_BG = (5, 5, 15)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_YELLOW = (255, 255, 0)
NEON_RED = (255, 20, 60)
NEON_GREEN = (0, 255, 120)
DARK_BLUE = (0, 30, 60)
DARK_PURPLE = (30, 0, 50)
WHITE = (200, 200, 220)
GRAY = (80, 80, 100)
ORANGE = (255, 140, 0)
BROWN = (100, 60, 20)

# Player
PLAYER_SPEED = 4
PLAYER_MAX_HP = 100
PLAYER_RADIUS = 14
BATTERY_MAX = 100

# Abilities: Attack
ATTACK_DAMAGE = 30
ATTACK_COOLDOWN = 1.5
ATTACK_HP_COST = 0
ATTACK_RANGE = 130
ATTACK_ARC = 120
ATTACK_KNOCKBACK = 12

# Abilities: Shield
SHIELD_DURATION = 5.0
SHIELD_COOLDOWN = 10.0
SLOW_MOTION_FACTOR = 0.25

# Abilities: Teleport
TELEPORT_COOLDOWN = 4.0
TELEPORT_WEAKNESS = 0.2
TELEPORT_WEAKNESS_DURATION = 6.0

# Enemies: Light (falling balls)
LIGHT_DAMAGE = 5
LIGHT_SPEED = 1.5
LIGHT_RADIUS = 8
LIGHT_HP = 20
LIGHT_SCORE = 10

# Enemies: Medium (orbiting robots)
MEDIUM_DAMAGE = 10
MEDIUM_SPEED = 2.5
MEDIUM_RADIUS = 13
MEDIUM_HP = 45
MEDIUM_SCORE = 25
MEDIUM_ORBIT_SPEED = 2.0
MEDIUM_ORBIT_RADIUS = 90

# Enemies: Heavy (doppelgangers)
HEAVY_DAMAGE = 15
HEAVY_RADIUS = 20
HEAVY_HP = 100
HEAVY_SPEED = 1.2
HEAVY_SCORE = 50
HEAVY_CLONE_INTERVAL = 6.0
HEAVY_CLONE_DURATION = 8.0

# Battery (shield that regenerates)
BATTERY_DRAIN = 0.5
BATTERY_REGEN = 3.0
BATTERY_KILL_REGEN = 10

# Waves
TOTAL_WAVES = 30
WAVE_DELAY = 4.0
ENEMIES_PER_WAVE_BASE = 3

# Upgrades
UPGRADES = [
    ("dmg",      "Урон +10",      "Урон атаки +10",           'D'),
    ("range",    "Радиус +30",    "Радиус атаки +30px",        'R'),
    ("atk_cd",   "Атака быстрее", "КД атаки -0.3с",            'A'),
    ("hp_cost",  "Реген щита",    "Щит восстанавливается +1/с", 'C'),
    ("shd_dur",  "Щит +2с",       "Длительность щита +2с",     'S'),
    ("shd_cd",   "Щит быстрее",   "КД щита -2с",              's'),
    ("tp_cd",    "ТП быстрее",    "КД телепорта -1.5с",        'T'),
    ("tp_weak",  "Меньше слабости","Штраф телепорта -10%",     't'),
    ("speed",    "Скорость +0.5", "Скорость передвижения +0.5",'>'),
    ("hp_max",   "HP +20",        "Максимум HP +20",           'H'),
    ("regen",    "Реген +2",      "Восстановление +2 HP/волну",'+'),
    ("battery",  "Щит +25",       "Максимум щита +25",        'B'),
]

# Arena
ARENA_PADDING = 50
ARENA_WIDTH = WINDOW_WIDTH - ARENA_PADDING * 2
ARENA_HEIGHT = WINDOW_HEIGHT - ARENA_PADDING * 2
