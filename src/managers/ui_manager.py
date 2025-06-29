"""
Gestor de interfaz de usuario - Maneja todos los menús y pantallas
"""

import pygame

class UIManager:
    def __init__(self, config, auth_manager, firebase_manager, save_manager, sound_manager):
        self.config = config
        self.auth_manager = auth_manager
        self.firebase_manager = firebase_manager
        self.save_manager = save_manager
        self.sound_manager = sound_manager
        
        # Importar menús
        from src.ui.menu import Menu
        from src.ui.login_menu import LoginMenu
        from src.ui.color_selector import ColorSelector
        from src.ui.pause_menu import PauseMenu
        from src.ui.save_menu import SaveMenu
        from src.ui.settings_menu import SettingsMenu
        from src.ui.leaderboard_menu import LeaderboardMenu
        
        # Inicializar menús
        self.login_menu = LoginMenu(config)
        self.menu = Menu(config, save_manager, auth_manager)
        self.color_selector = ColorSelector(config)
        self.pause_menu = PauseMenu(config)
        self.save_menu = SaveMenu(config)
        self.settings_menu = SettingsMenu(config, sound_manager)
        self.leaderboard_menu = LeaderboardMenu(config, firebase_manager, auth_manager)
    
    def handle_login_events(self, event):
        """Maneja eventos del menú de login"""
        self.login_menu.handle_event(event)
        action = self.login_menu.get_action()
        
        if action == "LOGIN_EMAIL":
            email, password = self.login_menu.get_credentials()
            success, message = self.auth_manager.login_with_email(email, password)
            self.login_menu.set_message(message, not success)
            if success:
                self.menu.update_options()
                self._sync_best_score()
            return "MENU" if success else None
            
        elif action == "REGISTER_EMAIL":
            email, password = self.login_menu.get_credentials()
            success, message = self.auth_manager.register_with_email(email, password)
            self.login_menu.set_message(message, not success)
            if success:
                self.menu.update_options()
                self._sync_best_score()
            return "MENU" if success else None
            
        elif action == "LOGIN_GOOGLE":
            success, message = self.auth_manager.login_with_google()
            self.login_menu.set_message(message, not success)
            if success:
                self.menu.update_options()
                self._sync_best_score()
            return "MENU" if success else None
            
        elif action == "CONTINUE_OFFLINE":
            return "MENU"
        
        return None
    
    def handle_menu_events(self, event):
        """Maneja eventos del menú principal"""
        self.menu.handle_event(event)
        
        if self.menu.start_game:
            self.sound_manager.play_sound('menu_select')
            self.menu.start_game = False
            return "COLOR_SELECT"
        elif self.menu.continue_game:
            self.sound_manager.play_sound('menu_select')
            self.menu.continue_game = False
            return "LOAD_GAME"
        elif self.menu.show_settings:
            self.sound_manager.play_sound('menu_select')
            self.menu.show_settings = False
            return "SETTINGS"
        elif self.menu.show_leaderboard:
            self.sound_manager.play_sound('menu_select')
            self.menu.show_leaderboard = False
            self.leaderboard_menu.load_leaderboard()
            return "LEADERBOARD"
        elif self.menu.show_login:
            self.sound_manager.play_sound('menu_select')
            self.menu.show_login = False
            return "LOGIN"
        elif self.menu.logout_user:
            self.auth_manager.logout()
            self.menu.logout_user = False
            self.menu.update_options()
        
        return None
    
    def handle_color_selector_events(self, event):
        """Maneja eventos del selector de color"""
        self.color_selector.handle_event(event)
        if self.color_selector.color_selected:
            self.sound_manager.play_sound('menu_select')
            color = self.color_selector.get_selected_color()
            return color
        return None
    
    def handle_pause_events(self, event):
        """Maneja eventos del menú de pausa"""
        self.pause_menu.handle_event(event)
        action = self.pause_menu.get_action()
        
        if action == "RESUME":
            return "RESUME"
        elif action == "SAVE_MENU":
            return "SAVE_MENU"
        
        return None
    
    def handle_save_events(self, event):
        """Maneja eventos del menú de guardado"""
        self.save_menu.handle_event(event)
        action = self.save_menu.get_action()
        
        if action == "SAVE_AND_EXIT":
            return "SAVE_AND_EXIT"
        elif action == "EXIT_NO_SAVE":
            return "EXIT_NO_SAVE"
        elif action == "CANCEL":
            return "CANCEL"
        
        return None
    
    def handle_settings_events(self, event):
        """Maneja eventos del menú de configuración"""
        self.settings_menu.handle_event(event)
        if self.settings_menu.back_to_menu:
            self.settings_menu.back_to_menu = False
            return "MENU"
        return None
    
    def handle_leaderboard_events(self, event):
        """Maneja eventos del menú de ranking"""
        self.leaderboard_menu.handle_event(event)
        if self.leaderboard_menu.back_to_menu:
            self.leaderboard_menu.back_to_menu = False
            return "MENU"
        return None
    
    def render_ui(self, screen, state, game_data=None):
        """Renderiza la interfaz según el estado"""
        if state == "LOGIN":
            self.login_menu.render(screen)
        elif state == "MENU":
            self.menu.render(screen)
        elif state == "COLOR_SELECT":
            self.color_selector.render(screen)
        elif state == "SETTINGS":
            self.settings_menu.render(screen)
        elif state == "LEADERBOARD":
            self.leaderboard_menu.render(screen)
        elif state == "PAUSED":
            self._render_game_background(screen, game_data)
            self.pause_menu.render(screen)
        elif state == "SAVE_MENU":
            self._render_game_background(screen, game_data)
            self.save_menu.render(screen)
        elif state == "GAME_OVER":
            self._render_game_over(screen)
        elif state == "LEVEL_COMPLETE":
            self._render_game_background(screen, game_data)
            self._render_level_complete(screen, game_data)
        elif state == "LIFE_LOST":
            self._render_game_background(screen, game_data)
            self._render_life_lost(screen, game_data)
    
    def _render_game_background(self, screen, game_data):
        """Renderiza el fondo del juego"""
        if not game_data:
            return
            
        if game_data.get('level'):
            game_data['level'].render(screen)
        if game_data.get('player'):
            game_data['player'].render(screen)
        for enemy in game_data.get('enemies', []):
            enemy.render(screen)
        for collectible in game_data.get('collectibles', []):
            collectible.render(screen)
        for projectile in game_data.get('projectiles', []):
            projectile.render(screen)
    
    def _render_game_over(self, screen):
        """Renderiza pantalla de game over"""
        font = pygame.font.Font(None, 74)
        text = font.render("GAME OVER", True, self.config.COLORS['RED'])
        text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 - 50))
        screen.blit(text, text_rect)
        
        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render("Presiona R para reintentar", True, self.config.COLORS['WHITE'])
        restart_rect = restart_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + 20))
        screen.blit(restart_text, restart_rect)
        
        menu_text = font_small.render("Presiona M para ir al menú", True, self.config.COLORS['WHITE'])
        menu_rect = menu_text.get_rect(center=(self.config.WINDOW_WIDTH//2, self.config.WINDOW_HEIGHT//2 + 60))
        screen.blit(menu_text, menu_rect)
    
    def _render_level_complete(self, screen, game_data):
        """Renderiza pantalla de nivel completado"""
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 74)
        font_medium = pygame.font.Font(None, 48)
        
        title = font_large.render("¡NIVEL COMPLETADO!", True, self.config.COLORS['YELLOW'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 200))
        screen.blit(title, title_rect)
        
        if game_data and game_data.get('player'):
            score_text = font_medium.render(f"Puntuación: {game_data['player'].score}", True, self.config.COLORS['WHITE'])
            score_rect = score_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 320))
            screen.blit(score_text, score_rect)
        
        instruction = font_medium.render("Presiona cualquier tecla para continuar", True, self.config.COLORS['YELLOW'])
        instruction_rect = instruction.get_rect(center=(self.config.WINDOW_WIDTH//2, 400))
        screen.blit(instruction, instruction_rect)
    
    def _render_life_lost(self, screen, game_data):
        """Renderiza pantalla de vida perdida"""
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((255, 0, 0))
        screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 74)
        font_medium = pygame.font.Font(None, 48)
        
        title = font_large.render("¡VIDA PERDIDA!", True, self.config.COLORS['WHITE'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 200))
        screen.blit(title, title_rect)
        
        if game_data and game_data.get('player'):
            lives_text = font_medium.render(f"Vidas restantes: {game_data['player'].lives}", True, self.config.COLORS['WHITE'])
            lives_rect = lives_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 280))
            screen.blit(lives_text, lives_rect)
        
        instruction = font_medium.render("Presiona cualquier tecla para continuar", True, self.config.COLORS['YELLOW'])
        instruction_rect = instruction.get_rect(center=(self.config.WINDOW_WIDTH//2, 420))
        screen.blit(instruction, instruction_rect)
    
    def _sync_best_score(self):
        """Sincroniza mejor puntuación con Firebase"""
        if self.auth_manager.get_best_score() > 0:
            self.firebase_manager.save_user_best_score(
                self.auth_manager.get_user_id(),
                self.auth_manager.get_best_score(),
                self.auth_manager.get_user_email()
            )