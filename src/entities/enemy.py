"""
Clase Enemy - Enemigos con inteligencia artificial usando Q-Learning
"""

import pygame
import random
from src.ai.q_learning import QLearningAgent

class Enemy:
    def __init__(self, x, y, config, enemy_type="barrel"):
        self.config = config
        self.rect = pygame.Rect(x, y, 25, 25)
        self.enemy_type = enemy_type
        self.speed = 2
        self.direction = random.choice([-1, 1])
        
        # IA con Q-Learning
        self.ai_agent = QLearningAgent(
            state_size=6,  # [pos_x, pos_y, player_x, player_y, direction, on_platform]
            action_size=4,  # [left, right, jump, wait]
            learning_rate=0.1,
            discount_factor=0.95,
            epsilon=0.1
        )
        
        # Estado del enemigo
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.5
        self.on_ground = False
        self.jump_power = -10
        
        # Persecución directa
        self.jump_timer = 0
        self.stuck_timer = 0
        self.last_position = (self.rect.x, self.rect.y)
        
        # Colores según tipo
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
        """Actualiza el enemigo con persecución directa"""
        if player_rect:
            self.chase_player(player_rect, platforms)
        else:
            # Movimiento básico si no hay jugador
            self.velocity_x = self.speed * self.direction
        
        # Aplicar física
        self.apply_physics(platforms)
    
    def chase_player(self, player_rect, platforms):
        """Persigue al jugador directamente"""
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        
        # Movimiento horizontal constante hacia el jugador
        if abs(dx) > 10:
            self.velocity_x = self.speed if dx > 0 else -self.speed
            self.direction = 1 if dx > 0 else -1
        else:
            self.velocity_x = 0
        
        # Lógica de salto y caída mejorada
        should_jump = False
        should_fall = False
        
        # Saltar si el jugador está significativamente arriba
        if dy < -40 and abs(dx) < 60:
            should_jump = True
        
        # Caer si el jugador está significativamente abajo
        if dy > 40 and abs(dx) < 60 and self.on_ground:
            should_fall = True
        
        # Verificar si puede caminar hacia el jugador o necesita saltar/caer
        if platforms and self.on_ground:
            # Buscar si hay un borde cerca en la dirección del jugador
            edge_ahead = True
            for platform in platforms:
                # Verificar si hay plataforma en la dirección del movimiento
                future_x = self.rect.centerx + (30 * self.direction)
                if (platform.left <= future_x <= platform.right and 
                    abs(platform.top - self.rect.bottom) < 10):
                    edge_ahead = False
                    break
            
            # Si hay un borde y el jugador está abajo, saltar del borde para caer
            if edge_ahead and dy > 20:
                should_fall = True
            
            # Si el jugador está arriba, buscar plataforma para saltar
            if dy < -20:
                for platform in platforms:
                    if (abs(platform.centerx - self.rect.centerx) < 100 and 
                        platform.centery < self.rect.centery):
                        should_jump = True
                        break
        
        # Ejecutar salto
        if should_jump and self.on_ground:
            self.jump_timer += 1
            if self.jump_timer > 15:
                self.velocity_y = self.jump_power
                self.on_ground = False
                self.jump_timer = 0
        # Ejecutar caída (continuar moviéndose hacia el borde)
        elif should_fall:
            # Mantener movimiento horizontal para caer del borde
            pass
        else:
            self.jump_timer = max(0, self.jump_timer - 1)
    
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
        """Aplica física básica al enemigo"""
        # Detectar si está atascado
        current_pos = (self.rect.x, self.rect.y)
        if abs(current_pos[0] - self.last_position[0]) < 2 and abs(current_pos[1] - self.last_position[1]) < 2:
            self.stuck_timer += 1
            if self.stuck_timer > 30 and self.on_ground:  # Si está atascado, saltar
                self.velocity_y = self.jump_power
                self.on_ground = False
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
        
        self.last_position = current_pos
        
        # Gravedad
        if not self.on_ground:
            self.velocity_y += self.gravity
        
        # Actualizar posición horizontal
        old_x = self.rect.x
        self.rect.x += self.velocity_x
        
        # Límites horizontales
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        if self.rect.right > self.config.WINDOW_WIDTH:
            self.rect.right = self.config.WINDOW_WIDTH
            self.direction = -1
        
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
        
        # Suelo básico
        if self.rect.bottom >= self.config.WINDOW_HEIGHT - 50:
            self.rect.bottom = self.config.WINDOW_HEIGHT - 50
            self.velocity_y = 0
            self.on_ground = True
    
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
    
    def render(self, screen):
        """Renderiza el enemigo"""
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