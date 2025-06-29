"""
Gestor principal del juego - Controla el bucle principal y estados
"""

import pygame
import sys
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.collectible import Collectible
from src.entities.projectile import Projectile
from src.managers.level_manager import LevelManager
from src.managers.ui_manager import UIManager
from src.managers.shop_manager import ShopManager
from src.ui.shop_menu import ShopMenu
from src.managers.firebase_manager import FirebaseManager
from src.managers.sound_manager import SoundManager
from src.managers.save_manager import SaveManager
from src.managers.auth_manager import AuthManager
import random
import pygame

class GameManager:
    def __init__(self, config):
        self.config = config
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Donkey Kong Classic")
        self.clock = pygame.time.Clock()
        
        # Estados del juego
        self.state = "MENU"  # LOGIN, MENU, COLOR_SELECT, PLAYING, PAUSED, SAVE_MENU, SETTINGS, GAME_OVER, TUTORIAL, LEVEL_COMPLETE, LIFE_LOST, SHOP, LEADERBOARD
        self.running = True
        self.tutorial_active = True
        self.tutorial_step = 0
        self.player_color = 'BLUE'
        self.collectibles_collected = 0
        self.collectibles_needed = 5
        self.mouse_pos = (0, 0)
        
        # Inicializar componentes
        self.firebase_manager = FirebaseManager(config)
        self.sound_manager = SoundManager()
        self.save_manager = SaveManager()
        self.auth_manager = AuthManager(config)
        
        # Managers
        self.ui_manager = UIManager(config, self.auth_manager, self.firebase_manager, self.save_manager, self.sound_manager)
        self.shop_manager = ShopManager(config)
        self.shop_menu = ShopMenu(config)
        self.level_manager = LevelManager(config)
        self.level = None
        self.player = None
        self.enemies = []
        self.collectibles = []
        self.projectiles = []
        self.spawn_timer = 0
        
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
            
            if self.state == "LOGIN":
                new_state = self.ui_manager.handle_login_events(event)
                if new_state:
                    self.state = new_state
            elif self.state == "MENU":
                new_state = self.ui_manager.handle_menu_events(event)
                if new_state == "LOAD_GAME":
                    self.load_game()
                elif new_state:
                    self.state = new_state
            elif self.state == "COLOR_SELECT":
                color = self.ui_manager.handle_color_selector_events(event)
                if color:
                    self.player_color = color
                    self.start_new_game()
            elif self.state == "SETTINGS":
                new_state = self.ui_manager.handle_settings_events(event)
                if new_state:
                    self.state = new_state
            elif self.state == "PLAYING" or self.state == "TUTORIAL":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PAUSED"
                    elif event.key == pygame.K_t:  # Abrir tienda
                        self.state = "SHOP"
                    elif event.key == pygame.K_f and self.player and self.player.bananas > 0:  # Disparar banana
                        self.throw_banana()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.player and self.player.bananas > 0:
                        self.throw_banana_to_mouse()
            elif self.state == "PAUSED":
                action = self.ui_manager.handle_pause_events(event)
                if action == "RESUME":
                    self.state = "PLAYING" if not self.tutorial_active else "TUTORIAL"
                elif action == "SAVE_MENU":
                    self.state = "SAVE_MENU"
            elif self.state == "SAVE_MENU":
                action = self.ui_manager.handle_save_events(event)
                if action == "SAVE_AND_EXIT":
                    self.save_game()
                    self.return_to_menu()
                elif action == "EXIT_NO_SAVE":
                    self.return_to_menu()
                elif action == "CANCEL":
                    self.state = "PAUSED"
            elif self.state == "LEVEL_COMPLETE":
                if event.type == pygame.KEYDOWN:
                    self.continue_to_next_level()
            elif self.state == "LIFE_LOST":
                if event.type == pygame.KEYDOWN:
                    if self.player and self.player.lives > 0:
                        self.state = "PLAYING" if not self.tutorial_active else "TUTORIAL"
                    else:
                        self.state = "GAME_OVER"
            elif self.state == "SHOP":
                self.shop_menu.handle_event(event, self.player, self.shop_manager)
                action = self.shop_menu.get_action()
                if action == "CLOSE":
                    self.state = "PLAYING" if not self.tutorial_active else "TUTORIAL"
            elif self.state == "LEADERBOARD":
                new_state = self.ui_manager.handle_leaderboard_events(event)
                if new_state:
                    self.state = new_state
            elif self.state == "GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_m:
                        self.return_to_menu()
    
    def start_new_game(self):
        """Inicia un nuevo juego"""
        self.state = "TUTORIAL"
        self.tutorial_active = True
        self.tutorial_step = 0
        self.collectibles_collected = 0
        self.level_manager.reset_level()
        
        # Crear nivel y enemigos
        self.level, self.enemies = self.level_manager.create_level(1)
        self.player = Player(100, 500, self.config, self.player_color, self.sound_manager)
        
        # Crear coleccionables iniciales
        self.create_collectibles()
        
        # Reproducir música de fondo
        self.sound_manager.play_music('background')
    
    def restart_game(self):
        """Reinicia el juego actual"""
        self.start_new_game()
    
    def return_to_menu(self):
        """Regresa al menú principal"""
        self.state = "MENU"
        self.ui_manager.menu.start_game = False
        self.ui_manager.menu.continue_game = False
        self.ui_manager.menu.show_settings = False
        self.ui_manager.color_selector.color_selected = False
        self.tutorial_active = True
        self.tutorial_step = 0
        self.ui_manager.menu.update_options()  # Actualizar opciones del menú
    
    def update(self):
        """Actualiza la lógica del juego"""
        if self.state == "PLAYING" or self.state == "TUTORIAL":
            if self.player:
                platforms = self.level.get_platforms() if self.level else []
                self.player.update(platforms)
                
                # Actualizar tutorial
                if self.state == "TUTORIAL":
                    self.update_tutorial()
            
            for enemy in self.enemies:
                platforms = self.level.get_platforms() if self.level else []
                enemy.update(self.player.rect if self.player else None, platforms)
            
            # Actualizar coleccionables
            for collectible in self.collectibles:
                collectible.update()
            
            # Actualizar proyectiles
            for projectile in self.projectiles[:]:
                projectile.update(self.enemies)
                if not projectile.active:
                    self.projectiles.remove(projectile)
            
            # Verificar colisiones
            self.check_collisions()
            
            # Generar nuevos coleccionables
            self.spawn_timer += 1
            if self.spawn_timer > 300:  # Cada 5 segundos a 60 FPS
                self.create_collectibles()
                self.spawn_timer = 0
    
    def update_tutorial(self):
        """Actualiza el estado del tutorial"""
        keys = pygame.key.get_pressed()
        
        if self.tutorial_step == 0 and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]):
            self.tutorial_step = 1
        elif self.tutorial_step == 1 and (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            self.sound_manager.play_sound('jump')
            self.tutorial_step = 2
        elif self.tutorial_step == 2 and self.player.rect.x > 300:
            self.tutorial_step = 3
            self.state = "PLAYING"
            self.tutorial_active = False
            # Agregar más enemigos al completar tutorial
            self.enemies.append(Enemy(300, 300, self.config, "flame"))
    
    def check_collisions(self):
        """Verifica colisiones entre entidades"""
        if not self.player:
            return
            
        # Colisiones con enemigos
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.sound_manager.play_sound('damage')
                self.player.take_damage()
                if self.player.lives <= 0:
                    self.sound_manager.play_sound('game_over')
                    self.state = "GAME_OVER"
                else:
                    # Reposicionar enemigos lejos del jugador
                    self.respawn_enemies()
                    # Pausa después de perder una vida
                    self.state = "LIFE_LOST"
        
        # Colisiones con coleccionables
        for collectible in self.collectibles[:]:
            if not collectible.collected and self.player.rect.colliderect(collectible.rect):
                points = collectible.collect()
                self.player.add_points(points)
                self.sound_manager.play_sound('point')
                self.collectibles.remove(collectible)
                self.collectibles_collected += 1
                
                # Verificar si debe pasar al siguiente nivel
                if self.collectibles_collected >= self.collectibles_needed:
                    self.state = "LEVEL_COMPLETE"
                    # Actualizar mejor puntuación
                    if self.player:
                        print(f"Actualizando mejor puntuación: {self.player.score}")
                        self.auth_manager.update_best_score(self.player.score, self.firebase_manager)
        
        # Colisiones de proyectiles con enemigos
        for projectile in self.projectiles[:]:
            if projectile.exploded:
                explosion_rect = projectile.get_explosion_rect()
                if explosion_rect:
                    for enemy in self.enemies[:]:
                        if enemy.rect.colliderect(explosion_rect):
                            self.enemies.remove(enemy)
                            if self.player:
                                self.player.add_points(100)  # Bonus por matar enemigo
                            self.sound_manager.play_sound('point')
    
    def render(self):
        """Renderiza todos los elementos del juego"""
        self.screen.fill(self.config.COLORS['BLACK'])
        
        # Renderizar juego si está en estados de juego
        if self.state in ["PLAYING", "TUTORIAL"]:
            self._render_game()
        elif self.state == "SHOP":
            self._render_game()
            self.shop_menu.render(self.screen, self.player, self.shop_manager)
        else:
            # Usar UI Manager para otros estados
            game_data = {
                'level': self.level,
                'player': self.player,
                'enemies': self.enemies,
                'collectibles': self.collectibles,
                'projectiles': self.projectiles
            }
            self.ui_manager.render_ui(self.screen, self.state, game_data)
        
        pygame.display.flip()
    
    def _render_game(self):
        """Renderiza elementos del juego"""
        if self.level:
            self.level.render(self.screen)
        if self.player:
            self.player.render(self.screen)
        for enemy in self.enemies:
            enemy.render(self.screen)
        for collectible in self.collectibles:
            collectible.render(self.screen)
        for projectile in self.projectiles:
            projectile.render(self.screen)
        
        if self.state == "TUTORIAL":
            self.render_tutorial()
    
    def render_tutorial(self):
        """Renderiza las instrucciones del tutorial"""
        font = pygame.font.Font(None, 36)
        
        # Indicador del personaje
        if self.player:
            pygame.draw.circle(self.screen, self.config.COLORS['YELLOW'], 
                             (self.player.rect.centerx, self.player.rect.top - 20), 15, 3)
            player_text = font.render("TÚ", True, self.config.COLORS['YELLOW'])
            player_rect = player_text.get_rect(center=(self.player.rect.centerx, self.player.rect.top - 40))
            self.screen.blit(player_text, player_rect)
        
        # Instrucciones según el paso del tutorial
        instructions = [
            "¡Bienvenido! Usa las flechas o WASD para moverte",
            "¡Bien! Ahora presiona ESPACIO o W para saltar",
            f"Recoge {self.collectibles_needed} estrellas ({self.collectibles_collected}/{self.collectibles_needed}). Presiona T para tienda",
            "¡Tutorial completado! T=Tienda, F=Disparar, Click=Apuntar"
        ]
        
        if self.tutorial_step < len(instructions):
            instruction = instructions[self.tutorial_step]
            text = font.render(instruction, True, self.config.COLORS['WHITE'])
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, 50))
            
            # Fondo semi-transparente para el texto
            bg_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 5, text_rect.width + 20, text_rect.height + 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
            self.screen.blit(text, text_rect)
    
    def create_collectibles(self):
        """Crea coleccionables en posiciones aleatorias"""
        platforms = self.level.get_platforms() if self.level else []
        
        for platform in platforms[1:4]:  # Solo en algunas plataformas
            if random.random() < 0.4:  # 40% de probabilidad
                x = random.randint(platform.left + 20, platform.right - 20)
                y = platform.top - 20
                collectible = Collectible(x, y, self.config, random.choice([10, 20, 50]))
                self.collectibles.append(collectible)
    
    def continue_to_next_level(self):
        """Continúa al siguiente nivel después de la pausa"""
        if self.level_manager.next_level():
            self.collectibles_collected = 0
            self.level, self.enemies = self.level_manager.create_level(self.level_manager.current_level)
            self.collectibles.clear()
            self.create_collectibles()
            
            # Reposicionar jugador
            self.player.rect.x = 100
            self.player.rect.y = 500
            self.player.velocity_y = 0
            self.player.on_ground = True
            
            self.state = "PLAYING"
        else:
            # Juego completado
            self.state = "GAME_OVER"
    

    
    def respawn_enemies(self):
        """Reposiciona enemigos en puntos alejados del jugador"""
        if not self.player or not self.enemies:
            return
        
        player_x = self.player.rect.centerx
        spawn_points = [
            (700, 500),  # Esquina derecha abajo
            (50, 500),   # Esquina izquierda abajo
            (700, 200),  # Esquina derecha arriba
            (50, 200),   # Esquina izquierda arriba
            (400, 200),  # Centro arriba
            (600, 400),  # Derecha medio
            (200, 400),  # Izquierda medio
        ]
        
        # Filtrar puntos que estén lejos del jugador (más de 200px)
        far_points = [point for point in spawn_points if abs(point[0] - player_x) > 200]
        
        # Si no hay puntos lejanos, usar todos
        if not far_points:
            far_points = spawn_points
        
        # Reposicionar cada enemigo
        for i, enemy in enumerate(self.enemies):
            spawn_point = far_points[i % len(far_points)]
            enemy.rect.x = spawn_point[0]
            enemy.rect.y = spawn_point[1]
            enemy.velocity_x = 0
            enemy.velocity_y = 0
            enemy.on_ground = False
            enemy.jump_timer = 0
            enemy.stuck_timer = 0
    
    def throw_banana(self):
        """Lanza banana hacia el enemigo más cercano"""
        if not self.player or self.player.bananas <= 0 or not self.enemies:
            return
        
        # Encontrar enemigo más cercano
        closest_enemy = min(self.enemies, key=lambda e: 
            ((e.rect.centerx - self.player.rect.centerx) ** 2 + 
             (e.rect.centery - self.player.rect.centery) ** 2) ** 0.5)
        
        # Crear proyectil
        projectile = Projectile(
            self.player.rect.centerx, self.player.rect.centery,
            closest_enemy.rect.centerx, closest_enemy.rect.centery,
            self.config
        )
        self.projectiles.append(projectile)
        self.player.bananas -= 1
        self.sound_manager.play_sound('jump')  # Sonido temporal
    
    def throw_banana_to_mouse(self):
        """Lanza banana hacia la posición del mouse"""
        if not self.player or self.player.bananas <= 0:
            return
        
        # Crear proyectil hacia mouse
        projectile = Projectile(
            self.player.rect.centerx, self.player.rect.centery,
            self.mouse_pos[0], self.mouse_pos[1],
            self.config
        )
        self.projectiles.append(projectile)
        self.player.bananas -= 1
        self.sound_manager.play_sound('jump')  # Sonido temporal
    
    def save_game(self):
        """Guarda la partida actual"""
        if self.player and self.level_manager:
            self.save_manager.save_game(self.player, self.level_manager, self.collectibles_collected)
    
    def load_game(self):
        """Carga una partida guardada"""
        save_data = self.save_manager.load_game()
        if save_data:
            # Restaurar estado del jugador
            self.player_color = save_data['player']['color']
            
            # Restaurar nivel
            self.level_manager.current_level = save_data['level']['current_level']
            self.collectibles_collected = save_data['level']['collectibles_collected']
            
            # Crear nivel y jugador
            self.level, self.enemies = self.level_manager.create_level(self.level_manager.current_level)
            self.player = Player(save_data['player']['position'][0], save_data['player']['position'][1], 
                               self.config, self.player_color, self.sound_manager)
            self.player.lives = save_data['player']['lives']
            self.player.score = save_data['player']['score']
            self.player.total_points = save_data['player'].get('total_points', self.player.score)  # Compatibilidad
            self.player.bananas = save_data['player'].get('bananas', 0)  # Compatibilidad
            
            # Crear coleccionables
            self.create_collectibles()
            
            # Ir al juego
            self.state = "PLAYING"
            self.tutorial_active = False
            
            # Reproducir música
            self.sound_manager.play_music('background')