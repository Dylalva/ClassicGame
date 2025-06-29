# Configuración Completa de Firebase Authentication

## 1. Configuración en Firebase Console

### Paso 1: Habilitar Authentication
1. Ve a Firebase Console → Tu proyecto
2. En el menú lateral: **Authentication**
3. Click en **Get started**
4. Ve a la pestaña **Sign-in method**

### Paso 2: Habilitar Email/Password
1. Click en **Email/Password**
2. Habilita **Email/Password** (primera opción)
3. **Guardar**

### Paso 3: Habilitar Google Sign-In
1. Click en **Google**
2. Habilitar **Google Sign-In**
3. Seleccionar email de soporte del proyecto
4. **Guardar**

### Paso 4: Configurar dominios autorizados
1. En **Settings** → **Authorized domains**
2. Agregar: `localhost` (para desarrollo)

## 2. Obtener Web API Key

### En Project Settings:
1. **⚙️ Project Settings** → Pestaña **General**
2. En **Your apps** → **Web app**
3. Copiar el **Web API Key**

### Actualizar auth_manager.py:
```python
self.api_key = "TU_WEB_API_KEY_AQUI"  # Línea 15
```

## 3. Configurar Google OAuth (Opcional)

### Para Google Sign-In completo:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto Firebase
3. **APIs & Services** → **Credentials**
4. **Create Credentials** → **OAuth 2.0 Client ID**
5. **Application type**: Web application
6. **Authorized redirect URIs**: `http://localhost:8080`
7. Copiar **Client ID**

### Actualizar auth_manager.py:
```python
google_auth_url = f"https://accounts.google.com/oauth/authorize?client_id=TU_GOOGLE_CLIENT_ID&..."
```

## 4. Habilitar Firestore

### Para guardar datos:
1. Firebase Console → **Firestore Database**
2. **Create database**
3. **Start in test mode** (para desarrollo)
4. Seleccionar región

### Reglas de Firestore (para desarrollo):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

## 5. Estructura de Datos en Firestore

### Colecciones que se crearán automáticamente:
- `users` - Progreso de usuarios
- `leaderboard` - Mejores puntuaciones
- `cloud_saves` - Partidas guardadas en la nube

## 6. Variables de Entorno Necesarias

### En tu .env (ya configurado):
```
FIREBASE_PROJECT_ID=classicgame-dk
# ... resto de configuración Service Account
```

### Agregar Web API Key:
```
FIREBASE_WEB_API_KEY=tu_web_api_key_aqui
```

## 7. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

## 8. Prueba de Funcionamiento

### El sistema incluye:
- ✅ Registro con email/contraseña
- ✅ Login con email/contraseña  
- ✅ Login con Google (abre navegador)
- ✅ Guardado de mejor puntuación local
- ✅ Sincronización con la nube
- ✅ Ranking global
- ✅ Guardado de partidas en la nube

### Flujo de autenticación:
1. **Primera vez**: Pantalla de login
2. **Registro/Login**: Credenciales o Google
3. **Juego**: Progreso se guarda automáticamente
4. **Ranking**: Ver mejores puntuaciones globales

## 9. Seguridad para Producción

### Cuando publiques el juego:
1. Cambiar reglas de Firestore para requerir autenticación
2. Configurar dominios autorizados reales
3. Usar variables de entorno seguras
4. Habilitar App Check para mayor seguridad

## Notas Importantes:
- El Web API Key es público y seguro para usar en cliente
- Las credenciales Service Account son privadas
- Google Sign-In abre el navegador web del usuario
- Los datos se sincronizan automáticamente entre local y nube