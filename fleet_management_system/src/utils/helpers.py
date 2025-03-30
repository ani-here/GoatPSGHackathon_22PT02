import math
import random
import networkx as nx
import time

def distance(pos1, pos2):
    """
    Calculate Euclidean distance between two points.
    
    Args:
        pos1 (tuple): First position (x, y)
        pos2 (tuple): Second position (x, y)
    
    Returns:
        float: Distance between the points
    """
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def lerp(a, b, t):
    """
    Linear interpolation between two values.
    
    Args:
        a (float): Starting value
        b (float): Ending value
        t (float): Interpolation factor (0.0 to 1.0)
    
    Returns:
        float: Interpolated value
    """
    return a + (b - a) * t

def lerp_pos(pos1, pos2, t):
    """
    Linear interpolation between two positions.
    
    Args:
        pos1 (tuple): Starting position (x, y)
        pos2 (tuple): Ending position (x, y)
        t (float): Interpolation factor (0.0 to 1.0)
    
    Returns:
        tuple: Interpolated position (x, y)
    """
    return (lerp(pos1[0], pos2[0], t), lerp(pos1[1], pos2[1], t))

def find_path_astar(graph, start, end):
    """
    Find a path using A* algorithm.
    
    Args:
        graph (nx.DiGraph): NetworkX graph
        start (int): Starting vertex ID
        end (int): Destination vertex ID
    
    Returns:
        list: List of vertex IDs forming the path, or None if no path exists
    """
    try:
        # Use NetworkX's A* implementation
        path = nx.astar_path(graph, start, end)
        return path
    except nx.NetworkXNoPath:
        return None

def find_path_avoiding_obstacles(graph, start, end, obstacles):
    """
    Find a path avoiding specified obstacles.
    
    Args:
        graph (nx.DiGraph): NetworkX graph
        start (int): Starting vertex ID
        end (int): Destination vertex ID
        obstacles (list): List of vertex IDs to avoid
    
    Returns:
        list: List of vertex IDs forming the path, or None if no path exists
    """
    # Create a copy of the graph
    temp_graph = graph.copy()
    
    # Remove obstacle vertices
    for vertex in obstacles:
        if temp_graph.has_node(vertex):
            temp_graph.remove_node(vertex)
    
    # Find path in modified graph
    try:
        path = nx.shortest_path(temp_graph, start, end)
        return path
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

def generate_unique_id(prefix=""):
    """
    Generate a unique ID based on timestamp and random number.
    
    Args:
        prefix (str): Prefix for the ID
    
    Returns:
        str: Unique ID
    """
    timestamp = int(time.time() * 1000)
    random_part = random.randint(1000, 9999)
    return f"{prefix}{timestamp}_{random_part}"

def format_time(seconds):
    """
    Format time in seconds to a human-readable string.
    
    Args:
        seconds (float): Time in seconds
    
    Returns:
        str: Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.0f}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"
