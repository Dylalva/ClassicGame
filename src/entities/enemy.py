"""
Clase Enemy - Enemigos con inteligencia artificial usando Q-Learning
"""

import pygame
import random
import os
from src.ai.q_learning import QLearningAgent

class Enemy:
    def __init__(self, x, y, config, enemy_type="barrel"):
        self.config = config
        self.rect = pygame.Rect(x, y, 25, 25)
        self.enemy_type = enemy_type
        self.speed = 3
        self.direction = 1  # Siempre hacia la derecha inicialmente
        
        # Estado del enemigo estilo Donkey Kong
        self.velocity_x = self.speed
        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False
        self.bounce_power = -8
        
        # Comportamiento específico según tipo
        if enemy_type == "monster":
            # Monstruo que cae del cielo
            self.state = "falling"  # falling, waiting, hunting
            self.fall_timer = 0
            self.wait_timer = 0
            self.speed = 2
        else:
            # Barril normal
            self.rolling = True
            self.can_fall = True
        
        self.active = True
        
        # Sistema de animación
        self.sprites = self.load_sprites()
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 6  # Más rápido para simular rodamiento
        
        # Colores según tipo (fallback si no hay sprites)
        self.color = self.config.COLORS['RED'] if enemy_type == "barrel" else self.config.COLORS['GREEN']
    
    def get_state(self, player_rect):
        """Obtiene el estado actual para el agente de IA"""
        if player_rect is None:
            return [0, 0, 0, 0, 0, 0]
        
        # Normalizar posiciones
        state = [
            self.rect.x / self.config.WINDOW_WIDTH,
            self.rect.y / self.config.WINDOW_HEIGHT,
            player_rect.x / self.config.WINDOW_WIDTH,
            player_rect.y / self.config.WINDOW_HEIGHT,
            (self.direction + 1) / 2,  # Normalizar dirección (-1,1) a (0,1)
            1 if self.on_ground else 0
        ]
        return state
    
    def update(self, player_rect, platforms=None):
        """Actualiza el enemigo según su tipo"""
        if self.enemy_type == "monster":
            self.monster_behavior(player_rect, platforms)
        else:
            # Movimiento de barril rodante
            self.barrel_movement(platforms)
        
        # Aplicar física
        self.apply_physics(platforms)
    
    def barrel_movement(self, platforms):
        """Movimiento de barril estilo Donkey Kong clásico"""
        # Movimiento horizontal constante
        self.velocity_x = self.speed * self.direction
        
        # Detectar borde de plataforma
        if platforms and self.on_ground:
            on_platform = False
            current_platform = None
            
            # Encontrar plataforma actual
            for platform in platforms:
                if (self.rect.bottom <= platform.top + 10 and 
                    self.rect.bottom >= platform.top - 10 and
                    self.rect.centerx >= platform.left and 
                    self.rect.centerx <= platform.right):
                    on_platform = True
                    current_platform = platform
                    break
            
            if on_platform and current_platform:
                # Verificar si está cerca del borde
                edge_distance = 15
                
                if self.direction == 1:  # Moviendo a la derecha
                    if self.rect.right >= current_platform.right - edge_distance:
                        # Buscar plataforma inferior para caer
                        can_fall_to_platform = False
                        for platform in platforms:
                            if (platform.top > current_platform.top and
                                platform.left <= self.rect.centerx <= platform.right):
                                can_fall_to_platform = True
                                break
                        
                        if can_fall_to_platform or random.random() < 0.3:
                            # Caer de la plataforma
                            pass
                        else:
                            # Rebotar y cambiar dirección
                            self.direction = -1
                            self.velocity_y = self.bounce_power
                            self.on_ground = False
                
                elif self.direction == -1:  # Moviendo a la izquierda
                    if self.rect.left <= current_platform.left + edge_distance:
                        # Buscar plataforma inferior para caer
                        can_fall_to_platform = False
                        for platform in platforms:
                            if (platform.top > current_platform.top and
                                platform.left <= self.rect.centerx <= platform.right):
                                can_fall_to_platform = True
                                break
                        
                        if can_fall_to_platform or random.random() < 0.3:
                            # Caer de la plataforma
                            pass
                        else:
                            # Rebotar y cambiar dirección
                            self.direction = 1
                            self.velocity_y = self.bounce_power
                            self.on_ground = False
    
    def execute_action(self, action):
        """Ejecuta la acción elegida por la IA"""
        if action == 0:  # Izquierda
            self.velocity_x = -self.speed
            self.direction = -1
        elif action == 1:  # Derecha
            self.velocity_x = self.speed
            self.direction = 1
        elif action == 2:  # Saltar
            if self.on_ground:
                self.velocity_y = -8
                self.on_ground = False
        elif action == 3:  # Esperar
            self.velocity_x = 0
    
    def apply_physics(self, platforms=None):
        """Aplica física estilo Donkey Kong"""
        # Gravedad
        if not self.on_ground:
            self.velocity_y += self.gravity
        
        # Actualizar posición horizontal
        self.rect.x += self.velocity_x
        
        # Límites horizontales - destruir barril si sale de pantalla
        if self.rect.right < 0 or self.rect.left > self.config.WINDOW_WIDTH:
            # Marcar para eliminación
            self.active = False
            return
        
        # Actualizar posición vertical
        self.rect.y += self.velocity_y
        
        # Colisiones con plataformas
        self.on_ground = False
        if platforms:
            for platform in platforms:
                if self.rect.colliderect(platform) and self.velocity_y > 0:
                    if self.rect.bottom <= platform.top + 15:
                        self.rect.bottom = platform.top
                        self.velocity_y = 0
                        self.on_ground = True
                        # Pequeño rebote al aterrizar
                        if abs(self.velocity_y) > 5:
                            self.velocity_y = -2
        
        # Suelo básico
        if self.rect.bottom >= self.config.WINDOW_HEIGHT - 50:
            self.rect.bottom = self.config.WINDOW_HEIGHT - 50
            self.velocity_y = 0
            self.on_ground = True
        elif self.rect.bottom > self.config.WINDOW_HEIGHT:
            # Destruir barril si cae fuera de pantalla
            self.active = False
    
    def monster_behavior(self, player_rect, platforms):
        """Comportamiento específico de monstruos que caen"""
        if self.state == "falling":
            # Caer del cielo
            self.velocity_x = 0
            self.fall_timer += 1
            
            # Después de 5-8 segundos (300-480 frames) cambiar a espera
            if self.fall_timer > random.randint(300, 480) and self.on_ground:
                self.state = "waiting"
                self.wait_timer = 0
                self.velocity_x = 0
        
        elif self.state == "waiting":
            # Quedarse quieto por 1-2 segundos
            self.velocity_x = 0
            self.wait_timer += 1
            
            if self.wait_timer > random.randint(60, 120):  # 1-2 segundos
                self.state = "hunting"
        
        elif self.state == "hunting":
            # Buscar al jugador
            if player_rect:
                dx = player_rect.centerx - self.rect.centerx
                if abs(dx) > 10:
                    self.direction = 1 if dx > 0 else -1
                    self.velocity_x = self.speed * self.direction
                else:
                    self.velocity_x = 0
                
                # Saltar si el jugador está arriba
                dy = player_rect.centery - self.rect.centery
                if dy < -40 and abs(dx) < 60 and self.on_ground:
                    self.velocity_y = -10
                    self.on_ground = False
    
    def calculate_reward(self, player_rect):
        """Calcula la recompensa para el aprendizaje"""
        if player_rect is None:
            return 0
        
        # Distancia al jugador
        distance = ((self.rect.x - player_rect.x) ** 2 + (self.rect.y - player_rect.y) ** 2) ** 0.5
        
        # Recompensa mayor por estar más cerca del jugador
        max_distance = (self.config.WINDOW_WIDTH ** 2 + self.config.WINDOW_HEIGHT ** 2) ** 0.5
        proximity_reward = (max_distance - distance) / max_distance
        
        return proximity_reward
    
    def load_sprites(self):
        """Carga los sprites del enemigo"""
        sprites = []
        sprite_paths = [
            'assets/enemy/enemy1.png',
            'assets/enemy/enemy2.png', 
            'assets/enemy/enemy3.png'
        ]
        
        for path in sprite_paths:
            if os.path.exists(path):
                try:
                    sprite = pygame.image.load(path)
                    sprite = pygame.transform.scale(sprite, (self.rect.width, self.rect.height))
                    sprites.append(sprite)
                except:
                    pass
        
        return sprites if sprites else None
    
    def update_animation(self):
        """Actualiza la animación del sprite"""
        if self.sprites:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.sprites)
                self.animation_timer = 0
    
    def render(self, screen):
        """Renderiza el enemigo"""
        # Actualizar animación
        self.update_animation()
        
        if self.sprites:
            # Renderizar sprite animado
            sprite = self.sprites[self.current_frame]
            # Voltear sprite según dirección
            if self.direction == -1:
                sprite = pygame.transform.flip(sprite, True, False)
            screen.blit(sprite, self.rect)
            
            # Indicador de estado para monstruos
            if self.enemy_type == "monster" and self.state == "waiting":
                pygame.draw.circle(screen, (255, 255, 0), 
                                 (self.rect.centerx, self.rect.top - 10), 3)
        else:
            # Fallback: renderizar rectángulo
            pygame.draw.rect(screen, self.color, self.rect)
            
            # Indicador de dirección
            if self.direction == 1:
                pygame.draw.polygon(screen, self.config.COLORS['WHITE'], [
                    (self.rect.right - 5, self.rect.centery),
                    (self.rect.right - 10, self.rect.centery - 3),
                    (self.rect.right - 10, self.rect.centery + 3)
                ])
            else:
                pygame.draw.polygon(screen, self.config.COLORS['WHITE'], [
                    (self.rect.left + 5, self.rect.centery),
                    (self.rect.left + 10, self.rect.centery - 3),
                    (self.rect.left + 10, self.rect.centery + 3)
                ])