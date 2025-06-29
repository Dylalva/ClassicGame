"""
Selector de color para el jugador
"""

import pygame

class ColorSelector:
    def __init__(self, config):
        self.config = config
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.selected_color = 0
        self.color_selected = False
        
        self.colors = [
            ('AZUL', 'BLUE'),
            ('ROJO', 'RED'),
            ('VERDE', 'GREEN'),
            ('AMARILLO', 'YELLOW'),
            ('BLANCO', 'WHITE')
        ]
    
    def handle_event(self, event):
        """Maneja eventos del selector"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_color = (self.selected_color - 1) % len(self.colors)
            elif event.key == pygame.K_RIGHT:
                self.selected_color = (self.selected_color + 1) % len(self.colors)
            elif event.key == pygame.K_RETURN:
                self.color_selected = True
    
    def get_selected_color(self):
        """Retorna el color seleccionado"""
        return self.colors[self.selected_color][1]
    
    def render(self, screen):
        """Renderiza el selector de color"""
        # Título
        title = self.font.render("Elige tu color:", True, self.config.COLORS['WHITE'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 200))
        screen.blit(title, title_rect)
        
        # Mostrar colores
        for i, (name, color_key) in enumerate(self.colors):
            x = 150 + i * 120
            y = 300
            
            # Rectángulo de color
            color_rect = pygame.Rect(x, y, 80, 80)
            pygame.draw.rect(screen, self.config.COLORS[color_key], color_rect)
            
            # Borde si está seleccionado
            if i == self.selected_color:
                pygame.draw.rect(screen, self.config.COLORS['YELLOW'], color_rect, 4)
            
            # Nombre del color
            text = self.small_font.render(name, True, self.config.COLORS['WHITE'])
            text_rect = text.get_rect(center=(x + 40, y + 100))
            screen.blit(text, text_rect)
        
        # Instrucciones
        instructions = [
            "Usa las flechas para elegir",
            "ENTER para confirmar"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.config.COLORS['WHITE'])
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, 450 + i * 30))
            screen.blit(text, text_rect)