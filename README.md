# Donkey Kong Classic Game

Un juego clásico estilo Donkey Kong desarrollado en Python con Pygame, que incluye inteligencia artificial usando Q-Learning y persistencia de datos con Firebase.

## Características

- 🎮 Mecánicas clásicas de plataformas
- 🤖 Enemigos con IA usando Q-Learning
- ☁️ Persistencia de datos con Firebase
- 🎯 Sistema de puntuación y vidas
- 📱 Preparado para empaquetado como ejecutable

## Instalación

1. Clona el repositorio
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura Firebase:
   - Crea un proyecto en Firebase Console
   - Descarga las credenciales del servicio
   - Actualiza el archivo `.env` con tus credenciales

4. Ejecuta el juego:
```bash
python main.py
```

## Estructura del Proyecto

```
ClassicGame/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── .env                   # Variables de entorno
├── build.py               # Script de empaquetado
├── src/
│   ├── game/              # Lógica principal del juego
│   ├── entities/          # Jugador y enemigos
│   ├── ai/                # Algoritmos de IA
│   ├── ui/                # Interfaz de usuario
│   └── utils/             # Utilidades y configuración
├── assets/                # Recursos gráficos y sonoros
├── data/                  # Datos persistentes y modelos
└── tests/                 # Pruebas unitarias
```

## Controles

- **Flechas/WASD**: Movimiento
- **Espacio**: Saltar
- **ESC**: Pausar juego

## Empaquetado

Para crear un ejecutable:

```bash
python build.py
```

El ejecutable se generará en la carpeta `dist/`.

## Configuración de Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Crea un nuevo proyecto
3. Habilita Firestore Database
4. Genera credenciales de cuenta de servicio
5. Actualiza el archivo `.env` con tus credenciales

## Desarrollo

El juego utiliza una arquitectura modular:

- **GameManager**: Controla el bucle principal
- **Player**: Maneja las mecánicas del jugador
- **Enemy**: Enemigos con IA Q-Learning
- **Level**: Estructura de niveles
- **QLearningAgent**: Algoritmo de aprendizaje por refuerzo

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.