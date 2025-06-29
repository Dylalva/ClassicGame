"""
Menú principal del juego
"""

import pygame

class Menu:
    def __init__(self, config, save_manager, auth_manager=None):
        self.config = config
        self.save_manager = save_manager
        self.auth_manager = auth_manager
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.tiny_font = pygame.font.Font(None, 24)
        self.start_game = False
        self.continue_game = False
        self.show_settings = False
        self.show_leaderboard = False
        self.show_login = False
        self.logout_user = False
        self.selected_option = 0
        
        # Opciones dinámicas según si hay partida guardada
        self.update_options()
        
        # Cargar imagen del menú
        self.menu_image = None
        try:
            self.menu_image = pygame.image.load("assets/images/menu_background.png")
            self.menu_image = pygame.transform.scale(self.menu_image, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        except:
            pass  # Si no existe la imagen, continuar sin ella
    
    def update_options(self):
        """Actualiza las opciones según el estado del juego"""
        base_options = []
        
        if self.save_manager.has_save_file():
            base_options.extend(["Continuar", "Nuevo Juego"])
        else:
            base_options.append("Jugar")
        
        base_options.extend(["Ranking", "Opciones"])
        
        if self.auth_manager and self.auth_manager.is_logged_in():
            base_options.append("Cerrar Sesión")
        else:
            base_options.append("Iniciar Sesión")
        
        base_options.append("Salir")
        self.options = base_options
    
    def handle_event(self, event):
        """Maneja eventos del menú"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                option = self.options[self.selected_option]
                if option == "Continuar":
                    self.continue_game = True
                elif option in ["Jugar", "Nuevo Juego"]:
                    self.start_game = True
                elif option == "Ranking":
                    self.show_leaderboard = True
                elif option == "Opciones":
                    self.show_settings = True
                elif option == "Cerrar Sesión":
                    self.logout_user = True
                elif option == "Iniciar Sesión":
                    self.show_login = True
                elif option == "Salir":
                    pygame.quit()
                    exit()
    
    def render(self, screen):
        """Renderiza el menú"""
        # Imagen de fondo si existe
        if self.menu_image:
            screen.blit(self.menu_image, (0, 0))
        
        # Título
        title = self.font_large.render("DONKEY KONG", True, self.config.COLORS['YELLOW'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 150))
        screen.blit(title, title_rect)
        
        # Opciones del menú
        menu_start_y = 280
        for i, option in enumerate(self.options):
            color = self.config.COLORS['WHITE']
            if i == self.selected_option:
                color = self.config.COLORS['YELLOW']
            
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, menu_start_y + i * 50))
            screen.blit(text, text_rect)
        
        # Información del usuario y mejor puntuación
        info_start_y = menu_start_y + len(self.options) * 50 + 30
        
        # Usuario actual
        if self.auth_manager and self.auth_manager.is_logged_in():
            user_text = self.small_font.render(f"Usuario: {self.auth_manager.get_user_email()}", True, self.config.COLORS['GREEN'])
            user_rect = user_text.get_rect(center=(self.config.WINDOW_WIDTH//2, info_start_y))
            screen.blit(user_text, user_rect)
            info_start_y += 35
        
        # Mejor puntuación local
        if self.auth_manager:
            best_score = self.auth_manager.get_best_score()
            if best_score > 0:
                score_text = self.small_font.render(f"Mejor Puntuación: {best_score}", True, self.config.COLORS['YELLOW'])
                score_rect = score_text.get_rect(center=(self.config.WINDOW_WIDTH//2, info_start_y))
                screen.blit(score_text, score_rect)
                info_start_y += 35
        
        # Instrucciones
        instructions = [
            "Controles: Flechas/WASD, ESPACIO, T=Tienda",
            "Inicia sesión para guardar en la nube"
        ]
        
        if self.auth_manager and self.auth_manager.is_logged_in():
            instructions[1] = "Progreso guardado en la nube"
        
        for i, instruction in enumerate(instructions):
            text = self.tiny_font.render(instruction, True, self.config.COLORS['WHITE'])
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, info_start_y + 20 + i * 25))
            screen.blit(text, text_rect)