# ROGALIK: The Ascension

ASCII-wave survival roguelike built with Pygame. Survive 30 waves of enemies using attack, shield, and teleport abilities.

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrows | Move |
| Q | Attack (120° cone, knockback) |
| E | Shield (5s invulnerability, slow-motion) |
| R | Teleport (random reposition, weakness penalty) |
| 1-3 | Choose upgrade after each wave |
| Space | Start game |
| R | Restart on Game Over / Victory |

## Features

- 3 enemy types: Light (floating), Medium (orbiting), Heavy (chase + clone)
- 12 upgrades after each wave
- ASCII/Unicode rendering with particle effects
- Slow-motion shield mechanic
- Screen shake, scanlines, vignette post-processing
- Web deployment (pygbag) and touch controls for mobile

## Run Locally

```bash
pip install pygame
python main.py
```

## Build

**Desktop (PyInstaller):**
```bash
pip install pyinstaller
pyinstaller ROGALIK_The_Ascension.spec
```

**Web (pygbag):**
```bash
pip install pygbag
cd web && python run_local.py
```

## Tech Stack

- Python 3.13 + Pygame
- pygbag (WebAssembly deployment)
- PyInstaller (desktop .exe)
