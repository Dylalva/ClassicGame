"""
Menú de configuración de audio
"""

import pygame

class SettingsMenu:
    def __init__(self, config, sound_manager):
        self.config = config
        self.sound_manager = sound_manager
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.selected_option = 0
        self.options = ["Volumen Música", "Volumen Efectos", "Volver"]
        self.music_volume = int(sound_manager.music_volume * 10)
        self.sfx_volume = int(sound_manager.sfx_volume * 10)
        self.back_to_menu = False
    
    def handle_event(self, event):
        """Maneja eventos del menú de configuración"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_LEFT:
                if self.selected_option == 0 and self.music_volume > 0:
                    self.music_volume -= 1
                    self.sound_manager.set_music_volume(self.music_volume / 10.0)
                elif self.selected_option == 1 and self.sfx_volume > 0:
                    self.sfx_volume -= 1
                    self.sound_manager.set_sfx_volume(self.sfx_volume / 10.0)
            elif event.key == pygame.K_RIGHT:
                if self.selected_option == 0 and self.music_volume < 10:
                    self.music_volume += 1
                    self.sound_manager.set_music_volume(self.music_volume / 10.0)
                elif self.selected_option == 1 and self.sfx_volume < 10:
                    self.sfx_volume += 1
                    self.sound_manager.set_sfx_volume(self.sfx_volume / 10.0)
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 2:
                    self.back_to_menu = True
            elif event.key == pygame.K_ESCAPE:
                self.back_to_menu = True
    
    def render(self, screen):
        """Renderiza el menú de configuración"""
        # Título
        title = self.font.render("CONFIGURACIÓN", True, self.config.COLORS['WHITE'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 120))
        screen.blit(title, title_rect)
        
        # Opciones de volumen
        y_start = 220
        spacing = 120  # Mayor espaciado entre opciones
        
        for i, option in enumerate(self.options[:-1]):  # Excluir "Volver"
            color = self.config.COLORS['YELLOW'] if i == self.selected_option else self.config.COLORS['WHITE']
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, y_start + i * spacing))
            screen.blit(text, text_rect)
            
            # Barra de volumen
            volume = self.music_volume if i == 0 else self.sfx_volume
            bar_width = 250
            bar_height = 25
            bar_x = self.config.WINDOW_WIDTH//2 - bar_width//2
            bar_y = y_start + i * spacing + 45
            
            # Fondo de la barra
            pygame.draw.rect(screen, self.config.COLORS['WHITE'], 
                           (bar_x, bar_y, bar_width, bar_height), 3)
            
            # Relleno de la barra
            fill_width = int((volume / 10.0) * (bar_width - 6))
            if fill_width > 0:
                pygame.draw.rect(screen, self.config.COLORS['GREEN'], 
                               (bar_x + 3, bar_y + 3, fill_width, bar_height - 6))
            
            # Texto del volumen
            vol_text = self.small_font.render(f"{volume}/10", True, self.config.COLORS['WHITE'])
            vol_rect = vol_text.get_rect(center=(self.config.WINDOW_WIDTH//2, bar_y + bar_height + 25))
            screen.blit(vol_text, vol_rect)
        
        # Opción "Volver"
        color = self.config.COLORS['YELLOW'] if self.selected_option == 2 else self.config.COLORS['WHITE']
        back_text = self.font.render("Volver", True, color)
        back_rect = back_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 500))
        screen.blit(back_text, back_rect)
        
        # Instrucciones
        instructions = [
            "← → para ajustar volumen",
            "ENTER para volver al menú"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.config.COLORS['WHITE'])
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, 550 + i * 30))
            screen.blit(text, text_rect)