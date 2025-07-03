# Game Architecture Documentation

This document provides a comprehensive overview of the Donkey Kong Classic Game architecture, design patterns, and system organization.

## Architecture Overview

The game follows a modular, manager-based architecture that separates concerns and promotes maintainability. The system is built around the concept of specialized managers that handle different aspects of the game.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Game Manager  │────│  State Manager  │────│ Tutorial Manager│
│   (Coordinator) │    │   (Game Flow)   │    │   (Learning)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Entity Manager  │    │Collision Manager│    │   UI Manager    │
│   (Entities)    │    │   (Physics)     │    │  (Interface)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Level Manager  │    │ Firebase Manager│    │  Sound Manager  │
│   (Levels)      │    │   (Cloud Data)  │    │    (Audio)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Game Manager (`src/game/game_manager.py`)

**Purpose**: Central coordinator that orchestrates all game systems.

**Responsibilities**:
- Main game loop execution
- Manager coordination
- Event handling delegation
- Rendering coordination

**Key Methods**:
```python
def run(self):
    """Main game loop"""
    while self.running:
        self.handle_events()
        self.update()
        self.render()
        self.clock.tick(self.config.FPS)

def handle_events(self):
    """Delegates events to appropriate managers"""
    
def update(self):
    """Updates all game systems"""
    
def render(self):
    """Renders all visual elements"""
```

### 2. Entity Manager (`src/managers/entity_manager.py`)

**Purpose**: Manages all game entities (player, enemies, collectibles, projectiles).

**Responsibilities**:
- Entity lifecycle management
- Spawn control and timing
- Entity updates and interactions
- Rendering coordination

**Key Features**:
```python
class EntityManager:
    def __init__(self, config):
        self.player = None
        self.enemies = []
        self.collectibles = []
        self.projectiles = []
        
        # Spawn control
        self.spawn_timer = 0
        self.monster_spawn_timer = 0
        self.monsters_spawned = 0
```

**Spawn System**:
- Gradual enemy spawning (1 every 60 seconds)
- Maximum limits (3 barrels, configurable monsters)
- Automatic cleanup of inactive entities

### 3. Game State Manager (`src/managers/game_state_manager.py`)

**Purpose**: Manages game states and transitions.

**States**:
- `MENU` - Main menu
- `TUTORIAL` - Tutorial mode
- `PLAYING` - Active gameplay
- `PAUSED` - Game paused
- `SHOP` - In-game shop
- `GAME_OVER` - Game over screen
- `LEVEL_COMPLETE` - Level completion

**State Transitions**:
```python
def set_state(self, new_state):
    """Safe state transition with validation"""
    
def is_playing(self):
    """Check if in active gameplay states"""
    return self.state in ["PLAYING", "TUTORIAL"]
```

### 4. Collision Manager (`src/managers/collision_manager.py`)

**Purpose**: Handles all collision detection and response.

**Collision Types**:
- Player vs Enemies
- Player vs Collectibles  
- Projectiles vs Enemies
- Entity vs Environment

**Collision Response**:
```python
def check_all_collisions(self, entity_manager, collectibles_collected, collectibles_needed):
    """Comprehensive collision checking"""
    # Enemy collisions -> damage/game over
    # Collectible collisions -> scoring
    # Projectile collisions -> enemy destruction
    # Level completion checking
```

### 5. Level Manager (`src/managers/level_manager.py`)

**Purpose**: Generates and manages game levels.

**Level Types**:
- **Fixed Levels** (1-3): Hand-designed levels
- **Procedural Levels** (4+): Algorithmically generated

**Procedural Generation**:
```python
def create_random_level(self, level_number):
    """Generates random level based on difficulty"""
    difficulty = min(level_number - 3, 10)
    
    # Generate 3-6 platform layers
    num_layers = random.randint(3, 6)
    
    # 2-4 platforms per layer
    # Random platform sizes (80-150px)
    # Strategic ladder placement
    # Difficulty-scaled enemy count
```

## Entity System

### Entity Hierarchy

```
Entity (Base)
├── Player
│   ├── Movement System
│   ├── Animation System
│   └── Inventory System
├── Enemy
│   ├── Barrel (AI-driven)
│   └── Monster (State-machine)
├── Collectible
│   └── Star (Point values: 10, 20, 50)
└── Projectile
    └── Banana (Explosive)
```

### Player System (`src/entities/player.py`)

**Features**:
- Sprite-based animation (12 frames for jump sequence)
- Physics-based movement
- Inventory management (bananas, lives, score)
- Input handling

**Animation System**:
```python
def update_animation(self):
    """Handles sprite animation based on state"""
    if not self.on_ground and self.sprites['jump']:
        # Play jump animation sequence
        if not self.is_jumping_animation:
            self.is_jumping_animation = True
            self.jump_frame = 0
```

### Enemy System (`src/entities/enemy.py`)

**Barrel Enemy**:
- Hybrid AI (Rule-based + Q-Learning)
- Platform navigation
- Adaptive pause system
- Anti-stuck mechanisms

**Monster Enemy**:
- Three-state behavior (Falling → Waiting → Hunting)
- Visual state indicators
- Timed state transitions

## AI Architecture

### Hybrid AI System

