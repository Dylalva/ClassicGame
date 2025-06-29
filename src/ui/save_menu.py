"""
Menú de guardado del juego
"""

import pygame

class SaveMenu:
    def __init__(self, config):
        self.config = config
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.selected_option = 0
        self.options = ["Guardar y Salir", "Salir sin Guardar", "Cancelar"]
        self.action = None
    
    def handle_event(self, event):
        """Maneja eventos del menú de guardado"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:
                    self.action = "SAVE_AND_EXIT"
                elif self.selected_option == 1:
                    self.action = "EXIT_NO_SAVE"
                elif self.selected_option == 2:
                    self.action = "CANCEL"
            elif event.key == pygame.K_ESCAPE:
                self.action = "CANCEL"
    
    def render(self, screen):
        """Renderiza el menú de guardado"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Título
        title = self.font.render("¿Guardar Partida?", True, self.config.COLORS['WHITE'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 200))
        screen.blit(title, title_rect)
        
        # Subtítulo
        subtitle = self.small_font.render("Tu progreso se perderá si no guardas", True, self.config.COLORS['YELLOW'])
        subtitle_rect = subtitle.get_rect(center=(self.config.WINDOW_WIDTH//2, 240))
        screen.blit(subtitle, subtitle_rect)
        
        # Opciones
        for i, option in enumerate(self.options):
            color = self.config.COLORS['YELLOW'] if i == self.selected_option else self.config.COLORS['WHITE']
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, 320 + i * 55))
            screen.blit(text, text_rect)
    
    def get_action(self):
        """Obtiene y resetea la acción"""
        action = self.action
        self.action = None
        return action