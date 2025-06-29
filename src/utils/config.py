"""
Configuración del juego y manejo de variables de entorno
"""

import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # Configuración de pantalla
        self.WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', 800))
        self.WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', 600))
        self.FPS = int(os.getenv('FPS', 60))
        
        # Configuración de Firebase
        self.firebase_config = {
            'type': os.getenv('FIREBASE_TYPE'),
            'project_id': os.getenv('FIREBASE_PROJECT_ID'),
            'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            'private_key': os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
            'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
            'client_id': os.getenv('FIREBASE_CLIENT_ID'),
            'auth_uri': os.getenv('FIREBASE_AUTH_URI'),
            'token_uri': os.getenv('FIREBASE_TOKEN_URI'),
            'client_x509_cert_url': os.getenv('FIREBASE_CLIENT_CERT_URL'),
            'database_url': os.getenv('FIREBASE_DATABASE_URL')
        }
        
        # Configuración del juego
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        
        # Colores
        self.COLORS = {
            'BLACK': (0, 0, 0),
            'WHITE': (255, 255, 255),
            'RED': (255, 0, 0),
            'BLUE': (0, 100, 255),
            'GREEN': (0, 200, 0),
            'YELLOW': (255, 255, 0),
            'BROWN': (139, 69, 19),
            'PURPLE': (128, 0, 128),
            'ORANGE': (255, 165, 0)
        }