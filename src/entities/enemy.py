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
        self.speed = 1.8  # 70% de velocidad (3 * 0.7)
        self.direction = 1  # Siempre hacia la derecha inicialmente
        
        # Estado del enemigo estilo Donkey Kong
        self.velocity_x = self.speed
        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False
        self.bounce_power = -12
        
        # Comportamiento específico según tipo
        if enemy_type == "monster":
            # Monstruo que cae del cielo
            self.state = "falling"  # falling, waiting, hunting
            self.fall_timer = 0
            self.wait_timer = 0
            self.speed = 1.1  # 70% de velocidad (2 * 0.7)
        else:
            # Barril con IA mejorada
            self.rolling = True
            self.can_fall = True
            self.target_platform_y = None
            self.last_player_platform = None
            self.platform_change_timer = 0
            self.stuck_on_platform_timer = 0
            
            # Sistema de pausa periódica
            self.pause_timer = 0
            self.pause_duration = 60  # 1 segundo inicial
            self.is_paused = False
            self.pause_cycle = 300  # Cada 5 segundos
            self.pause_reduction = 5  # Reducir 5 frames cada vez
            
            # IA con Q-Learning mejorada
            self.ai_agent = QLearningAgent(
                state_size=6,
                action_size=4,  # [left, right, jump, drop]
                learning_rate=0.1,
                discount_factor=0.95,
                epsilon=0.2
            )
        
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
            self.barrel_movement(platforms, player_rect)
        
        # Aplicar física
        self.apply_physics(platforms)
    
    def barrel_movement(self, platforms, player_rect=None):
        """Movimiento inteligente de barril con persecución directa y validación Q-Learning"""
        if not player_rect or not platforms:
            # Movimiento básico si no hay información
            self.velocity_x = self.speed * self.direction
            return
        
        # Encontrar plataforma del jugador y actual
        player_platform = self.find_player_platform(platforms, player_rect)
        current_platform = self.find_current_platform(platforms)
        
        # LÓGICA PRINCIPAL: Persecución directa del jugador
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        
        # Decidir acción principal basada en posición del jugador
        primary_action = self.decide_primary_action(dx, dy, current_platform, player_platform)
        
        # VALIDACIÓN Q-Learning: Solo para mejorar la decisión
        if hasattr(self, 'ai_agent'):
            state = self.get_state(player_rect)
            q_action = self.ai_agent.choose_action(state)
            
            # Usar Q-Learning solo si la acción principal no es óptima
            if self.should_override_action(primary_action, q_action, dx, dy):
                primary_action = q_action
            
            # Entrenar Q-Learning con la acción tomada
            reward = self.calculate_reward(player_rect)
            next_state = self.get_state(player_rect)
            done = not self.active
            self.ai_agent.learn(state, primary_action, reward, next_state, done)
        
        # Ejecutar acción decidida
        self.execute_action_decision(primary_action, current_platform, dx)
        
        # Sistema de pausa periódica
        self.handle_pause_behavior()
        
        # Anti-atascamiento
        self.handle_stuck_behavior(current_platform)
    
    def decide_primary_action(self, dx, dy, current_platform, player_platform):
        """Decide la acción principal basada en lógica directa"""
        # Si está en pausa, no moverse
        if self.is_paused:
            return 3  # Esperar/quedarse quieto
        
        # Si el jugador está arriba, saltar
        if dy < -40 and abs(dx) < 100 and self.on_ground:
            return 2  # Saltar
        
        # Forzar caída si está en el borde de la plataforma
        if current_platform:
            edge_distance = 15
            at_left_edge = self.rect.left <= current_platform.left + edge_distance
            at_right_edge = self.rect.right >= current_platform.right - edge_distance
            
            if at_left_edge or at_right_edge:
                return 3  # Bajar forzosamente
        
        # Si el jugador está abajo, buscar activamente forma de bajar
        if dy > 40 and current_platform:
            if self.should_actively_drop(current_platform, player_platform):
                return 3  # Bajar
        
        # Movimiento horizontal hacia el jugador
        if abs(dx) > 10:
            return 1 if dx > 0 else 0  # Derecha o Izquierda
        
        return 1  # Por defecto, moverse a la derecha
    
    def should_override_action(self, primary_action, q_action, dx, dy):
        """Decide si Q-Learning debe anular la acción principal"""
        # Solo anular si Q-Learning sugiere algo muy diferente y tiene sentido
        if primary_action == q_action:
            return False
        
        # Permitir anulación solo en casos específicos
        if abs(dx) < 50 and abs(dy) < 50:  # Muy cerca del jugador
            return True
        
        return False
    
    def execute_action_decision(self, action, current_platform, dx):
        """Ejecuta la acción decidida"""
        if action == 0:  # Izquierda
            self.direction = -1
            self.velocity_x = -self.speed
        elif action == 1:  # Derecha
            self.direction = 1
            self.velocity_x = self.speed
        elif action == 2:  # Saltar
            if self.on_ground:
                self.velocity_y = -15
                self.on_ground = False
        elif action == 3:  # Bajar o esperar
            if self.is_paused:
                # Quedarse quieto durante la pausa
                self.velocity_x = 0
            else:
                # FORZAR movimiento para caer - no depender de plataforma
                self.velocity_x = self.speed * self.direction
                # Si está en el borde, continuar movimiento para caer
                if current_platform:
                    edge_distance = 15
                    at_left_edge = self.rect.left <= current_platform.left + edge_distance
                    at_right_edge = self.rect.right >= current_platform.right - edge_distance
                    
                    if at_left_edge:
                        self.direction = -1
                        self.velocity_x = -self.speed
                    elif at_right_edge:
                        self.direction = 1
                        self.velocity_x = self.speed
    
    def handle_stuck_behavior(self, current_platform):
        """Maneja comportamiento cuando está atascado"""
        if current_platform and abs(self.velocity_x) < 0.1:
            self.stuck_on_platform_timer += 1
            if self.stuck_on_platform_timer > 60:  # 1 segundo atascado
                # Cambiar dirección o saltar
                if random.random() < 0.7:
                    self.direction *= -1
                    self.velocity_x = self.speed * self.direction
                else:
                    self.velocity_y = -15
                    self.on_ground = False
                self.stuck_on_platform_timer = 0
        else:
            self.stuck_on_platform_timer = 0
    
    def handle_pause_behavior(self):
        """Maneja el sistema de pausa periódica"""
        self.pause_timer += 1
        
        if self.is_paused:
            # Contar tiempo de pausa
            if self.pause_timer >= self.pause_duration:
                self.is_paused = False
                self.pause_timer = 0
                # Reducir duración de pausa para la próxima vez
                self.pause_duration = max(10, self.pause_duration - self.pause_reduction)
        else:
            # Verificar si debe pausar
            if self.pause_timer >= self.pause_cycle:
                self.is_paused = True
                self.pause_timer = 0
    
    def should_actively_drop(self, current_platform, player_platform):
        """Busca activamente formas de bajar a otra plataforma"""
        if not current_platform:
            return False
        
        # Si el jugador está en una plataforma más baja, intentar bajar
        if player_platform and player_platform.top > current_platform.top:
            return True
        
        # Si está en el borde, bajar automáticamente
        edge_distance = 20
        at_left_edge = self.rect.left <= current_platform.left + edge_distance
        at_right_edge = self.rect.right >= current_platform.right - edge_distance
        
        # Bajar automáticamente si está en el borde
        if at_left_edge or at_right_edge:
            return True
        
        return False
    
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
    
    def find_player_platform(self, platforms, player_rect):
        """Encuentra la plataforma donde está el jugador"""
        for platform in platforms:
            if (player_rect.bottom <= platform.top + 20 and 
                player_rect.bottom >= platform.top - 10 and
                player_rect.centerx >= platform.left and 
                player_rect.centerx <= platform.right):
                return platform
        return None
    
    def find_current_platform(self, platforms):
        """Encuentra la plataforma actual del enemigo"""
        for platform in platforms:
            if (self.rect.bottom <= platform.top + 10 and 
                self.rect.bottom >= platform.top - 10 and
                self.rect.centerx >= platform.left and 
                self.rect.centerx <= platform.right):
                return platform
        return None
    
    def should_drop_down(self, current_platform, player_platform):
        """Decide si debe bajar de la plataforma actual"""
        if not current_platform or not player_platform:
            return False
        
        # Bajar si el jugador está en una plataforma más baja
        if player_platform.top > current_platform.top:
            return True
        
        # Bajar si ha estado mucho tiempo en la misma plataforma
        self.platform_change_timer += 1
        if self.platform_change_timer > 300:  # 5 segundos
            self.platform_change_timer = 0
            return True
        
        return False
    
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