"""
Objetos coleccionables para obtener puntos
"""

import pygame
import random
import math

class Collectible:
    def __init__(self, x, y, config, points=10):
        self.config = config
        self.rect = pygame.Rect(x, y, 15, 15)
        self.points = points
        self.collected = False
        self.bob_offset = 0
        self.bob_speed = 0.1
        self.original_y = y
        
    def update(self):
        """Actualiza la animación del coleccionable"""
        self.bob_offset += self.bob_speed
        self.rect.y = self.original_y + int(5 * math.sin(self.bob_offset))
    
    def collect(self):
        """Marca el objeto como recolectado"""
        self.collected = True
        return self.points
    
    def render(self, screen):
        """Renderiza el coleccionable"""
        if not self.collected:
            # Estrella simple
            center = self.rect.center
            points = []
            for i in range(5):
                angle = i * 144 - 90  # -90 para que apunte hacia arriba
                outer_x = center[0] + 8 * math.cos(math.radians(angle))
                outer_y = center[1] + 8 * math.sin(math.radians(angle))
                points.append((outer_x, outer_y))
                
                angle += 72
                inner_x = center[0] + 4 * math.cos(math.radians(angle))
                inner_y = center[1] + 4 * math.sin(math.radians(angle))
                points.append((inner_x, inner_y))
            
            pygame.draw.polygon(screen, self.config.COLORS['YELLOW'], points)