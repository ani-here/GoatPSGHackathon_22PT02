# Fleet Management System with Traffic Negotiation

Python-based system for multi-robot navigation with collision avoidance and traffic negotiation.

## Features

- Interactive graph-based navigation environment
- Visual robot management with real-time movement
- Priority-based traffic management
- Advanced collision avoidance with three core rules:
  - No crossing at vertices
  - No shared destinations
  - No shared lanes
- Status monitoring and event logging

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/fleet-management-system.git
cd fleet-management-system

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run with default graph
python src/main.py

# Run with specific graph
python src/main.py --nav_graph data/nav_graph_2.json
```

## Controls

- **S key**: Switch to Spawn mode
- **A key**: Switch to Assign mode 
- **Left-click**:
  - Spawn mode: Create a robot at clicked vertex
  - Assign mode: Select robot, then assign destination
- **ESC key**: Exit application

## System Architecture

- **NavGraph**: Manages vertices, lanes, and reservations
- **Robot**: Handles movement, pathfinding, and state
- **FleetManager**: Controls robot creation and task assignment
- **TrafficManager**: Implements collision avoidance and deadlock resolution
- **FleetGUI**: Provides visualization and user interaction

## Traffic Management

The system enforces three critical rules:

1. **No vertex crossing**: Robots cannot cross paths at the same vertex
2. **No shared destinations**: Two robots cannot target the same endpoint
3. **No shared lanes**: Only one robot can use a lane at any time

Traffic conflicts are resolved using a priority system based on waiting time.

## Visualization Guide

- **Vertices**: Blue circles (green for charging stations)
- **Lanes**: Gray arrows connecting vertices
- **Robots**: Colored circles with ID numbers
- **Status indicators**:
  - Green: Moving
  - Yellow: Waiting
  - Blue: Task completed
  - Cyan: Charging
- **Occupied lanes**: Highlighted in red
- **Occupied vertices**: Show color of occupying robot

The minimap in the bottom-right corner provides an overview of the entire navigation graph.

## Testing Scenarios

1. **Cross-path navigation**: Spawn robots at opposite ends, assign destinations requiring crossing
2. **Shared destination test**: Attempt to assign multiple robots to same destination
3. **Lane conflicts**: Create scenarios where robots need the same lane
4. **Priority resolution**: Observe how traffic jams are resolved based on waiting time
