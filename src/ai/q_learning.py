"""
Implementación de Q-Learning para la IA de enemigos
"""

try:
    import numpy as np
except ImportError:
    # Usar reemplazo cuando NumPy no está disponible (PyInstaller)
    from src.utils.numpy_replacement import zeros, array, random_choice, exp, maximum
    import src.utils.numpy_replacement as np
import random
import pickle
import os

class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.95, epsilon=0.1):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Tabla Q inicializada con ceros
        self.q_table = {}
        
        # Cargar modelo existente si existe
        self.model_path = "data/models/q_learning_model.pkl"
        self.load_model()
    
    def get_state_key(self, state):
        """Convierte el estado en una clave para la tabla Q"""
        # Discretizar el estado para usar como clave
        discretized = tuple(int(s * 10) for s in state)
        return discretized
    
    def choose_action(self, state):
        """Elige una acción usando epsilon-greedy"""
        state_key = self.get_state_key(state)
        
        # Exploración vs explotación
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        
        # Si el estado no existe en la tabla, inicializarlo
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.action_size
        
        # Elegir la mejor acción
        q_values = self.q_table[state_key]
        return q_values.index(max(q_values))
    
    def learn(self, state, action, reward, next_state, done):
        """Actualiza la tabla Q usando la ecuación de Bellman"""
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Inicializar estados si no existen
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.action_size
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = [0.0] * self.action_size
        
        # Ecuación de Bellman
        current_q = self.q_table[state_key][action]
        max_next_q = max(self.q_table[next_state_key]) if not done else 0
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state_key][action] = new_q
        
        # Decaimiento de epsilon
        if self.epsilon > 0.01:
            self.epsilon *= 0.9995
    
    def save_model(self):
        """Guarda el modelo entrenado"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'q_table': self.q_table,
                    'epsilon': self.epsilon
                }, f)
            print("Modelo Q-Learning guardado")
        except Exception as e:
            print(f"Error al guardar modelo: {e}")
    
    def load_model(self):
        """Carga un modelo previamente entrenado"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.q_table = data.get('q_table', {})
                    self.epsilon = data.get('epsilon', self.epsilon)
                print("Modelo Q-Learning cargado")
        except Exception as e:
            print(f"Error al cargar modelo: {e}")
    
    def get_stats(self):
        """Obtiene estadísticas del modelo"""
        return {
            'states_explored': len(self.q_table),
            'epsilon': self.epsilon,
            'total_q_values': sum(len(actions) for actions in self.q_table.values())
        }