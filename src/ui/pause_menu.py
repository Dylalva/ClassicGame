"""
Menú de pausa del juego
"""

import pygame

class PauseMenu:
    def __init__(self, config):
        self.config = config
        self.font = pygame.font.Font(None, 48)
        self.selected_option = 0
        self.options = ["Reanudar", "Salir al Menú"]
        self.action = None
    
    def handle_event(self, event):
        """Maneja eventos del menú de pausa"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:
                    self.action = "RESUME"
                elif self.selected_option == 1:
                    self.action = "SAVE_MENU"
            elif event.key == pygame.K_ESCAPE:
                self.action = "RESUME"
    
    def render(self, screen):
        """Renderiza el menú de pausa"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Título
        title = self.font.render("PAUSA", True, self.config.COLORS['WHITE'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 220))
        screen.blit(title, title_rect)
        
        # Opciones
        for i, option in enumerate(self.options):
            color = self.config.COLORS['YELLOW'] if i == self.selected_option else self.config.COLORS['WHITE']
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, 300 + i * 70))
            screen.blit(text, text_rect)
    
    def get_action(self):
        """Obtiene y resetea la acción"""
        action = self.action
        self.action = None
        return action