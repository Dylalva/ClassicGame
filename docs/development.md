# Development Guide

This guide provides comprehensive information for developers who want to contribute to or modify the Donkey Kong Classic Game.

## Development Environment Setup

### Prerequisites

- **Python 3.12+** (recommended)
- **Git** for version control
- **Code editor** (VS Code, PyCharm, etc.)
- **Firebase account** (for cloud features)

### Initial Setup

1. **Clone and Setup**
```bash
git clone <repository-url>
cd ClassicGame
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your Firebase credentials
```

3. **Verify Installation**
```bash
python main.py
```

## Project Structure Deep Dive

### Core Directories

```
ClassicGame/
├── src/                    # Source code
│   ├── game/              # Core game logic
│   │   ├── game_manager.py    # Main coordinator
│   │   └── level.py           # Level definitions
│   ├── entities/          # Game objects
│   │   ├── player.py          # Player character
│   │   ├── enemy.py           # AI enemies
│   │   ├── collectible.py     # Items to collect
│   │   └── projectile.py      # Throwable objects
│   ├── managers/          # System managers
│   │   ├── entity_manager.py      # Entity lifecycle
│   │   ├── collision_manager.py   # Physics/collisions
│   │   ├── game_state_manager.py  # State management
│   │   ├── tutorial_manager.py    # Tutorial system
│   │   ├── level_manager.py       # Level generation
│   │   ├── firebase_manager.py    # Cloud integration
│   │   ├── sound_manager.py       # Audio system
│   │   ├── save_manager.py        # Local saves
│   │   ├── shop_manager.py        # Shop logic
│   │   └── ui_manager.py          # UI coordination
│   ├── ai/                # Artificial Intelligence
│   │   └── q_learning.py      # Q-Learning algorithm
│   ├── ui/                # User Interface
│   │   └── shop_menu.py       # Shop interface
│   └── utils/             # Utilities
│       └── config.py          # Game configuration
├── assets/                # Game assets
│   ├── player/            # Player sprites
│   ├── enemy/             # Enemy sprites
│   └── shop/              # Shop icons
├── data/                  # Persistent data
├── docs/                  # Documentation
└── tests/                 # Unit tests
```

## Development Workflow

### Adding New Features

1. **Create Feature Branch**
```bash
git checkout -b feature/new-feature-name
```

2. **Follow Architecture Patterns**
- Use manager pattern for new systems
- Implement proper error handling
- Add configuration options to `config.py`

3. **Testing**
```bash
python -m pytest tests/
```

4. **Documentation**
- Update relevant documentation
- Add docstrings to new functions
- Update README if needed

### Code Style Guidelines

#### Python Style

Follow PEP 8 with these specifics:

```python
# Class naming: PascalCase
class EntityManager:
    pass

# Function/variable naming: snake_case
def update_entities(self):
    player_position = self.get_player_position()

# Constants: UPPER_CASE
MAX_ENEMIES = 10
DEFAULT_SPEED = 5

# Docstrings: Google style
def calculate_distance(self, point_a, point_b):
    """Calculates Euclidean distance between two points.
    
    Args:
        point_a (tuple): First point (x, y)
        point_b (tuple): Second point (x, y)
    
    Returns:
        float: Distance between points
    """
```

#### Game-Specific Patterns

**Manager Pattern**:
```python
class NewManager:
    def __init__(self, config):
        self.config = config
        # Initialize manager state
    
    def update(self):
        """Update manager state each frame"""
        pass
    
    def render(self, screen):
        """Render manager visuals"""
        pass
```

**Entity Pattern**:
```python
class NewEntity:
    def __init__(self, x, y, config):
        self.rect = pygame.Rect(x, y, width, height)
        self.config = config
        self.active = True
    
    def update(self, *args):
        """Update entity state"""
        pass
    
    def render(self, screen):
        """Render entity"""
        pass
```

## Adding New Entities

### Step 1: Create Entity Class

