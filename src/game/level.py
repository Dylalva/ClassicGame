"""
Clase Level - Maneja la estructura y renderizado de niveles
"""

import pygame

class Level:
    def __init__(self, config):
        self.config = config
        self.platforms = []
        self.ladders = []
        self.create_level_1()
    
    def create_level_1(self):
        """Crea el primer nivel estilo Donkey Kong"""
        # Plataformas principales
        self.platforms = [
            pygame.Rect(0, 550, 800, 50),      # Suelo
            pygame.Rect(100, 450, 600, 20),    # Plataforma 1
            pygame.Rect(100, 350, 600, 20),    # Plataforma 2
            pygame.Rect(100, 250, 600, 20),    # Plataforma 3
            pygame.Rect(100, 150, 600, 20),    # Plataforma superior
        ]
        
        # Escaleras
        self.ladders = [
            pygame.Rect(150, 450, 20, 100),    # Escalera 1
            pygame.Rect(650, 350, 20, 100),    # Escalera 2
            pygame.Rect(200, 250, 20, 100),    # Escalera 3
            pygame.Rect(600, 150, 20, 100),    # Escalera 4
        ]
    
    def render(self, screen):
        """Renderiza el nivel"""
        # Renderizar plataformas
        for platform in self.platforms:
            pygame.draw.rect(screen, self.config.COLORS['BROWN'], platform)
        
        # Renderizar escaleras
        for ladder in self.ladders:
            pygame.draw.rect(screen, self.config.COLORS['YELLOW'], ladder)
    
    def get_platforms(self):
        """Retorna las plataformas para detección de colisiones"""
        return self.platforms
    
    def get_ladders(self):
        """Retorna las escaleras para detección de colisiones"""
        return self.ladders
    
    def create_level_2(self):
        """Crea el segundo nivel - Más complejo"""
        self.platforms = [
            pygame.Rect(0, 550, 800, 50),      # Suelo
            pygame.Rect(50, 480, 200, 20),     # Plataforma izquierda
            pygame.Rect(550, 480, 200, 20),    # Plataforma derecha
            pygame.Rect(200, 380, 400, 20),    # Plataforma central
            pygame.Rect(100, 280, 150, 20),    # Plataforma pequeña izq
            pygame.Rect(550, 280, 150, 20),    # Plataforma pequeña der
            pygame.Rect(300, 180, 200, 20),    # Plataforma superior
        ]
        
        self.ladders = [
            pygame.Rect(120, 480, 20, 70),     # Escalera 1
            pygame.Rect(580, 480, 20, 70),     # Escalera 2
            pygame.Rect(250, 380, 20, 100),    # Escalera 3
            pygame.Rect(550, 380, 20, 100),    # Escalera 4
            pygame.Rect(380, 180, 20, 100),    # Escalera 5
        ]
    
    def create_level_3(self):
        """Crea el tercer nivel - Muy difícil"""
        self.platforms = [
            pygame.Rect(0, 550, 800, 50),      # Suelo
            pygame.Rect(0, 450, 150, 20),      # Plataforma 1
            pygame.Rect(200, 480, 100, 20),    # Plataforma pequeña
            pygame.Rect(350, 420, 100, 20),    # Plataforma flotante
            pygame.Rect(500, 460, 150, 20),    # Plataforma 2
            pygame.Rect(650, 380, 150, 20),    # Plataforma alta der
            pygame.Rect(0, 320, 200, 20),      # Plataforma alta izq
            pygame.Rect(300, 280, 200, 20),    # Plataforma central
            pygame.Rect(550, 200, 150, 20),    # Plataforma muy alta
            pygame.Rect(200, 150, 300, 20),    # Plataforma superior
        ]
        
        self.ladders = [
            pygame.Rect(80, 450, 20, 100),     # Escalera 1
            pygame.Rect(230, 420, 20, 60),     # Escalera pequeña
            pygame.Rect(680, 380, 20, 80),     # Escalera 2
            pygame.Rect(150, 320, 20, 130),    # Escalera larga
            pygame.Rect(400, 280, 20, 140),    # Escalera central
            pygame.Rect(580, 200, 20, 80),     # Escalera alta
        ]