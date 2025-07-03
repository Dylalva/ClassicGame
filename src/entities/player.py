"""
Clase Player - Maneja el jugador principal
"""

import pygame
import os

class Player:
    def __init__(self, x, y, config, color='BLUE', sound_manager=None):
        self.config = config
        self.sound_manager = sound_manager
        self.rect = pygame.Rect(x, y, 40, 55)
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = True  # Inicializar en True para permitir salto inicial
        self.on_ladder = False
        self.lives = 3
        self.score = 0
        self.total_points = 0  # Puntos totales acumulados
        self.bananas = 0  # Bananas explosivas disponibles
        self.color = color
        self.direction = 1  # Dirección del jugador
        
        # Sistema de animación
        self.sprites = self.load_sprites()
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8  # Frames entre cambios
        self.jump_frame = 0  # Frame actual del salto
        self.is_jumping_animation = False
        
    def update(self, platforms=None):
        """Actualiza el estado del jugador"""
        keys = pygame.key.get_pressed()
        
        # Movimiento horizontal
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.direction = 1
        
        # Salto
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False
            if self.sound_manager:
                self.sound_manager.play_sound('jump')
        
        # Aplicar gravedad
        if not self.on_ladder:
            self.velocity_y += self.gravity
        
        # Actualizar posición horizontal
        self.rect.x += self.velocity_x
        
        # Límites horizontales
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.config.WINDOW_WIDTH:
            self.rect.right = self.config.WINDOW_WIDTH
        
        # Actualizar posición vertical
        self.rect.y += self.velocity_y
        
        # Colisiones con plataformas
        self.on_ground = False
        if platforms:
            for platform in platforms:
                if self.rect.colliderect(platform) and self.velocity_y > 0:
                    if self.rect.bottom <= platform.top + 10:
                        self.rect.bottom = platform.top
                        self.velocity_y = 0
                        self.on_ground = True
        
        # Límite inferior (caída)
        if self.rect.bottom >= self.config.WINDOW_HEIGHT - 50:
            self.rect.bottom = self.config.WINDOW_HEIGHT - 50
            self.velocity_y = 0
            self.on_ground = True
        elif self.rect.bottom > self.config.WINDOW_HEIGHT:
            self.take_damage()
            self.rect.bottom = self.config.WINDOW_HEIGHT - 50
    
    def add_points(self, points):
        """Agrega puntos al jugador"""
        self.score += points
        self.total_points += points
    
    def take_damage(self):
        """El jugador recibe daño"""
        self.lives -= 1
        # Respawn en posición inicial (sin cambiar de nivel)
        self.rect.x = 100
        self.rect.y = 500
        self.velocity_y = 0
        self.on_ground = True
    
    def load_sprites(self):
        """Carga los sprites del jugador"""
        sprites = {
            'idle': [],
            'jump': []
        }
        
        # Cargar sprites de salto (sprite_01 a sprite_11)
        for i in range(1, 12):
            sprite_path = f'assets/player/sprite_{i:02d}.png'
            if os.path.exists(sprite_path):
                try:
                    sprite = pygame.image.load(sprite_path)
                    sprite = pygame.transform.scale(sprite, (self.rect.width, self.rect.height))
                    sprites['jump'].append(sprite)
                except:
                    pass
        
        # Usar sprite_00 para idle si existe
        idle_path = 'assets/player/sprite_00.png'
        if os.path.exists(idle_path):
            try:
                sprite = pygame.image.load(idle_path)
                sprite = pygame.transform.scale(sprite, (self.rect.width, self.rect.height))
                sprites['idle'].append(sprite)
            except:
                pass
        
        return sprites if any(sprites.values()) else None
    
    def update_animation(self):
        """Actualiza la animación del sprite"""
        if not self.sprites:
            return
        
        # Animación de salto
        if not self.on_ground and self.sprites['jump']:
            if not self.is_jumping_animation:
                self.is_jumping_animation = True
                self.jump_frame = 0
            
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                if self.jump_frame < len(self.sprites['jump']) - 1:
                    self.jump_frame += 1
                self.animation_timer = 0
        else:
            # En el suelo - resetear salto
            if self.is_jumping_animation:
                self.is_jumping_animation = False
                self.jump_frame = 0
    
    def render(self, screen):
        """Renderiza el jugador"""
        # Actualizar animación
        self.update_animation()
        
        if self.sprites:
            # Seleccionar sprite según estado
            if self.is_jumping_animation and self.sprites['jump']:
                sprite = self.sprites['jump'][self.jump_frame]
            elif self.sprites['idle']:
                sprite = self.sprites['idle'][0]  # Usar primer frame idle
            else:
                sprite = None
            
            if sprite:
                # Voltear sprite según dirección
                if self.direction == -1:
                    sprite = pygame.transform.flip(sprite, True, False)
                screen.blit(sprite, self.rect)
            else:
                # Fallback: rectángulo
                pygame.draw.rect(screen, self.config.COLORS[self.color], self.rect)
        else:
            # Fallback: rectángulo
            pygame.draw.rect(screen, self.config.COLORS[self.color], self.rect)
            # Cara simple
            face_center = (self.rect.centerx, self.rect.centery - 5)
            pygame.draw.circle(screen, self.config.COLORS['WHITE'], face_center, 3)
        
        # Renderizar información del jugador
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Vidas: {self.lives}", True, self.config.COLORS['WHITE'])
        screen.blit(lives_text, (10, 10))
        
        score_text = font.render(f"Puntos: {self.score}", True, self.config.COLORS['WHITE'])
        screen.blit(score_text, (10, 50))
        
        total_text = font.render(f"Total: {self.total_points}", True, self.config.COLORS['YELLOW'])
        screen.blit(total_text, (10, 90))
        
        if self.bananas > 0:
            banana_text = font.render(f"Bananas: {self.bananas}", True, self.config.COLORS['GREEN'])
            screen.blit(banana_text, (10, 130))