The game implements a sophisticated AI system that combines multiple approaches:

1. **Primary Decision Layer**: Rule-based logic for reliable behavior
2. **Validation Layer**: Q-Learning for behavior refinement
3. **Safety Layer**: Anti-stuck and fallback mechanisms

```python
def barrel_movement(self, platforms, player_rect=None):
    # 1. Rule-based primary decision
    primary_action = self.decide_primary_action(dx, dy, current_platform, player_platform)
    
    # 2. Q-Learning validation
    if hasattr(self, 'ai_agent'):
        q_action = self.ai_agent.choose_action(state)
        if self.should_override_action(primary_action, q_action, dx, dy):
            primary_action = q_action
    
    # 3. Execute decision
    self.execute_action_decision(primary_action, current_platform, dx)
```

### Learning System

**Q-Learning Implementation**:
- State space: 6 dimensions (positions, direction, ground contact)
- Action space: 4 actions (left, right, jump, drop)
- Reward function: Distance-based with bonuses/penalties
- Learning parameters: α=0.1, γ=0.95, ε=0.2

## Data Management

### Firebase Integration (`src/managers/firebase_manager.py`)

**Services Used**:
- **Realtime Database**: Leaderboards and cloud saves
- **Authentication**: User management
- **REST API**: Direct HTTP communication (no SDK)

**Data Structure**:
```json
{
  "leaderboard": {
    "user_id": {
      "email": "player@example.com",
      "best_score": 1500,
      "timestamp": 1640995200
    }
  },
  "cloud_saves": {
    "user_id": {
      "save_data": {
        "level": 3,
        "score": 1200,
        "lives": 2
      },
      "last_updated": 1640995200
    }
  }
}
```

### Local Data Management

**Save System** (`src/managers/save_manager.py`):
- JSON-based local saves
- Player progress persistence
- Game state serialization

**Configuration** (`src/utils/config.py`):
- Game constants
- Color definitions
- Physics parameters

## UI System

### Menu System (`src/ui/`)

**Components**:
- Main Menu
- Shop Menu (with item images)
- Pause Menu
- Game Over Screen
- Leaderboard Display

**Shop System**:
```python
class ShopMenu:
    def load_item_images(self):
        """Loads item icons from assets/shop/"""
        
    def render(self, screen, player, shop_manager):
        """Renders shop with images and player stats"""
```

### HUD System

**In-Game Display**:
- Lives counter
- Score display
- Shop indicator
- Tutorial instructions

## Asset Management

### Sprite System

**Player Sprites**:
- `sprite_00.png` - Idle state
- `sprite_01.png` to `sprite_11.png` - Jump sequence

**Enemy Sprites**:
- `enemy1.png`, `enemy2.png`, `enemy3.png` - Animation frames
- Automatic scaling to entity size
- Direction-based sprite flipping

**Shop Icons**:
- `banana.png` - Banana item
- `heart.png` - Extra life
- Automatic loading and scaling

### Sound System (`src/managers/sound_manager.py`)

**Audio Management**:
- Background music
- Sound effects (jump, damage, points)
- Volume control
- Format support (WAV, OGG)

## Performance Optimization

### Entity Management

**Optimization Strategies**:
- Inactive entity cleanup
- Spawn rate limiting
- Collision optimization (spatial partitioning concepts)

**Memory Management**:
- Sprite caching
- Asset preloading
- Garbage collection awareness

### Rendering Optimization

**Techniques**:
- Dirty rectangle updates
- Sprite batching
- Efficient collision detection

## Error Handling

### Robust Systems

**Firebase Fallbacks**:
```python
def get_global_leaderboard(self, limit=10):
    try:
        # Firebase operation
        return data
    except Exception as e:
        print(f"Error: {e}")
        return []  # Graceful fallback
```

**Asset Loading**:
```python
def load_sprites(self):
    sprites = []
    for path in sprite_paths:
        if os.path.exists(path):
            try:
                sprite = pygame.image.load(path)
                sprites.append(sprite)
            except:
                pass  # Continue without sprite
    return sprites if sprites else None
```

## Configuration Management

### Environment Variables

**Security**:
- Sensitive data in `.env`
- `.gitignore` protection
- Example configuration (`.env.example`)

**Game Settings**:
```python
class Config:
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 60
    
    COLORS = {
        'BLACK': (0, 0, 0),
        'WHITE': (255, 255, 255),
        # ... more colors
    }
```

## Testing Strategy

### Unit Testing Structure

```
tests/
├── test_entities.py      # Entity behavior tests
├── test_ai.py           # AI algorithm tests
├── test_managers.py     # Manager functionality tests
└── test_integration.py  # Integration tests
```

### Testing Approaches

**AI Testing**:
- Q-Learning convergence tests
- Behavior validation
- Performance benchmarks

**Game Logic Testing**:
- Collision detection accuracy
- State transition validation
- Score calculation verification

## Deployment Architecture

### Build System (`build.py`)

**PyInstaller Configuration**:
- Asset bundling
- Dependency resolution
- Cross-platform compatibility

**Distribution**:
- Single executable generation
- Asset packaging
- Configuration inclusion

This architecture provides a solid foundation for a maintainable, extensible, and performant game while maintaining clean separation of concerns and robust error handling.