"""
Gestor de niveles del juego
"""

from src.game.level import Level
from src.entities.enemy import Enemy

class LevelManager:
    def __init__(self, config):
        self.config = config
        self.current_level = 1
        self.max_level = 3
    
    def create_level(self, level_number):
        """Crea un nivel específico"""
        if level_number == 1:
            return self.create_level_1()
        elif level_number == 2:
            return self.create_level_2()
        elif level_number == 3:
            return self.create_level_3()
        else:
            return self.create_level_1()  # Nivel por defecto
    
    def create_level_1(self):
        """Primer nivel - Tutorial"""
        level = Level(self.config)
        enemies = [Enemy(400, 400, self.config, "barrel")]
        return level, enemies
    
    def create_level_2(self):
        """Segundo nivel - Más desafiante"""
        level = Level(self.config)
        level.create_level_2()
        enemies = [
            Enemy(200, 350, self.config, "barrel"),
            Enemy(500, 250, self.config, "flame"),
            Enemy(300, 450, self.config, "barrel")
        ]
        return level, enemies
    
    def create_level_3(self):
        """Tercer nivel - Muy difícil"""
        level = Level(self.config)
        level.create_level_3()
        enemies = [
            Enemy(150, 350, self.config, "flame"),
            Enemy(350, 250, self.config, "barrel"),
            Enemy(550, 350, self.config, "flame"),
            Enemy(250, 150, self.config, "barrel"),
            Enemy(450, 450, self.config, "flame")
        ]
        return level, enemies
    
    def next_level(self):
        """Avanza al siguiente nivel"""
        if self.current_level < self.max_level:
            self.current_level += 1
            return True
        return False
    
    def get_current_level(self):
        """Obtiene el nivel actual"""
        return self.current_level
    
    def reset_level(self):
        """Reinicia al primer nivel"""
        self.current_level = 1