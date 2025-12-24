# Galaga Clone

A classic space shooter game clone written in Python using the pygame framework.

## Features

- Classic Galaga-style gameplay
- Player ship with smooth movement and shooting
- Enemy formations that move in patterns
- Enemy dive attacks
- Collision detection
- Score system
- Lives system
- Starfield background
- Game states (Menu, Playing, Game Over)

## Requirements

- Python 3.7 or higher
- pygame 2.5.0 or higher

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Run

Simply run the main game file:
```bash
python galaga.py
```

## Controls

- **Arrow Keys** or **WASD** - Move your ship left/right
- **Space** or **Up Arrow** or **W** - Shoot bullets
- **Space** or **Enter** - Start game / Return to menu

## Gameplay

- Destroy enemy ships to earn points (100 points for normal enemies, 200 for bosses)
- Avoid enemy bullets and collisions
- You have 3 lives
- When all enemies are destroyed, a new wave appears
- Survive as long as possible and achieve the highest score!

## Game Structure

The game includes:
- `Player` class - Handles player ship movement, shooting, and lives
- `Enemy` class - Individual enemy ships with formation and attack behaviors
- `EnemyFormation` class - Manages groups of enemies in formation patterns
- `Bullet` classes - Projectiles for both player and enemies
- `Star` class - Background starfield effect
- `Game` class - Main game loop and state management

Enjoy the game!