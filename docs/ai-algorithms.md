# AI Algorithms Documentation

This document explains the artificial intelligence algorithms implemented in the Donkey Kong Classic Game.

## Overview

The game implements a hybrid AI system that combines rule-based behavior with reinforcement learning (Q-Learning) to create intelligent enemy behavior that adapts to player patterns.

## Q-Learning Algorithm

### What is Q-Learning?

Q-Learning is a model-free reinforcement learning algorithm that learns the quality of actions, telling an agent what action to take under what circumstances.

### Implementation Details

#### State Space
The AI agent observes a 6-dimensional state space:

```python
state = [
    enemy_x / window_width,      # Normalized enemy X position (0-1)
    enemy_y / window_height,     # Normalized enemy Y position (0-1)
    player_x / window_width,     # Normalized player X position (0-1)
    player_y / window_height,    # Normalized player Y position (0-1)
    (direction + 1) / 2,         # Normalized direction (-1,1) → (0,1)
    1 if on_ground else 0        # Ground contact boolean
]
```

#### Action Space
The agent can choose from 4 possible actions:

```python
actions = {
    0: "Move Left",      # Move enemy left
    1: "Move Right",     # Move enemy right  
    2: "Jump",           # Jump to higher platform
    3: "Drop/Wait"       # Drop to lower platform or wait
}
```

#### Reward Function
The reward system encourages the AI to get closer to the player:

```python
def calculate_reward(self, player_rect):
    if player_rect is None:
        return -0.1
    
    # Distance-based reward
    distance = sqrt((enemy_x - player_x)² + (enemy_y - player_y)²)
    max_distance = sqrt(window_width² + window_height²)
    proximity_reward = (max_distance - distance) / max_distance
    
    # Bonus for being on same platform
    same_platform_bonus = 0.3 if abs(enemy_y - player_y) < 30 else 0
    
    # Penalty for being stuck
    stuck_penalty = -0.2 if stuck_timer > 60 else 0
    
    return proximity_reward + same_platform_bonus + stuck_penalty
```

#### Learning Parameters

```python
learning_rate = 0.1        # How fast the agent learns
discount_factor = 0.95     # Future reward importance
epsilon = 0.2              # Exploration vs exploitation balance
```

### Q-Learning Update Rule

The Q-value is updated using the Bellman equation:

```
Q(s,a) = Q(s,a) + α[r + γ·max(Q(s',a')) - Q(s,a)]
```

Where:
- `α` = learning rate
- `r` = immediate reward
- `γ` = discount factor
- `s'` = next state
- `a'` = next action

## Hybrid AI Architecture

### Primary Decision System (Rule-Based)

The AI uses rule-based logic as the primary decision-making system:

```python
def decide_primary_action(self, dx, dy, current_platform, player_platform):
    # Force drop if at platform edge
    if at_platform_edge():
        return DROP_ACTION
    
    # Jump if player is above
    if dy < -40 and abs(dx) < 100:
        return JUMP_ACTION
    
    # Move horizontally toward player
    if abs(dx) > 10:
        return RIGHT_ACTION if dx > 0 else LEFT_ACTION
    
    return RIGHT_ACTION  # Default behavior
```

### Q-Learning Validation System

Q-Learning acts as a validation and improvement layer:

```python
def should_override_action(self, primary_action, q_action, dx, dy):
    # Only override in specific situations
    if primary_action == q_action:
        return False
    
    # Allow override when very close to player
    if abs(dx) < 50 and abs(dy) < 50:
        return True
    
    return False
```

## Enemy Behavior Types

### Barrel Enemies

**Characteristics:**
- Speed: 1.8 pixels/frame (70% of original)
- Behavior: Rolling and platform navigation
- AI: Hybrid rule-based + Q-Learning

**Behavior States:**
1. **Rolling**: Normal horizontal movement
2. **Edge Detection**: Identifies platform boundaries
3. **Platform Navigation**: Jumps between platforms
4. **Player Pursuit**: Actively chases player

**Special Features:**
- Automatic platform dropping
- Periodic pause system (decreasing duration)
- Anti-stuck mechanisms
- Smart platform navigation

### Monster Enemies

**Characteristics:**
- Speed: 1.1 pixels/frame (70% of original)
- Behavior: Three-state system
- AI: State machine based

**Behavior States:**

1. **Falling State**
   ```python
   # Falls from sky for 5-8 seconds
   duration = random.randint(300, 480)  # frames
   velocity_x = 0  # No horizontal movement
   ```

