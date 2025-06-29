"""
Menú de tienda para comprar items
"""

import pygame

class ShopMenu:
    def __init__(self, config):
        self.config = config
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.selected_option = 0
        self.items = [
            {"name": "Banana Explosiva", "cost": 50, "description": "Elimina enemigos"},
            {"name": "Vida Extra", "cost": 100, "description": "+1 vida"},
            {"name": "Cerrar Tienda", "cost": 0, "description": "Volver al juego"}
        ]
        self.action = None
        self.show_shop = False
    
    def handle_event(self, event, player, shop_manager=None):
        """Maneja eventos del menú de tienda"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                item = self.items[self.selected_option]
                if item["name"] == "Cerrar Tienda":
                    self.action = "CLOSE"
                elif item["cost"] <= player.total_points:
                    if item["name"] == "Banana Explosiva":
                        player.total_points -= item["cost"]
                        player.bananas += 1
                        self.action = "BOUGHT_BANANA"
                    elif item["name"] == "Vida Extra":
                        player.total_points -= item["cost"]
                        player.lives += 1
                        self.action = "BOUGHT_LIFE"
                else:
                    self.action = "NOT_ENOUGH_POINTS"
            elif event.key == pygame.K_ESCAPE:
                self.action = "CLOSE"
    
    def render(self, screen, player, shop_manager=None):
        """Renderiza el menú de tienda"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Título
        title = self.font.render("TIENDA", True, self.config.COLORS['WHITE'])
        title_rect = title.get_rect(center=(self.config.WINDOW_WIDTH//2, 120))
        screen.blit(title, title_rect)
        
        # Puntos disponibles
        points_text = self.small_font.render(f"Puntos disponibles: {player.total_points}", True, self.config.COLORS['YELLOW'])
        points_rect = points_text.get_rect(center=(self.config.WINDOW_WIDTH//2, 160))
        screen.blit(points_text, points_rect)
        
        # Items de la tienda
        y_start = 220
        for i, item in enumerate(self.items):
            color = self.config.COLORS['YELLOW'] if i == self.selected_option else self.config.COLORS['WHITE']
            
            # Nombre del item
            name_text = self.font.render(item["name"], True, color)
            name_rect = name_text.get_rect(center=(self.config.WINDOW_WIDTH//2, y_start + i * 80))
            screen.blit(name_text, name_rect)
            
            # Costo y descripción
            if item["cost"] > 0:
                cost_text = self.small_font.render(f"Costo: {item['cost']} pts", True, color)
                cost_rect = cost_text.get_rect(center=(self.config.WINDOW_WIDTH//2, y_start + i * 80 + 25))
                screen.blit(cost_text, cost_rect)
            
            desc_text = self.small_font.render(item["description"], True, self.config.COLORS['WHITE'])
            desc_rect = desc_text.get_rect(center=(self.config.WINDOW_WIDTH//2, y_start + i * 80 + 45))
            screen.blit(desc_text, desc_rect)
        
        # Inventario actual
        inventory_y = y_start + len(self.items) * 80 + 40
        inventory_text = self.small_font.render(f"Bananas: {player.bananas}", True, self.config.COLORS['GREEN'])
        inventory_rect = inventory_text.get_rect(center=(self.config.WINDOW_WIDTH//2, inventory_y))
        screen.blit(inventory_text, inventory_rect)
        
        # Instrucciones
        instructions = [
            "↑↓ para navegar, ENTER para comprar",
            "ESC para cerrar tienda"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.config.COLORS['WHITE'])
            text_rect = text.get_rect(center=(self.config.WINDOW_WIDTH//2, inventory_y + 40 + i * 25))
            screen.blit(text, text_rect)
    
    def get_action(self):
        """Obtiene y resetea la acción"""
        action = self.action
        self.action = None
        return action