"""
Gestor de estados del juego - Maneja transiciones y lógica de estados
"""

from src.managers.tutorial_manager import TutorialManager

class GameStateManager:
    def __init__(self, config):
        self.config = config
        self.state = "MENU"
        self.collectibles_collected = 0
        self.collectibles_needed = 5
        self.tutorial_manager = TutorialManager(config)
    
    def set_state(self, new_state):
        """Cambia el estado del juego"""
        self.state = new_state
    
    def get_state(self):
        """Obtiene el estado actual"""
        return self.state
    
    def start_tutorial(self):
        """Inicia el tutorial"""
        self.state = "TUTORIAL"
        self.tutorial_manager.reset()
        self.collectibles_collected = 0
    
    def update_tutorial(self, player, sound_manager, entity_manager):
        """Actualiza el estado del tutorial"""
        if self.tutorial_manager.update(player, sound_manager, entity_manager):
            # Tutorial completado
            self.state = "PLAYING"
    
    def continue_to_next_level(self, level_manager, entity_manager):
        """Continúa al siguiente nivel"""
        if level_manager.next_level():
            self.collectibles_collected = 0
            entity_manager.reset_level()
            level, enemies = level_manager.create_level(level_manager.current_level)
            entity_manager.clear_all()
            entity_manager.add_enemies(enemies)
            
            # Reposicionar jugador
            if entity_manager.player:
                entity_manager.player.rect.x = 100
                entity_manager.player.rect.y = 500
                entity_manager.player.velocity_y = 0
                entity_manager.player.on_ground = True
            
            self.state = "PLAYING"
            return level
        else:
            self.state = "GAME_OVER"
            return None
    
    def reset_game(self):
        """Resetea el juego"""
        self.tutorial_manager.reset()
        self.collectibles_collected = 0
    
    def is_playing(self):
        """Verifica si está en estado de juego"""
        return self.state in ["PLAYING", "TUTORIAL"]
    
    def render_tutorial(self, screen, player):
        """Renderiza el tutorial"""
        if self.state == "TUTORIAL":
            self.tutorial_manager.render(screen, player, self.collectibles_collected)