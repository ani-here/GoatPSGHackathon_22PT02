import json
import networkx as nx
import numpy as np

class NavGraph:
    """Navigation graph representation for robot fleet management."""
    
    def __init__(self, json_file_path):
        """
        Initialize the navigation graph from a JSON file.
        
        Args:
            json_file_path (str): Path to the navigation graph JSON file
        """
        self.graph = nx.DiGraph()
        self.vertices = []
        self.lanes = []
        self.scale_factor = 50  # Scale factor for visualization
        self.offset_x = 300     # X offset for visualization
        self.offset_y = 300     # Y offset for visualization
        
        self.load_from_json(json_file_path)
        
    def load_from_json(self, json_file_path):
        """
        Load and parse the navigation graph from a JSON file.
        
        Args:
            json_file_path (str): Path to the navigation graph JSON file
        """
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            # Extract the level name (assuming there's only one level)
            level_name = list(data['levels'].keys())[0]
            level_data = data['levels'][level_name]
            
            # Parse vertices
            self.vertices = []
            for i, vertex_data in enumerate(level_data['vertices']):
                x, y, attrs = vertex_data
                
                # Default values if not specified
                name = attrs.get('name', f'v{i}')
                is_charger = attrs.get('is_charger', False)
                
                # Store vertex data
                vertex = {
                    'id': i,
                    'x': x,
                    'y': y,
                    'name': name,
                    'is_charger': is_charger,
                    'occupying_robot': None  # Track which robot is at this vertex
                }
                self.vertices.append(vertex)
                
                # Add vertex to the graph
                self.graph.add_node(i, **vertex)
            
            # Parse lanes
            self.lanes = []
            for lane_data in level_data['lanes']:
                from_vertex, to_vertex, attrs = lane_data
                
                # Default values if not specified
                speed_limit = attrs.get('speed_limit', 0)
                
                # Store lane data
                lane = {
                    'from_vertex': from_vertex,
                    'to_vertex': to_vertex,
                    'speed_limit': speed_limit,
                    'occupying_robot': None,  # Track which robot is on this lane
                    'is_blocked': False       # Flag for traffic management
                }
                self.lanes.append(lane)
                
                # Add edge to the graph
                self.graph.add_edge(from_vertex, to_vertex, **lane)
            
            # Calculate position bounds for visualization scaling
            self._calculate_bounds()
            
            print(f"Loaded navigation graph with {len(self.vertices)} vertices and {len(self.lanes)} lanes")
            
        except Exception as e:
            print(f"Error loading navigation graph: {e}")
            raise
    
    def _calculate_bounds(self):
        """Calculate bounds for visualization scaling."""
        if not self.vertices:
            return
        
        # Find min and max x, y coordinates
        x_coords = [v['x'] for v in self.vertices]
        y_coords = [v['y'] for v in self.vertices]
        
        self.min_x = min(x_coords)
        self.max_x = max(x_coords)
        self.min_y = min(y_coords)
        self.max_y = max(y_coords)
        
        # Add padding to ensure vertices aren't at the edge
        padding = 2.0
        width = (self.max_x - self.min_x) + padding
        height = (self.max_y - self.min_y) + padding
        
        # Calculate scale factor to fit in screen with margins
        screen_width = 800
        screen_height = 600
        
        # Adjust margins to leave space for UI elements
        margin_x = 100
        margin_y = 100
        
        if width > 0 and height > 0:
            self.scale_factor = min((screen_width - 2*margin_x) / width, 
                                    (screen_height - 2*margin_y) / height)
        
        # Center the graph in the available space
        self.offset_x = margin_x + (screen_width - 2*margin_x - width * self.scale_factor) / 2
        self.offset_y = margin_y + (screen_height - 2*margin_y - height * self.scale_factor) / 2
    def get_scaled_position(self, vertex_id):
        """
        Get the scaled position of a vertex for visualization.
        
        Args:
            vertex_id (int): Vertex ID
        
        Returns:
            tuple: (x, y) scaled position coordinates
        """
        vertex = self.vertices[vertex_id]
        x = (vertex['x'] - self.min_x) * self.scale_factor + self.offset_x
        y = (vertex['y'] - self.min_y) * self.scale_factor + self.offset_y
        return (int(x), int(y))
    
    def get_vertex_at_position(self, x, y, tolerance=15):
        """
        Get the vertex at the given screen position.
        
        Args:
            x (int): Screen X coordinate
            y (int): Screen Y coordinate
            tolerance (int): Click tolerance in pixels
        
        Returns:
            int or None: Vertex ID if found, None otherwise
        """
        for vertex in self.vertices:
            pos_x, pos_y = self.get_scaled_position(vertex['id'])
            distance = np.sqrt((pos_x - x)**2 + (pos_y - y)**2)
            if distance <= tolerance:
                return vertex['id']
        return None
    
    def get_shortest_path(self, start_vertex, end_vertex):
        """
        Get the shortest path between two vertices.
        
        Args:
            start_vertex (int): Starting vertex ID
            end_vertex (int): Destination vertex ID
        
        Returns:
            list: List of vertex IDs forming the path
        """
        try:
            path = nx.shortest_path(self.graph, start_vertex, end_vertex)
            return path
        except nx.NetworkXNoPath:
            return None
        
    def reserve_vertex(self, vertex_id, robot_id):
        """
        Try to reserve a vertex for a robot.
        
        Args:
            vertex_id (int): Vertex ID to reserve
            robot_id (int): Robot ID
        
        Returns:
            bool: True if reservation succeeded, False otherwise
        """
        if self.vertices[vertex_id]['occupying_robot'] is None:
            self.vertices[vertex_id]['occupying_robot'] = robot_id
            return True
        return False
    
    def release_vertex(self, vertex_id, robot_id):
        """
        Release a vertex reservation.
        
        Args:
            vertex_id (int): Vertex ID to release
            robot_id (int): Robot ID that was occupying the vertex
        """
        if self.vertices[vertex_id]['occupying_robot'] == robot_id:
            self.vertices[vertex_id]['occupying_robot'] = None
    
    def reserve_lane(self, from_vertex, to_vertex, robot_id):
        """
        Try to reserve a lane for a robot.
        
        Args:
            from_vertex (int): From vertex ID
            to_vertex (int): To vertex ID
            robot_id (int): Robot ID
        
        Returns:
            bool: True if reservation succeeded, False otherwise
        """
        for lane in self.lanes:
            if lane['from_vertex'] == from_vertex and lane['to_vertex'] == to_vertex:
                if lane['occupying_robot'] is None and not lane['is_blocked']:
                    lane['occupying_robot'] = robot_id
                    return True
                return False
        return False
    
    def release_lane(self, from_vertex, to_vertex, robot_id):
        """
        Release a lane reservation.
        
        Args:
            from_vertex (int): From vertex ID
            to_vertex (int): To vertex ID
            robot_id (int): Robot ID that was occupying the lane
        """
        for lane in self.lanes:
            if lane['from_vertex'] == from_vertex and lane['to_vertex'] == to_vertex:
                if lane['occupying_robot'] == robot_id:
                    lane['occupying_robot'] = None
