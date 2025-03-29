import time
import random
from ..models.robot import Robot

class FleetManager:
    """Manager for robot fleet operations and task assignment."""
    
    def __init__(self, nav_graph, log_file_path):
        """
        Initialize the fleet manager.
        
        Args:
            nav_graph (NavGraph): Reference to the navigation graph
            log_file_path (str): Path to the log file
        """
        self.nav_graph = nav_graph
        self.robots = {}
        self.next_robot_id = 0
        self.selected_robot = None
        self.log_file_path = log_file_path
        
        # Define a set of visually distinct colors for robots
        self.robot_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 128, 0),  # Orange
            (128, 0, 128),  # Purple
            (0, 128, 0),    # Dark Green
            (128, 128, 0),  # Olive
            (128, 0, 0),    # Maroon
            (0, 128, 128),  # Teal
        ]
        
        # Initialize logging
        self._init_logging()
    
    def _init_logging(self):
        """Initialize the log file."""
        try:
            with open(self.log_file_path, 'w') as f:
                f.write(f"=== Fleet Management System Log - {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
            self.log_event("system", "Fleet Management System initialized")
        except Exception as e:
            print(f"Error initializing log file: {e}")
    
    def log_event(self, source, message):
        """
        Log an event to the log file.
        
        Args:
            source (str): Source of the event (e.g., robot ID, system)
            message (str): Event message
        """
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file_path, 'a') as f:
                f.write(f"[{timestamp}] [{source}] {message}\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def spawn_robot(self, vertex_id):
        """
        Spawn a new robot at the specified vertex.
        
        Args:
            vertex_id (int): Vertex ID where the robot will spawn
        
        Returns:
            int or None: Robot ID if spawned successfully, None otherwise
        """
        # Check if vertex is occupied
        if self.nav_graph.vertices[vertex_id]['occupying_robot'] is not None:
            self.log_event("system", f"Cannot spawn robot at vertex {vertex_id}: Vertex occupied")
            return None
        
        # Assign a color from the predefined set
        color_index = self.next_robot_id % len(self.robot_colors)
        robot_color = self.robot_colors[color_index]
        
        # Create new robot
        robot = Robot(self.next_robot_id, vertex_id, self.nav_graph, robot_color)
        self.robots[self.next_robot_id] = robot
        
        # Log the event
        self.log_event(f"robot_{self.next_robot_id}", f"Spawned at vertex {vertex_id}")
        
        # Increment robot ID counter
        current_id = self.next_robot_id
        self.next_robot_id += 1
        
        return current_id
    
    def select_robot(self, x, y, tolerance=20):
        """
        Select a robot at the given screen position.
        
        Args:
            x (int): Screen X coordinate
            y (int): Screen Y coordinate
            tolerance (int): Click tolerance in pixels
        
        Returns:
            int or None: Selected robot ID if found, None otherwise
        """
        min_distance = tolerance
        selected = None
        
        for robot_id, robot in self.robots.items():
            rx, ry = robot.position
            distance = ((rx - x) ** 2 + (ry - y) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                selected = robot_id
        
        if selected is not None:
            self.selected_robot = selected
            self.log_event(f"robot_{selected}", "Selected for task assignment")
        
        return selected
    
    def assign_navigation_task(self, destination_vertex):
        """
        Assign a navigation task to the selected robot.
        
        Args:
            destination_vertex (int): Destination vertex ID
        
        Returns:
            bool: True if task was successfully assigned, False otherwise
        """
        if self.selected_robot is None or self.selected_robot not in self.robots:
            return False
        
        robot = self.robots[self.selected_robot]
        
        # Try to assign the task
        success = robot.assign_task(destination_vertex)
        
        if success:
            # Log the task assignment
            source_vertex = robot.current_vertex
            self.log_event(f"robot_{robot.id}", 
                          f"Assigned navigation task from vertex {source_vertex} to {destination_vertex}")
            return True
        else:
            self.log_event(f"robot_{robot.id}", 
                          f"Failed to assign navigation task to vertex {destination_vertex}")
            return False
    
    def update(self, delta_time):
        """
        Update all robots and handle events.
        
        Args:
            delta_time (float): Time elapsed since last update in seconds
        """
        for robot_id, robot in self.robots.items():
            status_update = robot.update(delta_time)
            
            # Log significant events
            if status_update['event']:
                self.log_event(f"robot_{robot_id}", 
                              f"State: {status_update['state']}, Event: {status_update['event']}")
    
    def get_all_robot_statuses(self):
        """
        Get status information for all robots.
        
        Returns:
            dict: Dictionary mapping robot IDs to status strings
        """
        return {robot_id: robot.get_status_display() for robot_id, robot in self.robots.items()}
