"""
Gestor de guardado y carga de partidas
"""

import json
import os
from datetime import datetime

class SaveManager:
    def __init__(self):
        self.save_file = "data/saves/game_save.json"
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Asegura que el directorio de guardado existe"""
        os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
    
    def save_game(self, player, level_manager, collectibles_collected):
        """Guarda el estado actual del juego"""
        try:
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "player": {
                    "lives": player.lives,
                    "score": player.score,
                    "total_points": player.total_points,
                    "bananas": player.bananas,
                    "color": player.color,
                    "position": [player.rect.x, player.rect.y]
                },
                "level": {
                    "current_level": level_manager.current_level,
                    "collectibles_collected": collectibles_collected
                }
            }
            
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False
    
    def load_game(self):
        """Carga una partida guardada"""
        try:
            if not os.path.exists(self.save_file):
                return None
            
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            return save_data
        except Exception as e:
            print(f"Error al cargar: {e}")
            return None
    
    def has_save_file(self):
        """Verifica si existe una partida guardada"""
        return os.path.exists(self.save_file)
    
    def delete_save(self):
        """Elimina la partida guardada"""
        try:
            if os.path.exists(self.save_file):
                os.remove(self.save_file)
            return True
        except Exception as e:
            print(f"Error al eliminar guardado: {e}")
            return False