2. **Waiting State**
   ```python
   # Stays still for 1-2 seconds
   duration = random.randint(60, 120)  # frames
   velocity_x = 0
   # Visual indicator: yellow circle
   ```

3. **Hunting State**
   ```python
   # Actively pursues player
   if abs(dx) > 10:
       direction = 1 if dx > 0 else -1
       velocity_x = speed * direction
   
   # Jump if player is above
   if dy < -40 and abs(dx) < 60:
       velocity_y = -10
   ```

## Advanced AI Features

### Adaptive Pause System

Enemies implement a dynamic pause system:

```python
# Initial pause: 1 second every 5 seconds
pause_duration = 60      # frames (1 second)
pause_cycle = 300        # frames (5 seconds)
pause_reduction = 5      # frames to reduce each time

# Each pause gets shorter
new_duration = max(10, pause_duration - pause_reduction)
```

### Platform Navigation Intelligence

The AI can intelligently navigate between platforms:

```python
def should_actively_drop(self, current_platform, player_platform):
    # Drop if player is on lower platform
    if player_platform.top > current_platform.top:
        return True
    
    # Drop if at platform edge
    if at_platform_edge():
        return True
    
    return False
```

### Anti-Stuck Mechanisms

Multiple systems prevent AI from getting stuck:

1. **Movement Detection**
   ```python
   if abs(velocity_x) < 0.1 and stuck_timer > 60:
       # Change direction or jump
       if random.random() < 0.7:
           direction *= -1
       else:
           jump()
   ```

2. **Platform Timer**
   ```python
   platform_change_timer += 1
   if platform_change_timer > 300:  # 5 seconds
       force_platform_change()
   ```

## Performance Optimization

### State Space Normalization

All state values are normalized to [0,1] range for better learning:

```python
normalized_x = x_position / window_width
normalized_y = y_position / window_height
```

### Experience Replay

The Q-Learning agent learns from each action immediately:

```python
# Learn from current experience
reward = calculate_reward(player_rect)
next_state = get_state(player_rect)
done = not self.active
agent.learn(state, action, reward, next_state, done)
```

### Epsilon-Greedy Exploration

Balances exploration vs exploitation:

```python
if random.random() < epsilon:
    action = random.choice(available_actions)  # Explore
else:
    action = argmax(Q_values)  # Exploit
```

## Tuning Parameters

### Learning Rate (α = 0.1)
- **Higher values**: Faster learning, less stable
- **Lower values**: Slower learning, more stable
- **Current**: Balanced for real-time gameplay

### Discount Factor (γ = 0.95)
- **Higher values**: More future-focused
- **Lower values**: More immediate reward focused
- **Current**: Long-term strategy emphasis

### Exploration Rate (ε = 0.2)
- **Higher values**: More random exploration
- **Lower values**: More exploitation of learned behavior
- **Current**: 20% exploration maintains adaptability

## Future Improvements

### Potential Enhancements

1. **Deep Q-Learning (DQN)**
   - Neural network for Q-value approximation
   - Better handling of large state spaces

2. **Multi-Agent Learning**
   - Enemies learn from each other
   - Coordinated attack strategies

3. **Player Modeling**
   - Learn specific player patterns
   - Adapt to individual play styles

4. **Hierarchical Learning**
   - High-level strategy selection
   - Low-level action execution

### Implementation Considerations

```python
# Example: Player pattern recognition
player_patterns = {
    'jump_frequency': track_jump_timing(),
    'movement_preference': track_direction_bias(),
    'platform_usage': track_platform_preference()
}

# Adapt AI behavior based on patterns
if player_patterns['jump_frequency'] > threshold:
    increase_jump_prediction()
```

## Debugging and Monitoring

### AI State Visualization

The game includes visual indicators for AI states:

```python
# Monster waiting state indicator
if enemy_type == "monster" and state == "waiting":
    pygame.draw.circle(screen, (255, 255, 0), 
                      (rect.centerx, rect.top - 10), 3)
```

### Performance Metrics

Key metrics to monitor AI performance:

1. **Learning Convergence**: Q-values stabilization
2. **Player Catch Rate**: Successful player contacts
3. **Platform Navigation**: Successful platform changes
4. **Stuck Incidents**: Times anti-stuck mechanisms activate

This AI system creates challenging, adaptive enemies that provide engaging gameplay while maintaining the classic Donkey Kong feel.