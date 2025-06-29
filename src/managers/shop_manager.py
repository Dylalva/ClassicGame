"""
Gestor de tienda - Maneja compras y mejoras del jugador
"""

class ShopManager:
    def __init__(self, config):
        self.config = config
        
        # Items de la tienda
        self.items = {
            'banana': {
                'name': 'Banana Explosiva',
                'price': 50,
                'description': 'Proyectil que explota al contacto'
            },
            'extra_life': {
                'name': 'Vida Extra',
                'price': 100,
                'description': 'Agrega una vida adicional'
            },
            'speed_boost': {
                'name': 'Impulso de Velocidad',
                'price': 75,
                'description': 'Aumenta velocidad temporalmente'
            },
            'jump_boost': {
                'name': 'Salto Mejorado',
                'price': 60,
                'description': 'Aumenta altura de salto'
            },
            'shield': {
                'name': 'Escudo Temporal',
                'price': 80,
                'description': 'Protección contra un golpe'
            }
        }
    
    def can_buy(self, item_id, player):
        """Verifica si el jugador puede comprar un item"""
        if item_id not in self.items:
            return False
        
        item = self.items[item_id]
        return player.score >= item['price']
    
    def buy_item(self, item_id, player):
        """Compra un item para el jugador"""
        if not self.can_buy(item_id, player):
            return False, "No tienes suficientes puntos"
        
        item = self.items[item_id]
        player.score -= item['price']
        
        # Aplicar efectos del item
        if item_id == 'banana':
            player.bananas += 3
            return True, f"Compraste 3 {item['name']}"
        
        elif item_id == 'extra_life':
            player.lives += 1
            return True, f"Compraste {item['name']}"
        
        elif item_id == 'speed_boost':
            player.speed += 2
            return True, f"Velocidad aumentada"
        
        elif item_id == 'jump_boost':
            player.jump_power -= 3  # Más negativo = salto más alto
            return True, f"Salto mejorado"
        
        elif item_id == 'shield':
            # Implementar escudo temporal
            return True, f"Escudo activado"
        
        return False, "Item no válido"
    
    def get_item_info(self, item_id):
        """Obtiene información de un item"""
        return self.items.get(item_id, None)
    
    def get_all_items(self):
        """Obtiene todos los items disponibles"""
        return self.items