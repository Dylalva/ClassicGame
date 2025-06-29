"""
Menú de ranking/leaderboard
"""

import pygame

class LeaderboardMenu:
    def __init__(self, config, firebase_manager, auth_manager):
        self.config = config
        self.firebase_manager = firebase_manager
        self.auth_manager = auth_manager
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.tiny_font = pygame.font.Font(None, 24)
        
        self.leaderboard_data = []
        self.loading = True
        self.back_to_menu = False
        
        # Cargar datos
        self.load_leaderboard()
    
    def load_leaderboard(self):
        """Carga el ranking desde Firebase"""
        self.loading = True
        self.leaderboard_data = []
        try:
            print("Cargando ranking desde Firebase...")
            self.leaderboard_data = self.firebase_manager.get_global_leaderboard(10)
            print(f"Ranking cargado: {len(self.leaderboard_data)} entradas")
            self.loading = False
        except Exception as e:
            print(f"Error cargando ranking: {e}")
            self.loading = False
            self.leaderboard_data = []
    
    def handle_event(self, event):
        """Maneja eventos del menú"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                self.back_to_menu = True
    
    def render(self, screen):
        """Renderiza el ranking"""
        # Título
        title = self.font.render("RANKING GLOBAL", True, self.config.COLORS['YELLOW'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 80))
        screen.blit(title, title_rect)
        
        if self.loading:
            loading_text = self.small_font.render("Cargando...", True, self.config.COLORS['WHITE'])
            loading_rect = loading_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 300))
            screen.blit(loading_text, loading_rect)
        elif not self.leaderboard_data:
            no_data_text = self.small_font.render("No hay datos disponibles", True, self.config.COLORS['WHITE'])
            no_data_rect = no_data_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 300))
            screen.blit(no_data_text, no_data_rect)
        else:
            # Encabezados
            pos_header = self.small_font.render("Pos", True, self.config.COLORS['WHITE'])
            screen.blit(pos_header, (150, 140))
            
            email_header = self.small_font.render("Jugador", True, self.config.COLORS['WHITE'])
            screen.blit(email_header, (250, 140))
            
            score_header = self.small_font.render("Puntuación", True, self.config.COLORS['WHITE'])
            screen.blit(score_header, (500, 140))
            
            # Línea separadora
            pygame.draw.line(screen, self.config.COLORS['WHITE'], (150, 170), (650, 170), 2)
            
            # Datos del ranking
            for i, entry in enumerate(self.leaderboard_data):
                y_pos = 190 + i * 35
                
                # Posición
                pos_color = self.config.COLORS['YELLOW'] if i < 3 else self.config.COLORS['WHITE']
                pos_text = self.small_font.render(f"{i+1}", True, pos_color)
                screen.blit(pos_text, (160, y_pos))
                
                # Email (truncado si es muy largo)
                email = entry['email']
                if len(email) > 20:
                    email = email[:17] + "..."
                
                # Resaltar usuario actual
                email_color = self.config.COLORS['GREEN'] if (self.auth_manager.is_logged_in() and 
                                                            email.startswith(self.auth_manager.get_user_email()[:17])) else self.config.COLORS['WHITE']
                email_text = self.small_font.render(email, True, email_color)
                screen.blit(email_text, (250, y_pos))
                
                # Puntuación
                score_text = self.small_font.render(f"{entry['score']:,}", True, self.config.COLORS['WHITE'])
                screen.blit(score_text, (500, y_pos))
        
        # Tu mejor puntuación local
        if self.auth_manager:
            local_best = self.auth_manager.get_best_score()
            if local_best > 0:
                your_score_text = self.small_font.render(f"Tu mejor puntuación local: {local_best:,}", True, self.config.COLORS['YELLOW'])
                your_score_rect = your_score_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 500))
                screen.blit(your_score_text, your_score_rect)
        
        # Instrucciones
        instruction = self.tiny_font.render("ESC o ENTER para volver al menú", True, self.config.COLORS['WHITE'])
        instruction_rect = instruction.get_rect(center=(self.config.WINDOW_WIDTH//2, 550))
        screen.blit(instruction, instruction_rect)