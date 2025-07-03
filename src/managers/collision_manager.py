"""
Gestor de colisiones - Maneja todas las colisiones del juego
"""

class CollisionManager:
    def __init__(self, config, sound_manager, auth_manager, firebase_manager):
        self.config = config
        self.sound_manager = sound_manager
        self.auth_manager = auth_manager
        self.firebase_manager = firebase_manager
    
    def check_all_collisions(self, entity_manager, collectibles_collected, collectibles_needed):
        """Verifica todas las colisiones del juego"""
        if not entity_manager.player:
            return None, collectibles_collected
        
        # Colisiones con enemigos
        game_state = self.check_enemy_collisions(entity_manager)
        if game_state:
            return game_state, collectibles_collected
        
        # Colisiones con coleccionables
        collectibles_collected = self.check_collectible_collisions(
            entity_manager, collectibles_collected, collectibles_needed
        )
        
        # Colisiones de proyectiles
        self.check_projectile_collisions(entity_manager)
        
        # Verificar nivel completado
        if collectibles_collected >= collectibles_needed:
            if entity_manager.player:
                self.auth_manager.update_best_score(
                    entity_manager.player.score, self.firebase_manager
                )
            return "LEVEL_COMPLETE", collectibles_collected
        
        return None, collectibles_collected
    
    def check_enemy_collisions(self, entity_manager):
        """Verifica colisiones con enemigos"""
        for enemy in entity_manager.enemies:
            if entity_manager.player.rect.colliderect(enemy.rect):
                self.sound_manager.play_sound('damage')
                entity_manager.player.take_damage()
                
                if entity_manager.player.lives <= 0:
                    self.sound_manager.play_sound('game_over')
                    return "GAME_OVER"
                else:
                    self.respawn_enemies(entity_manager.enemies, entity_manager.player)
                    return "LIFE_LOST"
        return None
    
    def check_collectible_collisions(self, entity_manager, collectibles_collected, collectibles_needed):
        """Verifica colisiones con coleccionables"""
        for collectible in entity_manager.collectibles[:]:
            if (not collectible.collected and 
                entity_manager.player.rect.colliderect(collectible.rect)):
                
                points = collectible.collect()
                entity_manager.player.add_points(points)
                self.sound_manager.play_sound('point')
                entity_manager.collectibles.remove(collectible)
                collectibles_collected += 1
        
        return collectibles_collected
    
    def check_projectile_collisions(self, entity_manager):
        """Verifica colisiones de proyectiles con enemigos"""
        for projectile in entity_manager.projectiles[:]:
            if projectile.exploded:
                explosion_rect = projectile.get_explosion_rect()
                if explosion_rect:
                    enemies_to_remove = []
                    for enemy in entity_manager.enemies:
                        if enemy.rect.colliderect(explosion_rect):
                            enemies_to_remove.append(enemy)
                    
                    for enemy in enemies_to_remove:
                        entity_manager.enemies.remove(enemy)
                        if entity_manager.player:
                            entity_manager.player.add_points(100)
                        self.sound_manager.play_sound('point')
    
    def respawn_enemies(self, enemies, player):
        """Reposiciona enemigos lejos del jugador"""
        if not player or not enemies:
            return
        
        player_x = player.rect.centerx
        spawn_points = [
            (700, 500), (50, 500), (700, 200), (50, 200),
            (400, 200), (600, 400), (200, 400)
        ]
        
        far_points = [point for point in spawn_points if abs(point[0] - player_x) > 200]
        if not far_points:
            far_points = spawn_points
        
        for i, enemy in enumerate(enemies):
            spawn_point = far_points[i % len(far_points)]
            enemy.rect.x = spawn_point[0]
            enemy.rect.y = spawn_point[1]
            enemy.velocity_x = 0
            enemy.velocity_y = 0
            enemy.on_ground = False
            if hasattr(enemy, 'jump_timer'):
                enemy.jump_timer = 0
            if hasattr(enemy, 'stuck_timer'):
                enemy.stuck_timer = 0