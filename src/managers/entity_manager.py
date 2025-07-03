"""
Gestor de entidades - Maneja jugador, enemigos, coleccionables y proyectiles
"""

import random
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.collectible import Collectible
from src.entities.projectile import Projectile

class EntityManager:
    def __init__(self, config):
        self.config = config
        self.player = None
        self.enemies = []
        self.collectibles = []
        self.projectiles = []
        
        # Spawn timers
        self.spawn_timer = 0
        self.monster_spawn_timer = 0
        self.monsters_spawned = 0
        self.monsters_per_level = 3
    
    def create_player(self, x, y, color, sound_manager):
        """Crea el jugador"""
        self.player = Player(x, y, self.config, color, sound_manager)
        return self.player
    
    def add_enemies(self, enemies):
        """Agrega enemigos a la lista"""
        self.enemies.extend(enemies)
    
    def update_all(self, platforms=None):
        """Actualiza todas las entidades"""
        # Actualizar jugador
        if self.player:
            self.player.update(platforms)
        
        # Actualizar enemigos y remover inactivos
        for enemy in self.enemies[:]:
            enemy.update(self.player.rect if self.player else None, platforms)
            if hasattr(enemy, 'active') and not enemy.active:
                self.enemies.remove(enemy)
        
        # Actualizar coleccionables
        for collectible in self.collectibles:
            collectible.update()
        
        # Actualizar proyectiles
        for projectile in self.projectiles[:]:
            projectile.update(self.enemies)
            if not projectile.active:
                self.projectiles.remove(projectile)
    
    def spawn_entities(self):
        """Maneja el spawn de entidades"""
        # Spawn de coleccionables
        self.spawn_timer += 1
        if self.spawn_timer > 300:
            # Necesita referencia al nivel para spawn
            self.spawn_timer = 0
        
        # Spawn gradual de barriles (más lento)
        barrel_count = len([e for e in self.enemies if e.enemy_type == "barrel"])
        max_barrels = min(1 + (self.spawn_timer // 3600), 3)  # Máximo 3 barriles, uno cada 60 segundos
        
        if barrel_count < max_barrels and random.random() < 0.005:  # Spawn mucho más lento
            self.spawn_barrel()
        
        # Spawn gradual de monstruos (más lento)
        self.monster_spawn_timer += 1
        max_monsters = min(1 + (self.spawn_timer // 4800), self.monsters_per_level)  # Uno cada 80 segundos
        
        if (self.monster_spawn_timer > 1200 and self.monsters_spawned < max_monsters):  # Spawn mucho más lento
            self.spawn_monster()
    
    def spawn_collectibles(self, level=None):
        """Genera coleccionables aleatorios"""
        if not level:
            return
            
        import random
        platforms = level.get_platforms()
        
        for platform in platforms[1:4]:  # Solo en algunas plataformas
            if random.random() < 0.7:  # 70% de probabilidad
                x = random.randint(platform.left + 20, platform.right - 20)
                y = platform.top - 20
                collectible = Collectible(x, y, self.config, random.choice([10, 20, 50]))
                self.collectibles.append(collectible)
    
    def spawn_barrel(self):
        """Genera un barril"""
        spawn_points = [(50, 100), (self.config.WINDOW_WIDTH - 50, 100)]
        spawn_point = random.choice(spawn_points)
        new_enemy = Enemy(spawn_point[0], spawn_point[1], self.config, "barrel")
        self.enemies.append(new_enemy)
    
    def spawn_monster(self):
        """Genera un monstruo que cae del cielo"""
        spawn_x = random.randint(100, self.config.WINDOW_WIDTH - 100)
        monster = Enemy(spawn_x, -50, self.config, "monster")
        self.enemies.append(monster)
        self.monsters_spawned += 1
        self.monster_spawn_timer = 0
    
    def throw_projectile(self, target_x, target_y):
        """Lanza un proyectil"""
        if self.player and self.player.bananas > 0:
            projectile = Projectile(
                self.player.rect.centerx, self.player.rect.centery,
                target_x, target_y, self.config
            )
            self.projectiles.append(projectile)
            self.player.bananas -= 1
            return True
        return False
    
    def reset_level(self):
        """Resetea contadores para nuevo nivel"""
        self.monsters_spawned = 0
        self.monster_spawn_timer = 0
        self.spawn_timer = 0
    
    def clear_all(self):
        """Limpia todas las entidades"""
        self.enemies.clear()
        self.collectibles.clear()
        self.projectiles.clear()
    
    def render_all(self, screen):
        """Renderiza todas las entidades"""
        if self.player:
            self.player.render(screen)
        
        for enemy in self.enemies:
            enemy.render(screen)
        
        for collectible in self.collectibles:
            collectible.render(screen)
        
        for projectile in self.projectiles:
            projectile.render(screen)