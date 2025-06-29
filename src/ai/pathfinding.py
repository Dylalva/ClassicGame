"""
Algoritmo A* para pathfinding de enemigos
"""

import heapq
import math

class AStarPathfinder:
    def __init__(self, grid_width, grid_height, cell_size=20):
        self.grid_width = grid_width // cell_size
        self.grid_height = grid_height // cell_size
        self.cell_size = cell_size
        self.obstacles = set()
    
    def add_obstacles(self, platforms):
        """Agrega obstáculos basados en las plataformas (solo el interior, no la superficie)"""
        self.obstacles.clear()
        for platform in platforms:
            # Solo marcar como obstáculo el interior de las plataformas, no la superficie superior
            for x in range(platform.left // self.cell_size, (platform.right // self.cell_size) + 1):
                for y in range((platform.top + 5) // self.cell_size, (platform.bottom // self.cell_size) + 1):
                    if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                        self.obstacles.add((x, y))
    
    def heuristic(self, a, b):
        """Distancia Manhattan"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(self, pos):
        """Obtiene vecinos válidos incluyendo saltos verticales"""
        x, y = pos
        neighbors = []
        # Movimientos básicos
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and 
                (nx, ny) not in self.obstacles):
                neighbors.append((nx, ny))
        
        # Saltos verticales para alcanzar plataformas
        for dx in [-1, 0, 1]:
            for jump_height in range(2, 6):  # Saltos de 2 a 5 celdas
                nx, ny = x + dx, y - jump_height
                if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and 
                    (nx, ny) not in self.obstacles):
                    neighbors.append((nx, ny))
        
        return neighbors
    
    def find_path(self, start_pos, target_pos):
        """Encuentra el camino más corto usando A*"""
        start = (start_pos[0] // self.cell_size, start_pos[1] // self.cell_size)
        goal = (target_pos[0] // self.cell_size, target_pos[1] // self.cell_size)
        
        if start == goal:
            return []
        
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                # Reconstruir camino
                path = []
                while current in came_from:
                    path.append((current[0] * self.cell_size, current[1] * self.cell_size))
                    current = came_from[current]
                return path[::-1]
            
            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # No se encontró camino