```python
# src/entities/new_entity.py
import pygame

class NewEntity:
    def __init__(self, x, y, config):
        self.config = config
        self.rect = pygame.Rect(x, y, 30, 30)
        self.velocity_x = 0
        self.velocity_y = 0
        self.active = True
        
        # Load sprites
        self.sprites = self.load_sprites()
        
    def load_sprites(self):
        """Load entity sprites"""
        # Implementation here
        pass
    
    def update(self):
        """Update entity logic"""
        # Physics, AI, etc.
        pass
    
    def render(self, screen):
        """Render entity"""
        if self.sprites:
            screen.blit(self.sprites[0], self.rect)
        else:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)
```

### Step 2: Integrate with Entity Manager

```python
# In src/managers/entity_manager.py
from src.entities.new_entity import NewEntity

class EntityManager:
    def __init__(self, config):
        # ... existing code ...
        self.new_entities = []
    
    def spawn_new_entity(self, x, y):
        """Spawn new entity"""
        entity = NewEntity(x, y, self.config)
        self.new_entities.append(entity)
    
    def update_all(self, platforms=None):
        # ... existing updates ...
        
        # Update new entities
        for entity in self.new_entities[:]:
            entity.update()
            if not entity.active:
                self.new_entities.remove(entity)
    
    def render_all(self, screen):
        # ... existing rendering ...
        
        # Render new entities
        for entity in self.new_entities:
            entity.render(screen)
```

### Step 3: Add Collision Handling

```python
# In src/managers/collision_manager.py
def check_new_entity_collisions(self, entity_manager):
    """Check collisions with new entities"""
    for entity in entity_manager.new_entities[:]:
        if entity_manager.player.rect.colliderect(entity.rect):
            # Handle collision
            pass
```

## Adding New AI Behaviors

### Step 1: Extend Q-Learning Agent

```python
# In src/ai/q_learning.py
class QLearningAgent:
    def add_new_action(self, action_id, action_name):
        """Add new action to action space"""
        self.action_size += 1
        # Resize Q-table if needed
```

### Step 2: Implement Behavior

```python
# In enemy behavior
def new_behavior_pattern(self, player_rect, platforms):
    """New AI behavior pattern"""
    # Get current state
    state = self.get_state(player_rect)
    
    # Choose action
    action = self.ai_agent.choose_action(state)
    
    # Execute new behavior
    if action == NEW_ACTION_ID:
        # Implement new behavior
        pass
    
    # Learn from action
    reward = self.calculate_reward(player_rect)
    next_state = self.get_state(player_rect)
    self.ai_agent.learn(state, action, reward, next_state, False)
```

## Adding New Game States

### Step 1: Define State

```python
# In src/managers/game_state_manager.py
class GameStateManager:
    def __init__(self, config):
        # ... existing code ...
        self.valid_states = [
            "MENU", "TUTORIAL", "PLAYING", "PAUSED", 
            "SHOP", "GAME_OVER", "NEW_STATE"  # Add here
        ]
    
    def handle_new_state(self):
        """Handle new state logic"""
        pass
```

### Step 2: Add State Transitions

```python
# In src/game/game_manager.py
def handle_events(self):
    # ... existing event handling ...
    
    elif current_state == "NEW_STATE":
        # Handle new state events
        action = self.handle_new_state_events(event)
        if action == "TRANSITION":
            self.game_state_manager.set_state("TARGET_STATE")
```

### Step 3: Add Rendering

```python
def render(self):
    # ... existing rendering ...
    
    elif self.game_state_manager.get_state() == "NEW_STATE":
        self.render_new_state()

def render_new_state(self):
    """Render new state UI"""
    # Implementation here
    pass
```

## Performance Optimization

### Profiling

Use Python's built-in profiler:

```python
import cProfile
import pstats

def profile_game():
    """Profile game performance"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run game loop
    game.run()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

### Common Optimizations

**Sprite Caching**:
```python
class SpriteCache:
    _cache = {}
    
    @classmethod
    def get_sprite(cls, path, size):
        key = (path, size)
        if key not in cls._cache:
            sprite = pygame.image.load(path)
            sprite = pygame.transform.scale(sprite, size)
            cls._cache[key] = sprite
        return cls._cache[key]
```

**Collision Optimization**:
```python
def optimized_collision_check(self, entities):
    """Use spatial partitioning for collision detection"""
    # Group entities by screen regions
    regions = self.partition_entities(entities)
    
    # Only check collisions within same region
    for region in regions:
        for i, entity_a in enumerate(region):
            for entity_b in region[i+1:]:
                if entity_a.rect.colliderect(entity_b.rect):
                    self.handle_collision(entity_a, entity_b)
