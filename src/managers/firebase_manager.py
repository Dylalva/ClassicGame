"""
Gestor de Firebase para persistencia de datos
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseManager:
    def __init__(self, config):
        self.config = config
        self.db = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Inicializa la conexión con Firebase REST API"""
        try:
            self.database_url = os.getenv('FIREBASE_DATABASE_URL')
            self.api_key = os.getenv('FIREBASE_API_KEY')
            print("Firebase REST API inicializado correctamente")
        except Exception as e:
            print(f"Error al inicializar Firebase: {e}")
    
    def save_user_progress(self, user_id, progress_data):
        """Guarda el progreso del usuario"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.set({
                'progress': progress_data,
                'last_updated': firestore.SERVER_TIMESTAMP
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error al guardar progreso: {e}")
            return False
    
    def load_user_progress(self, user_id):
        """Carga el progreso del usuario"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict().get('progress', {})
            return {}
        except Exception as e:
            print(f"Error al cargar progreso: {e}")
            return {}
    
    def save_ai_model(self, model_name, model_data):
        """Guarda datos del modelo de IA"""
        try:
            doc_ref = self.db.collection('ai_models').document(model_name)
            doc_ref.set({
                'model_data': model_data,
                'last_updated': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            print(f"Error al guardar modelo IA: {e}")
            return False
    
    def load_ai_model(self, model_name):
        """Carga datos del modelo de IA"""
        try:
            doc_ref = self.db.collection('ai_models').document(model_name)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict().get('model_data', {})
            return {}
        except Exception as e:
            print(f"Error al cargar modelo IA: {e}")
            return {}
    
    def save_user_best_score(self, user_id, score, email):
        """Guarda la mejor puntuación del usuario en Realtime Database"""
        try:
            print(f"Intentando guardar puntuación: {score} para {email} (ID: {user_id})")
            
            # URL para obtener datos actuales
            get_url = f"{self.database_url}/leaderboard/{user_id}.json"
            
            # Obtener datos actuales
            response = requests.get(get_url)
            current_data = response.json() if response.status_code == 200 else None
            
            print(f"Datos actuales: {current_data}")
            
            should_save = False
            if current_data:
                current_score = current_data.get('best_score', 0)
                if score > current_score:
                    should_save = True
                    print(f"Actualizando: {current_score} -> {score}")
            else:
                should_save = True
                print("Creando nueva entrada")
            
            if should_save:
                import time
                data_to_save = {
                    'user_id': user_id,
                    'email': email,
                    'best_score': score,
                    'timestamp': int(time.time())
                }
                
                # URL para guardar datos
                put_url = f"{self.database_url}/leaderboard/{user_id}.json"
                save_response = requests.put(put_url, json=data_to_save)
                
                if save_response.status_code == 200:
                    print(f"Datos guardados exitosamente: {data_to_save}")
                    return True
                else:
                    print(f"Error al guardar: {save_response.status_code}")
                    return False
            else:
                print(f"No se actualizó: puntuación actual {current_data.get('best_score', 0)} >= nueva {score}")
                return False
                
        except Exception as e:
            print(f"Error detallado al guardar: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user_best_score(self, user_id):
        """Obtiene la mejor puntuación del usuario"""
        try:
            url = f"{self.database_url}/leaderboard/{user_id}.json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data.get('best_score', 0)
            return 0
        except Exception as e:
            print(f"Error al obtener mejor puntuación: {e}")
            return 0
    
    def get_global_leaderboard(self, limit=10):
        """Obtiene el ranking global"""
        try:
            url = f"{self.database_url}/leaderboard.json"
            response = requests.get(url)
            
            leaderboard = []
            if response.status_code == 200:
                data = response.json()
            
                if data:
                # Obtener todos los datos y ordenar localmente
                    for user_id, user_data in data.items():
                        if isinstance(user_data, dict) and 'best_score' in user_data:
                            leaderboard.append({
                                'email': user_data.get('email', 'Anonimo'),
                                'score': user_data.get('best_score', 0)
                            })
                
                # Ordenar por puntuación descendente y limitar
                leaderboard.sort(key=lambda x: x['score'], reverse=True)
                leaderboard = leaderboard[:limit]
            
            return leaderboard
        except Exception as e:
            print(f"Error al obtener ranking: {e}")
            return []
    
    def save_cloud_game(self, user_id, save_data):
        """Guarda partida en la nube"""
        try:
            import time
            url = f"{self.database_url}/cloud_saves/{user_id}.json"
            data = {
                'save_data': save_data,
                'last_updated': int(time.time())
            }
            response = requests.put(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error al guardar en la nube: {e}")
            return False
    
    def load_cloud_game(self, user_id):
        """Carga partida de la nube"""
        try:
            url = f"{self.database_url}/cloud_saves/{user_id}.json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data.get('save_data', {})
            return {}
        except Exception as e:
            print(f"Error al cargar de la nube: {e}")
            return {}