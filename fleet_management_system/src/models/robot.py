import time
import numpy as np

class Robot:
    """Robot class for the fleet management system."""
    
    # Define possible robot states
    IDLE = "idle"
    MOVING = "moving"
    WAITING = "waiting"
    CHARGING = "charging"
    COMPLETED = "completed"
    
    def __init__(self, robot_id, start_vertex, nav_graph, color):
        """
        Initialize a robot.
        
        Args:
            robot_id (int): Unique robot identifier
            start_vertex (int): Starting vertex ID
            nav_graph (NavGraph): Reference to the navigation graph
            color (tuple): RGB color tuple for visualization
        """
        self.id = robot_id
        self.current_vertex = start_vertex
        self.nav_graph = nav_graph
        self.color = color
        
        self.state = self.IDLE
        self.path = []
        self.current_path_index = 0
        self.target_vertex = None
        
        self.position = nav_graph.get_scaled_position(start_vertex)
        self.target_position = self.position
        self.move_speed = 2.0  # pixels per tick
        self.last_action_time = time.time()
        
        # Reserve the initial position
        self.nav_graph.reserve_vertex(start_vertex, self.id)
    
    def assign_task(self, destination_vertex):
        """
        Assign a navigation task to the robot.
        
        Args:
            destination_vertex (int): Destination vertex ID
        
        Returns:
            bool: True if task was successfully assigned, False otherwise
        """
        if self.state != self.IDLE and self.state != self.COMPLETED:
            return False
        
        # Calculate path to destination
        path = self.nav_graph.get_shortest_path(self.current_vertex, destination_vertex)
        if path is None:
            return False
        
        self.path = path
        self.current_path_index = 0
        self.target_vertex = destination_vertex
        self.state = self.IDLE  # Will start moving in the next update
        
        return True
    
    def update(self, delta_time):
        """
        Update the robot's state and position.
        
        Args:
            delta_time (float): Time elapsed since last update in seconds
        
        Returns:
            dict: Status update for logging
        """
        status_update = {
            'robot_id': self.id,
            'state': self.state,
            'position': self.current_vertex,
            'event': None
        }
        
        # If robot is at a charger and idle, start charging
        if self.state == self.IDLE:
            current_vertex_data = self.nav_graph.vertices[self.current_vertex]
            if current_vertex_data.get('is_charger', False):
                self.state = self.CHARGING
                status_update['state'] = self.state
                status_update['event'] = 'started_charging'
                return status_update
        
        # If robot has a path to follow
        if self.path and self.current_path_index < len(self.path) - 1:
            # If in IDLE state, start moving
            if self.state == self.IDLE or self.state == self.CHARGING:
                # Try to reserve the next vertex and lane
                next_vertex = self.path[self.current_path_index + 1]
                
                can_reserve_lane = self.nav_graph.reserve_lane(
                    self.current_vertex, next_vertex, self.id)
                
                if can_reserve_lane:
                    # Release current vertex
                    self.nav_graph.release_vertex(self.current_vertex, self.id)
                    
                    # Start moving
                    self.state = self.MOVING
                    self.target_position = self.nav_graph.get_scaled_position(next_vertex)
                    
                    status_update['state'] = self.state
                    status_update['event'] = f'moving_to_{next_vertex}'
                else:
                    # Wait for path to clear
                    self.state = self.WAITING
                    status_update['state'] = self.state
                    status_update['event'] = f'waiting_for_lane_to_{next_vertex}'
            
            # If moving, update position
            elif self.state == self.MOVING:
                current_pos = np.array(self.position)
                target_pos = np.array(self.target_position)
                direction = target_pos - current_pos
                distance = np.linalg.norm(direction)
                
                # If reached target position
                if distance < self.move_speed:
                    self.position = self.target_position
                    
                    # Advance to next vertex in path
                    self.current_path_index += 1
                    next_vertex = self.path[self.current_path_index]
                    
                    # Release the lane we just traversed
                    prev_vertex = self.path[self.current_path_index - 1]
                    self.nav_graph.release_lane(prev_vertex, next_vertex, self.id)
                    
                    # Reserve the vertex we arrived at
                    self.nav_graph.reserve_vertex(next_vertex, self.id)
                    
                    # Update current vertex
                    self.current_vertex = next_vertex
                    
                    # Check if we've reached the final destination
                    if self.current_path_index == len(self.path) - 1:
                        self.state = self.COMPLETED
                        status_update['state'] = self.state
                        status_update['event'] = 'reached_destination'
                    else:
                        # Prepare for next movement
                        self.state = self.IDLE
                        status_update['state'] = self.state
                        status_update['event'] = f'arrived_at_{next_vertex}'
                else:
                    # Move toward target
                    normalized_dir = direction / distance
                    movement = normalized_dir * self.move_speed
                    self.position = tuple(current_pos + movement)
            
            # If waiting, check if path is clear now
            elif self.state == self.WAITING:
                # Try again to reserve the next vertex and lane
                next_vertex = self.path[self.current_path_index + 1]
                
                can_reserve_lane = self.nav_graph.reserve_lane(
                    self.current_vertex, next_vertex, self.id)
                
                if can_reserve_lane:
                    # Release current vertex
                    self.nav_graph.release_vertex(self.current_vertex, self.id)
                    
                    # Start moving
                    self.state = self.MOVING
                    self.target_position = self.nav_graph.get_scaled_position(next_vertex)
                    
                    status_update['state'] = self.state
                    status_update['event'] = f'moving_to_{next_vertex}'
        
        return status_update
    
    def get_status_display(self):
        """
        Get a text representation of the robot's state for display.
        
        Returns:
            str: Status text
        """
        if self.state == self.IDLE:
            return f"Robot {self.id}: Idle"
        elif self.state == self.MOVING:
            return f"Robot {self.id}: Moving to vertex {self.path[self.current_path_index + 1]}"
        elif self.state == self.WAITING:
            return f"Robot {self.id}: Waiting to move to vertex {self.path[self.current_path_index + 1]}"
        elif self.state == self.CHARGING:
            return f"Robot {self.id}: Charging"
        elif self.state == self.COMPLETED:
            return f"Robot {self.id}: Task completed"
        
        return f"Robot {self.id}: Unknown state"