```

## Testing

### Unit Testing

Create tests for new components:

```python
# tests/test_new_entity.py
import unittest
from src.entities.new_entity import NewEntity
from src.utils.config import Config

class TestNewEntity(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.entity = NewEntity(100, 100, self.config)
    
    def test_initialization(self):
        """Test entity initialization"""
        self.assertEqual(self.entity.rect.x, 100)
        self.assertEqual(self.entity.rect.y, 100)
        self.assertTrue(self.entity.active)
    
    def test_update(self):
        """Test entity update logic"""
        initial_x = self.entity.rect.x
        self.entity.velocity_x = 5
        self.entity.update()
        self.assertEqual(self.entity.rect.x, initial_x + 5)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
# tests/test_integration.py
def test_entity_manager_integration():
    """Test entity manager with multiple entities"""
    config = Config()
    entity_manager = EntityManager(config)
    
    # Spawn entities
    entity_manager.spawn_new_entity(100, 100)
    entity_manager.spawn_new_entity(200, 200)
    
    # Update
    entity_manager.update_all()
    
    # Verify
    assert len(entity_manager.new_entities) == 2
```

## Debugging

### Debug Mode

Add debug visualization:

```python
class Config:
    DEBUG_MODE = True  # Set via environment variable
    
    # Debug colors
    DEBUG_COLORS = {
        'COLLISION_BOX': (255, 0, 0),
        'AI_STATE': (0, 255, 0),
        'PATH_FINDING': (0, 0, 255)
    }
```

### Debug Rendering

```python
def render_debug_info(self, screen):
    """Render debug information"""
    if not self.config.DEBUG_MODE:
        return
    
    # Draw collision boxes
    for entity in self.entities:
        pygame.draw.rect(screen, self.config.DEBUG_COLORS['COLLISION_BOX'], 
                        entity.rect, 2)
    
    # Draw AI state
    font = pygame.font.Font(None, 24)
    for enemy in self.enemies:
        if hasattr(enemy, 'ai_agent'):
            state_text = font.render(f"State: {enemy.current_state}", 
                                   True, self.config.DEBUG_COLORS['AI_STATE'])
            screen.blit(state_text, (enemy.rect.x, enemy.rect.y - 25))
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug(f"Entity spawned at {x}, {y}")
logger.info(f"Level {level_number} completed")
logger.warning(f"Low performance detected: {fps} FPS")
logger.error(f"Failed to load sprite: {sprite_path}")
```

## Asset Management

### Adding New Assets

1. **Sprites**: Place in appropriate `assets/` subdirectory
2. **Naming Convention**: `entity_state_frame.png`
3. **Size Guidelines**: Consistent sizing within entity types
4. **Format**: PNG with transparency support

### Asset Loading Pattern

```python
def load_asset_safely(self, path, default_size=(32, 32)):
    """Safely load game asset with fallback"""
    try:
        if os.path.exists(path):
            sprite = pygame.image.load(path)
            return pygame.transform.scale(sprite, default_size)
    except Exception as e:
        logger.warning(f"Failed to load asset {path}: {e}")
    
    # Return colored rectangle as fallback
    surface = pygame.Surface(default_size)
    surface.fill((255, 0, 255))  # Magenta for missing assets
    return surface
```

## Deployment

### Building Executable

```python
# build.py
import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--add-data', 'assets;assets',
    '--add-data', '.env;.',
    '--name', 'DonkeyKongClassic',
    '--icon', 'assets/icon.ico'
])
```

### Distribution Checklist

- [ ] All assets included
- [ ] Environment variables configured
- [ ] Dependencies resolved
- [ ] Cross-platform testing
- [ ] Performance validation
- [ ] Error handling verification

## Contributing Guidelines

### Pull Request Process

1. **Fork** the repository
2. **Create** feature branch
3. **Implement** changes with tests
4. **Update** documentation
5. **Submit** pull request with description

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No performance regressions
- [ ] Error handling implemented
- [ ] Assets properly managed

This development guide provides the foundation for contributing to and extending the Donkey Kong Classic Game. Follow these patterns and guidelines to maintain code quality and system architecture.