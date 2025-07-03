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
        """Crea un nivel específico o aleatorio"""
        if level_number <= 3:
            if level_number == 1:
                return self.create_level_1()
            elif level_number == 2:
                return self.create_level_2()
            elif level_number == 3:
                return self.create_level_3()
        else:
            return self.create_random_level(level_number)
    
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
        """Avanza al siguiente nivel (infinito)"""
        self.current_level += 1
        return True
    
    def get_current_level(self):
        """Obtiene el nivel actual"""
        return self.current_level
    
    def reset_level(self):
        """Reinicia al primer nivel"""
        self.current_level = 1
    
    def create_random_level(self, level_number):
        """Genera un nivel aleatorio"""
        import random
        import pygame
        
        level = Level(self.config)
        enemies = []
        
        # Dificultad basada en el nivel
        difficulty = min(level_number - 3, 10)
        
        # Generar plataformas aleatorias
        platforms = []
        ground = pygame.Rect(0, self.config.WINDOW_HEIGHT - 50, self.config.WINDOW_WIDTH, 50)
        platforms.append(ground)
        
        # Capas de plataformas
        num_layers = random.randint(3, 6)
        layer_height = (self.config.WINDOW_HEIGHT - 100) // num_layers
        
        for layer in range(1, num_layers + 1):
            y = self.config.WINDOW_HEIGHT - 50 - (layer * layer_height)
            num_platforms = random.randint(2, 4)
            platform_width = random.randint(80, 150)
            spacing = (self.config.WINDOW_WIDTH - 100) // num_platforms
            
            for i in range(num_platforms):
                x = 50 + (i * spacing) + random.randint(-30, 30)
                x = max(0, min(x, self.config.WINDOW_WIDTH - platform_width))
                platform = pygame.Rect(x, y, platform_width, 20)
                platforms.append(platform)
        
        # Escaleras aleatorias
        ladders = []
        for _ in range(random.randint(1, 3)):
            ladder_x = random.randint(100, self.config.WINDOW_WIDTH - 100)
            ladder_y = random.randint(200, self.config.WINDOW_HEIGHT - 200)
            ladder = pygame.Rect(ladder_x, ladder_y, 20, 100)
            ladders.append(ladder)
        
        level.platforms = platforms
        level.ladders = ladders
        
        # Enemigos basados en dificultad
        num_enemies = min(1 + difficulty // 2, 5)
        for _ in range(num_enemies):
            if len(platforms) > 1:
                platform = random.choice(platforms[1:])
                enemy_x = random.randint(platform.left + 10, platform.right - 35)
                enemy_y = platform.top - 30
                enemy_type = random.choice(["barrel", "flame"])
                enemy = Enemy(enemy_x, enemy_y, self.config, enemy_type)
                enemy.speed = 3 + (difficulty * 0.5)
                enemies.append(enemy)
        
        return level, enemies