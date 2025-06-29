"""
Gestor de autenticación con Firebase
"""

import json
import os
import webbrowser
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
class AuthManager:
    def __init__(self, config):
        self.config = config
        self.user_data = None
        self.local_best_score = self.load_local_best_score()
        
        # URLs de Firebase Auth REST API
        self.api_key = os.getenv('FIREBASE_API_KEY')
        self.auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts"
        
        # Cargar sesión guardada
        self.load_saved_session()
        
    def load_local_best_score(self):
        """Carga la mejor puntuación local"""
        try:
            if os.path.exists("data/saves/best_score.json"):
                with open("data/saves/best_score.json", 'r') as f:
                    data = json.load(f)
                    return data.get('best_score', 0)
        except:
            pass
        return 0
    
    def save_local_best_score(self, score):
        """Guarda la mejor puntuación local"""
        try:
            os.makedirs("data/saves", exist_ok=True)
            with open("data/saves/best_score.json", 'w') as f:
                json.dump({
                    'best_score': score,
                    'timestamp': datetime.now().isoformat()
                }, f)
            self.local_best_score = score
        except Exception as e:
            print(f"Error guardando puntuación local: {e}")
    
    def register_with_email(self, email, password):
        """Registra usuario con email y contraseña"""
        try:
            url = f"{self.auth_url}:signUp?key={self.api_key}"
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=data)
            result = response.json()
            
            if response.status_code == 200:
                self.user_data = {
                    'uid': result['localId'],
                    'email': result['email'],
                    'token': result['idToken']
                }
                self.save_session()
                return True, "Registro exitoso"
            else:
                return False, result.get('error', {}).get('message', 'Error desconocido')
                
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def login_with_email(self, email, password):
        """Inicia sesión con email y contraseña"""
        try:
            url = f"{self.auth_url}:signInWithPassword?key={self.api_key}"
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=data)
            result = response.json()
            
            if response.status_code == 200:
                self.user_data = {
                    'uid': result['localId'],
                    'email': result['email'],
                    'token': result['idToken']
                }
                self.save_session()
                return True, "Inicio de sesión exitoso"
            else:
                return False, result.get('error', {}).get('message', 'Credenciales incorrectas')
                
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def login_with_google(self):
        """Inicia sesión con Google OAuth real"""
        try:
            import urllib.parse
            import threading
            import http.server
            import socketserver
            from urllib.parse import parse_qs, urlparse
            import time
            
            # Credenciales OAuth reales
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            redirect_uri = "http://localhost:8080"
            
            # URL de autorización de Google
            auth_params = {
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'scope': 'openid email profile',
                'access_type': 'offline'
            }
            
            auth_url = f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(auth_params)}"
            
            # Variable para capturar respuesta
            auth_result = {'code': None, 'error': None}
            
            class AuthHandler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    try:
                        parsed_url = urlparse(self.path)
                        params = parse_qs(parsed_url.query)
                        
                        if 'code' in params:
                            auth_result['code'] = params['code'][0]
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write('<h1>Autenticacion exitosa! Cierra esta ventana.</h1>'.encode('utf-8'))
                        elif 'error' in params:
                            auth_result['error'] = params['error'][0]
                            self.send_response(400)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write('<h1>Error en autenticacion</h1>'.encode('utf-8'))
                        else:
                            auth_result['error'] = 'Respuesta invalida'
                    except Exception as e:
                        auth_result['error'] = str(e)
                
                def log_message(self, format, *args):
                    pass
            
            # Iniciar servidor local
            server = socketserver.TCPServer(('localhost', 8080), AuthHandler)
            server_thread = threading.Thread(target=server.handle_request)
            server_thread.daemon = True
            server_thread.start()
            
            # Abrir navegador
            print("Abriendo navegador para autenticación con Google...")
            webbrowser.open(auth_url)
            
            # Esperar respuesta
            timeout = 60
            start_time = time.time()
            
            while auth_result['code'] is None and auth_result['error'] is None:
                if time.time() - start_time > timeout:
                    server.server_close()
                    return False, "Timeout: Autenticación no completada"
                time.sleep(0.5)
            
            server.server_close()
            
            if auth_result['error']:
                return False, f"Error OAuth: {auth_result['error']}"
            
            print(f"Código de autorización recibido: {auth_result['code'][:10]}...")
            
            # Intercambiar código por tokens
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': auth_result['code'],
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            print("Intercambiando código por tokens...")
            token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
            
            print(f"Status de token: {token_response.status_code}")
            print(f"Respuesta de token: {token_response.text[:200]}...")
            
            if token_response.status_code != 200:
                return False, f"Error obteniendo tokens: {token_response.status_code}"
            
            try:
                token_result = token_response.json()
            except json.JSONDecodeError as e:
                return False, f"Error parsing JSON de tokens: {str(e)}"
            
            if 'access_token' not in token_result:
                return False, f"No se recibió access_token: {token_result}"
            
            print("Tokens obtenidos exitosamente")
            
            # Obtener información del usuario
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {token_result["access_token"]}'}
            )
            
            if user_info_response.status_code != 200:
                return False, f"Error obteniendo info de usuario: {user_info_response.status_code}"
            
            try:
                user_info = user_info_response.json()
            except json.JSONDecodeError as e:
                return False, f"Error parsing JSON de usuario: {str(e)}"
            
            print(f"Info de usuario obtenida: {user_info.get('email', 'Sin email')}")
            
            # Crear usuario en Firebase usando signInWithIdp
            firebase_auth_url = f"{self.auth_url}:signInWithIdp?key={self.api_key}"
            
            firebase_data = {
                'postBody': f'access_token={token_result["access_token"]}&providerId=google.com',
                'requestUri': redirect_uri,
                'returnIdpCredential': True,
                'returnSecureToken': True
            }
            
            print("Autenticando con Firebase...")
            firebase_response = requests.post(firebase_auth_url, json=firebase_data)
            
            print(f"Status Firebase: {firebase_response.status_code}")
            print(f"Respuesta Firebase: {firebase_response.text[:200]}...")
            
            if firebase_response.status_code == 200:
                try:
                    firebase_result = firebase_response.json()
                    if 'idToken' in firebase_result:
                        self.user_data = {
                            'uid': firebase_result['localId'],
                            'email': firebase_result['email'],
                            'token': firebase_result['idToken']
                        }
                        self.save_session()
                        return True, f"Login con Google exitoso: {firebase_result['email']}"
                    else:
                        return False, f"No se recibió idToken de Firebase: {firebase_result}"
                except json.JSONDecodeError as e:
                    return False, f"Error parsing JSON de Firebase: {str(e)}"
            else:
                return False, f"Error en Firebase Auth: {firebase_response.status_code} - {firebase_response.text}"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error inesperado: {str(e)}"
    
    def logout(self):
        """Cierra sesión"""
        self.user_data = None
        self.clear_session()
        return True
    
    def is_logged_in(self):
        """Verifica si hay usuario logueado"""
        return self.user_data is not None
    
    def get_user_email(self):
        """Obtiene el email del usuario actual"""
        return self.user_data['email'] if self.user_data else None
    
    def get_user_id(self):
        """Obtiene el ID del usuario actual"""
        return self.user_data['uid'] if self.user_data else None
    
    def update_best_score(self, score, firebase_manager=None):
        """Actualiza la mejor puntuación local y en la nube"""
        # Actualizar local
        if score > self.local_best_score:
            self.save_local_best_score(score)
        
        # Actualizar en la nube si está logueado
        if self.is_logged_in() and firebase_manager:
            firebase_manager.save_user_best_score(
                self.get_user_id(), 
                score, 
                self.get_user_email()
            )
    
    def get_best_score(self):
        """Obtiene la mejor puntuación"""
        return self.local_best_score
    
    def save_session(self):
        """Guarda la sesión actual"""
        try:
            if self.user_data:
                os.makedirs("data/saves", exist_ok=True)
                with open("data/saves/session.json", 'w') as f:
                    json.dump(self.user_data, f)
        except Exception as e:
            print(f"Error guardando sesión: {e}")
    
    def load_saved_session(self):
        """Carga sesión guardada si existe"""
        try:
            if os.path.exists("data/saves/session.json"):
                with open("data/saves/session.json", 'r') as f:
                    self.user_data = json.load(f)
                    print(f"Sesión restaurada: {self.user_data['email']}")
        except Exception as e:
            print(f"Error cargando sesión: {e}")
    
    def clear_session(self):
        """Elimina la sesión guardada"""
        try:
            if os.path.exists("data/saves/session.json"):
                os.remove("data/saves/session.json")
        except Exception as e:
            print(f"Error eliminando sesión: {e}")