"""
Gestor de tutorial - Maneja la lógica y renderizado del tutorial
"""

import pygame

class TutorialManager:
    def __init__(self, config):
        self.config = config
        self.active = True
        self.step = 0
        self.collectibles_needed = 5
        
    def update(self, player, sound_manager, entity_manager):
        """Actualiza el estado del tutorial"""
        if not self.active:
            return False
            
        keys = pygame.key.get_pressed()
        
        if self.step == 0 and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or 
                              keys[pygame.K_a] or keys[pygame.K_d]):
            self.step = 1
        elif self.step == 1 and (keys[pygame.K_SPACE] or keys[pygame.K_UP] or 
                                keys[pygame.K_w]):
            sound_manager.play_sound('jump')
            self.step = 2
        elif self.step == 2 and player.rect.x > 300:
            self.step = 3
            self.active = False
            # Agregar enemigo al completar tutorial
            from src.entities.enemy import Enemy
            entity_manager.enemies.append(Enemy(300, 300, self.config, "flame"))
            return True  # Tutorial completado
        
        return False
    
    def render(self, screen, player, collectibles_collected):
        """Renderiza las instrucciones del tutorial"""
        if not self.active:
            return
            
        font = pygame.font.Font(None, 36)
        
        # Indicador del personaje
        if player:
            pygame.draw.circle(screen, self.config.COLORS['YELLOW'], 
                             (player.rect.centerx, player.rect.top - 20), 15, 3)
            player_text = font.render("TÚ", True, self.config.COLORS['YELLOW'])
            player_rect = player_text.get_rect(center=(player.rect.centerx, player.rect.top - 40))
            screen.blit(player_text, player_rect)
        
        # Instrucciones según el paso
        instructions = [
            "¡Bienvenido! Usa las flechas o WASD para moverte",
            "¡Bien! Ahora presiona ESPACIO o W para saltar",
            f"Recoge {self.collectibles_needed} estrellas ({collectibles_collected}/{self.collectibles_needed}). Presiona T para tienda",
            "¡Tutorial completado! T=Tienda, F=Disparar, Click=Apuntar"
        ]
        
        if self.step < len(instructions):
            instruction = instructions[self.step]
            text = font.render(instruction, True, self.config.COLORS['WHITE'])
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, 50))
            
            # Fondo semi-transparente
            bg_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 5, 
                                text_rect.width + 20, text_rect.height + 10)
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
            screen.blit(text, text_rect)
    
    def reset(self):
        """Reinicia el tutorial"""
        self.active = True
        self.step = 0
    
    def is_active(self):
        """Verifica si el tutorial está activo"""
        return self.active
    
    def complete(self):
        """Completa el tutorial"""
        self.active = False