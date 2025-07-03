"""
Gestor principal del juego - Controla el bucle principal y estados
"""

import pygame
from src.managers.level_manager import LevelManager
from src.managers.ui_manager import UIManager
from src.managers.shop_manager import ShopManager
from src.managers.entity_manager import EntityManager
from src.managers.collision_manager import CollisionManager
from src.managers.game_state_manager import GameStateManager
from src.ui.shop_menu import ShopMenu
from src.managers.firebase_manager import FirebaseManager
from src.managers.sound_manager import SoundManager
from src.managers.save_manager import SaveManager
from src.managers.auth_manager import AuthManager
import pygame

class GameManager:
    def __init__(self, config):
        self.config = config
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Donkey Kong Classic")
        self.clock = pygame.time.Clock()
        
        # Estados del juego
        self.running = True
        self.player_color = 'BLUE'
        self.mouse_pos = (0, 0)
        
        # Inicializar componentes
        self.firebase_manager = FirebaseManager(config)
        self.sound_manager = SoundManager()
        self.save_manager = SaveManager()
        self.auth_manager = AuthManager(config)
        
        # Managers
        self.ui_manager = UIManager(config, self.auth_manager, self.firebase_manager, self.save_manager, self.sound_manager)
        self.shop_manager = ShopManager(config)
        self.entity_manager = EntityManager(config)
        self.collision_manager = CollisionManager(config, self.sound_manager, self.auth_manager, self.firebase_manager)
        self.game_state_manager = GameStateManager(config)
        self.shop_menu = ShopMenu(config)
        self.level_manager = LevelManager(config)
        self.level = None
        
    def run(self):
        """Bucle principal del juego"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.config.FPS)
    
    def handle_events(self):
        """Maneja eventos del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = pygame.mouse.get_pos()
            
            current_state = self.game_state_manager.get_state()
            
            if current_state == "LOGIN":
                new_state = self.ui_manager.handle_login_events(event)
                if new_state:
                    self.game_state_manager.set_state(new_state)
            elif current_state == "MENU":
                new_state = self.ui_manager.handle_menu_events(event)
                if new_state == "LOAD_GAME":
                    self.load_game()
                elif new_state:
                    self.game_state_manager.set_state(new_state)
            elif current_state == "COLOR_SELECT":
                self.start_new_game()
            elif current_state == "SETTINGS":
                new_state = self.ui_manager.handle_settings_events(event)
                if new_state:
                    self.game_state_manager.set_state(new_state)
            elif self.game_state_manager.is_playing():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state_manager.set_state("PAUSED")
                    elif event.key == pygame.K_t:
                        self.game_state_manager.set_state("SHOP")
                    elif event.key == pygame.K_f:
                        self.throw_banana()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.throw_banana_to_mouse()
            elif current_state == "PAUSED":
                action = self.ui_manager.handle_pause_events(event)
                if action == "RESUME":
                    resume_state = "PLAYING" if not self.game_state_manager.tutorial_manager.is_active() else "TUTORIAL"
                    self.game_state_manager.set_state(resume_state)
                elif action == "SAVE_MENU":
                    self.game_state_manager.set_state("SAVE_MENU")
            elif current_state == "SAVE_MENU":
                action = self.ui_manager.handle_save_events(event)
                if action == "SAVE_AND_EXIT":
                    self.save_game()
                    self.return_to_menu()
                elif action == "EXIT_NO_SAVE":
                    self.return_to_menu()
                elif action == "CANCEL":
                    self.game_state_manager.set_state("PAUSED")
            elif current_state == "LEVEL_COMPLETE":
                if event.type == pygame.KEYDOWN:
                    self.continue_to_next_level()
            elif current_state == "LIFE_LOST":
                if event.type == pygame.KEYDOWN:
                    if self.entity_manager.player and self.entity_manager.player.lives > 0:
                        resume_state = "PLAYING" if not self.game_state_manager.tutorial_manager.is_active() else "TUTORIAL"
                        self.game_state_manager.set_state(resume_state)
                    else:
                        # Reiniciar spawn de enemigos al perder
                        self.entity_manager.reset_level()
                        self.entity_manager.clear_all()
                        self.game_state_manager.set_state("GAME_OVER")
            elif current_state == "SHOP":
                self.shop_menu.handle_event(event, self.entity_manager.player, self.shop_manager)
                action = self.shop_menu.get_action()
                if action == "CLOSE":
                    resume_state = "PLAYING" if not self.game_state_manager.tutorial_manager.is_active() else "TUTORIAL"
                    self.game_state_manager.set_state(resume_state)
            elif current_state == "LEADERBOARD":
                new_state = self.ui_manager.handle_leaderboard_events(event)
                if new_state:
                    self.game_state_manager.set_state(new_state)
            elif current_state == "GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_m:
                        self.return_to_menu()
    
    def start_new_game(self):
        """Inicia un nuevo juego"""
        self.game_state_manager.start_tutorial()
        self.level_manager.reset_level()
        self.entity_manager.reset_level()
        self.entity_manager.clear_all()  # Limpiar todos los enemigos
        
        # Crear nivel y entidades
        self.level, enemies = self.level_manager.create_level(1)
        self.entity_manager.create_player(100, 500, self.player_color, self.sound_manager)
        self.entity_manager.add_enemies(enemies)
        
        self.sound_manager.play_music('background')
    
    def restart_game(self):
        """Reinicia el juego actual"""
        self.start_new_game()
    
    def return_to_menu(self):
        """Regresa al menú principal"""
        self.game_state_manager.set_state("MENU")
        self.ui_manager.menu.start_game = False
        self.ui_manager.menu.continue_game = False
        self.ui_manager.menu.show_settings = False
        self.ui_manager.color_selector.color_selected = False
        self.game_state_manager.reset_game()
        self.ui_manager.menu.update_options()
    
    def update(self):
        """Actualiza la lógica del juego"""
        if self.game_state_manager.is_playing():
            platforms = self.level.get_platforms() if self.level else []
            
            # Actualizar entidades
            self.entity_manager.update_all(platforms)
            
            # Actualizar tutorial
            if self.game_state_manager.get_state() == "TUTORIAL":
                self.game_state_manager.update_tutorial(
                    self.entity_manager.player, self.sound_manager, self.entity_manager
                )
            
            # Spawn de entidades
            self.entity_manager.spawn_entities()
            
            # Spawn de coleccionables
            self.entity_manager.spawn_timer += 1
            if self.entity_manager.spawn_timer > 120:  # Cada 2 segundos en lugar de 5
                self.entity_manager.spawn_collectibles(self.level)
                self.entity_manager.spawn_timer = 0
            
            # Verificar colisiones
            game_state, collectibles = self.collision_manager.check_all_collisions(
                self.entity_manager, 
                self.game_state_manager.collectibles_collected,
                self.game_state_manager.collectibles_needed
            )
            
            if game_state:
                self.game_state_manager.set_state(game_state)
            
            self.game_state_manager.collectibles_collected = collectibles
    

    

    
    def render(self):
        """Renderiza todos los elementos del juego"""
        self.screen.fill(self.config.COLORS['BLACK'])
        
        # Renderizar juego si está en estados de juego
        if self.game_state_manager.is_playing():
            self._render_game()
        elif self.game_state_manager.get_state() == "SHOP":
            self._render_game()
            self.shop_menu.render(self.screen, self.entity_manager.player, self.shop_manager)
        else:
            # Usar UI Manager para otros estados
            game_data = {
                'level': self.level,
                'player': self.entity_manager.player,
                'enemies': self.entity_manager.enemies,
                'collectibles': self.entity_manager.collectibles,
                'projectiles': self.entity_manager.projectiles
            }
            self.ui_manager.render_ui(self.screen, self.game_state_manager.get_state(), game_data)
        
        pygame.display.flip()
    
    def _render_game(self):
        """Renderiza elementos del juego"""
        if self.level:
            self.level.render(self.screen)
        
        self.entity_manager.render_all(self.screen)
        
        # Renderizar indicador de tienda
        self.render_shop_indicator()
        
        # Renderizar tutorial si está activo
        if self.game_state_manager.get_state() == "TUTORIAL":
            self.game_state_manager.render_tutorial(self.screen, self.entity_manager.player)
    

    
    def render_shop_indicator(self):
        """Renderiza el indicador de la tienda"""
        if self.game_state_manager.is_playing():
            # Cuadro de tienda en esquina superior derecha
            shop_rect = pygame.Rect(self.config.WINDOW_WIDTH - 150, 10, 140, 60)
            pygame.draw.rect(self.screen, (50, 50, 50), shop_rect)
            pygame.draw.rect(self.screen, self.config.COLORS['WHITE'], shop_rect, 2)
            
            # Texto de la tienda
            font = pygame.font.Font(None, 24)
            shop_text = font.render("TIENDA", True, self.config.COLORS['WHITE'])
            text_rect = shop_text.get_rect(center=(shop_rect.centerx, shop_rect.centery - 10))
            self.screen.blit(shop_text, text_rect)
            
            # Instrucción
            key_text = font.render("Presiona T", True, self.config.COLORS['YELLOW'])
            key_rect = key_text.get_rect(center=(shop_rect.centerx, shop_rect.centery + 10))
            self.screen.blit(key_text, key_rect)
    

    
    def continue_to_next_level(self):
        """Continúa al siguiente nivel después de la pausa"""
        new_level = self.game_state_manager.continue_to_next_level(self.level_manager, self.entity_manager)
        if new_level:
            self.level = new_level
    

    
    def respawn_enemies(self):
        """Reposiciona enemigos en puntos alejados del jugador"""
        # Delegado al collision_manager
        self.collision_manager.respawn_enemies(self.entity_manager.enemies, self.entity_manager.player)
    
    def throw_banana(self):
        """Lanza banana hacia el enemigo más cercano"""
        if not self.entity_manager.player or not self.entity_manager.enemies:
            return
        
        # Encontrar enemigo más cercano
        closest_enemy = min(self.entity_manager.enemies, key=lambda e: 
            ((e.rect.centerx - self.entity_manager.player.rect.centerx) ** 2 + 
             (e.rect.centery - self.entity_manager.player.rect.centery) ** 2) ** 0.5)
        
        # Usar entity_manager para lanzar proyectil
        if self.entity_manager.throw_projectile(closest_enemy.rect.centerx, closest_enemy.rect.centery):
            self.sound_manager.play_sound('jump')
    
    def throw_banana_to_mouse(self):
        """Lanza banana hacia la posición del mouse"""
        if self.entity_manager.throw_projectile(self.mouse_pos[0], self.mouse_pos[1]):
            self.sound_manager.play_sound('jump')
    
    def save_game(self):
        """Guarda la partida actual"""
        if self.entity_manager.player and self.level_manager:
            self.save_manager.save_game(
                self.entity_manager.player, 
                self.level_manager, 
                self.game_state_manager.collectibles_collected
            )
    
    def load_game(self):
        """Carga una partida guardada"""
        save_data = self.save_manager.load_game()
        if save_data:
            # Restaurar estado del jugador
            self.player_color = save_data['player']['color']
            
            # Restaurar nivel
            self.level_manager.current_level = save_data['level']['current_level']
            self.game_state_manager.collectibles_collected = save_data['level']['collectibles_collected']
            
            # Crear nivel y jugador
            self.level, enemies = self.level_manager.create_level(self.level_manager.current_level)
            player = self.entity_manager.create_player(
                save_data['player']['position'][0], 
                save_data['player']['position'][1], 
                self.player_color, 
                self.sound_manager
            )
            player.lives = save_data['player']['lives']
            player.score = save_data['player']['score']
            player.total_points = save_data['player'].get('total_points', player.score)
            player.bananas = save_data['player'].get('bananas', 0)
            
            self.entity_manager.add_enemies(enemies)
            
            # Ir al juego
            self.game_state_manager.set_state("PLAYING")
            self.game_state_manager.tutorial_manager.complete()
            
            # Reproducir música
            self.sound_manager.play_music('background')