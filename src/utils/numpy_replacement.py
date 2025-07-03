# Reemplazo simple de NumPy para PyInstaller
import random
import math

class SimpleArray:
    def __init__(self, data):
        if isinstance(data, (list, tuple)):
            self.data = list(data)
        else:
            self.data = [data]
    
    def __getitem__(self, index):
        return self.data[index]
    
    def __setitem__(self, index, value):
        self.data[index] = value
    
    def __len__(self):
        return len(self.data)
    
    def argmax(self):
        return self.data.index(max(self.data))
    
    def max(self):
        return max(self.data)
    
    def zeros(self, shape):
        if isinstance(shape, int):
            return SimpleArray([0.0] * shape)
        return SimpleArray([[0.0] * shape[1] for _ in range(shape[0])])

def array(data):
    return SimpleArray(data)

def zeros(shape):
    if isinstance(shape, int):
        return SimpleArray([0.0] * shape)
    if isinstance(shape, (list, tuple)) and len(shape) == 2:
        return [[0.0] * shape[1] for _ in range(shape[0])]
    return SimpleArray([0.0] * shape)

def random_choice(choices):
    return random.choice(choices)

def exp(x):
    return math.exp(x)

def maximum(a, b):
    return max(a, b)

# Simular módulo random de numpy
class RandomModule:
    @staticmethod
    def random():
        return random.random()
    
    @staticmethod
    def choice(choices):
        return random.choice(choices)

random = RandomModule()
