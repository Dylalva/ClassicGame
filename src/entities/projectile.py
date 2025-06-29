"""
Proyectiles del jugador (banana explosiva)
"""

import pygame
import math

class Projectile:
    def __init__(self, x, y, target_x, target_y, config):
        self.config = config
        self.rect = pygame.Rect(x, y, 15, 15)
        self.start_x = x
        self.start_y = y
        
        # Calcular trayectoria parabólica
        distance = ((target_x - x) ** 2 + (target_y - y) ** 2) ** 0.5
        self.speed = 8
        self.velocity_x = (target_x - x) / distance * self.speed if distance > 0 else 0
        self.velocity_y = (target_y - y) / distance * self.speed if distance > 0 else 0
        
        # Gravedad para efecto parabólico
        self.gravity = 0.3
        self.active = True
        self.explosion_timer = 0
        self.exploded = False
        
    def update(self, enemies=None):
        """Actualiza el proyectil"""
        if not self.active:
            return
        
        if not self.exploded:
            # Aplicar movimiento solo si no ha explotado
            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y
            self.velocity_y += self.gravity
            
            # Verificar colisión con enemigos
            if enemies:
                for enemy in enemies:
                    if self.rect.colliderect(enemy.rect):
                        self.explode()
                        return
            
            # Límites de pantalla
            if (self.rect.x < 0 or self.rect.x > self.config.WINDOW_WIDTH or 
                self.rect.y > self.config.WINDOW_HEIGHT):
                self.explode()
        else:
            # Manejar explosión
            if self.explosion_timer > 0:
                self.explosion_timer -= 1
            else:
                self.active = False
    
    def explode(self):
        """Explota el proyectil"""
        if not self.exploded:
            self.exploded = True
            self.explosion_timer = 30  # Duración de la explosión
            self.velocity_x = 0
            self.velocity_y = 0
    
    def get_explosion_rect(self):
        """Obtiene el área de explosión"""
        if self.exploded and self.explosion_timer > 0:
            explosion_size = 60
            return pygame.Rect(
                self.rect.centerx - explosion_size//2,
                self.rect.centery - explosion_size//2,
                explosion_size, explosion_size
            )
        return None
    
    def render(self, screen):
        """Renderiza el proyectil"""
        if self.exploded:
            # Renderizar explosión
            if self.explosion_timer > 0:
                explosion_rect = self.get_explosion_rect()
                if explosion_rect:
                    # Círculo de explosión
                    pygame.draw.circle(screen, self.config.COLORS['YELLOW'], 
                                     explosion_rect.center, explosion_rect.width//2)
                    pygame.draw.circle(screen, self.config.COLORS['RED'], 
                                     explosion_rect.center, explosion_rect.width//3)
                self.explosion_timer -= 1
                if self.explosion_timer <= 0:
                    self.active = False
        else:
            # Renderizar banana
            pygame.draw.ellipse(screen, self.config.COLORS['YELLOW'], self.rect)
            # Detalle de banana
            pygame.draw.arc(screen, (139, 69, 19), self.rect, 0, math.pi, 2)