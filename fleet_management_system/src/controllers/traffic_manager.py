class TrafficManager:
    """
    Manager for traffic negotiation and collision avoidance.
    This class works with the NavGraph and FleetManager to
    coordinate robot movements and prevent collisions.
    """
    
    def __init__(self, nav_graph, fleet_manager):
        """
        Initialize the traffic manager.
        
        Args:
            nav_graph (NavGraph): Reference to the navigation graph
            fleet_manager (FleetManager): Reference to the fleet manager
        """
        self.nav_graph = nav_graph
        self.fleet_manager = fleet_manager
        
        # Initialize collision tracking
        self.collision_warnings = []
        self.lane_usage = {}  # Track lane usage for each timestep in the future
    
    def check_path_conflicts(self, robot_id, path):
        """
        Check for conflicts along a planned path.
        
        Args:
            robot_id (int): ID of the robot planning the path
            path (list): List of vertex IDs forming the path
        
        Returns:
            list: List of conflict points (vertex IDs) along the path
        """
        conflicts = []
        
        # Check each segment of the path
        for i in range(len(path) - 1):
            from_vertex = path[i]
            to_vertex = path[i+1]
            
            # Check if lane is currently blocked
            for lane in self.nav_graph.lanes:
                if lane['from_vertex'] == from_vertex and lane['to_vertex'] == to_vertex:
                    if lane['occupying_robot'] is not None and lane['occupying_robot'] != robot_id:
                        conflicts.append(to_vertex)
                    break
            
            # Check if destination vertex is currently occupied
            if self.nav_graph.vertices[to_vertex]['occupying_robot'] is not None:
                conflicts.append(to_vertex)
        
        return conflicts
    
    def resolve_deadlocks(self):
        """
        Attempt to resolve deadlocks by prioritizing robots.
        This is a simple implementation that could be improved.
        
        Returns:
            int: Number of deadlocks resolved
        """
        resolved = 0
        waiting_robots = []
        
        # Find waiting robots
        for robot_id, robot in self.fleet_manager.robots.items():
            if robot.state == robot.WAITING:
                waiting_robots.append(robot_id)
        
        if not waiting_robots:
            return 0
        
        # Simple resolution strategy: randomly allow one robot to proceed
        if waiting_robots:
            # Choose a robot to prioritize (could be improved with more sophisticated algorithms)
            # For now, just choose the robot that has been waiting the longest
            # In a real implementation, you might consider factors like:
            # - Battery level
            # - Task priority
            # - Path length
            # - Time spent waiting
            prioritized_robot_id = waiting_robots[0]
            robot = self.fleet_manager.robots[prioritized_robot_id]
            
            if robot.path and robot.current_path_index < len(robot.path) - 1:
                next_vertex = robot.path[robot.current_path_index + 1]
                
                # Force reservation (temporarily clear obstacles)
                for lane in self.nav_graph.lanes:
                    if (lane['from_vertex'] == robot.current_vertex and 
                        lane['to_vertex'] == next_vertex):
                        if lane['occupying_robot'] is not None:
                            # Log the resolution
                            self.fleet_manager.log_event(
                                "traffic_manager", 
                                f"Resolving deadlock: Prioritizing robot {prioritized_robot_id} "
                                f"over robot {lane['occupying_robot']}"
                            )
                            
                            # Clear the lane (in a real system, you'd coordinate this better)
                            lane['occupying_robot'] = None
                            resolved += 1
        
        return resolved
    
    def update(self):
        """
        Update the traffic management system.
        
        Returns:
            dict: Status information about the traffic system
        """
        # Clear previous warnings
        self.collision_warnings = []
        
        # Check for and resolve deadlocks periodically
        deadlocks_resolved = self.resolve_deadlocks()
        
        # Return status information
        return {
            'collision_warnings': self.collision_warnings,
            'deadlocks_resolved': deadlocks_resolved
        }
    
    def get_lane_status(self, from_vertex, to_vertex):
        """
        Get the status of a lane.
        
        Args:
            from_vertex (int): Starting vertex ID
            to_vertex (int): Ending vertex ID
        
        Returns:
            dict: Lane status information
        """
        for lane in self.nav_graph.lanes:
            if lane['from_vertex'] == from_vertex and lane['to_vertex'] == to_vertex:
                occupying_robot = lane['occupying_robot']
                robot_info = None
                
                if occupying_robot is not None and occupying_robot in self.fleet_manager.robots:
                    robot = self.fleet_manager.robots[occupying_robot]
                    robot_info = {
                        'id': robot.id,
                        'state': robot.state
                    }
                
                return {
                    'from_vertex': from_vertex,
                    'to_vertex': to_vertex,
                    'is_blocked': lane['is_blocked'],
                    'occupying_robot': occupying_robot,
                    'robot_info': robot_info
                }
        
        return None
