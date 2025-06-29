# Configuración de Firebase

Los datos que tienes son de la configuración web, pero para Python necesitas **Service Account credentials**.

## Cómo obtener las credenciales correctas:

### 1. Ve a Firebase Console
- https://console.firebase.google.com/
- Selecciona tu proyecto

### 2. Ve a Project Settings
- Icono de engranaje → Project Settings
- Pestaña "Service accounts"

### 3. Generar nueva clave privada
- Click en "Generate new private key"
- Se descargará un archivo JSON

### 4. El archivo JSON contiene:
```json
{
  "type": "service_account",
  "project_id": "classicgame-dk",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@example-ex.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

### 5. Actualiza tu .env con estos valores:
```
FIREBASE_PROJECT_ID=classicgame-dk
FIREBASE_PRIVATE_KEY_ID=abc123...
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nTU_CLAVE_AQUI\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@classicgame-dk.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456789...
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...
```

### 6. Habilitar Firestore
- En Firebase Console → Firestore Database
- Click "Create database"
- Selecciona modo de prueba

## Nota importante:
- Mantén el archivo JSON seguro
- No lo subas a repositorios públicos