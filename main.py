#!/usr/bin/env python3
"""
Donkey Kong Classic Game
Punto de entrada principal del juego
"""

import pygame
import sys
from src.game.game_manager import GameManager
from src.utils.config import Config

def main():
    """Función principal del juego"""
    pygame.init()
    
    try:
        config = Config()
        game = GameManager(config)
        game.run()
    except Exception as e:
        print(f"Error al iniciar el juego: {e}")
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()