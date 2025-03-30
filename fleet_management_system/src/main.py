import os
import sys
import time
import pygame
import argparse

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.nav_graph import NavGraph
from src.models.robot import Robot
from src.controllers.fleet_manager import FleetManager
from src.controllers.traffic_manager import TrafficManager
from src.gui.fleet_gui import FleetGUI

def main():
    """Main entry point for the Fleet Management System."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fleet Management System')
    parser.add_argument('--nav_graph', type=str, default='data/nav_graph_1.json',
                        help='Path to navigation graph JSON file')
    parser.add_argument('--log_file', type=str, default='src/logs/fleet_logs.txt',
                        help='Path to log file')
    parser.add_argument('--width', type=int, default=1200,
                        help='Window width')
    parser.add_argument('--height', type=int, default=600,
                        help='Window height')
    
    args = parser.parse_args()
    
    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(args.log_file), exist_ok=True)
    
    # Initialize components
    try:
        # Load navigation graph
        nav_graph = NavGraph(args.nav_graph)
        
        # Initialize fleet manager
        fleet_manager = FleetManager(nav_graph, args.log_file)
        
        # Initialize traffic manager
        traffic_manager = TrafficManager(nav_graph, fleet_manager)
        
        # Initialize GUI
        gui = FleetGUI(args.width, args.height, nav_graph, fleet_manager, traffic_manager)
        
        # Add startup messages
        gui.add_message("Fleet Management System initialized")
        gui.add_message("Press S for Spawn mode, A for Assign mode")
        gui.add_log("System started")
        gui.add_log(f"Loaded nav graph with {len(nav_graph.vertices)} vertices")
        
        # Main loop
        running = True
        last_time = time.time()
        
        while running:
            # Calculate delta time
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            # Handle events
            running = gui.handle_events()
            
            # Update components
            fleet_manager.update(delta_time)
            traffic_status = traffic_manager.update()
            gui.update(delta_time)
            
            # Log any traffic events
            if traffic_status['deadlocks_resolved'] > 0:
                gui.add_log(f"Resolved {traffic_status['deadlocks_resolved']} traffic deadlocks")
            
            # Render GUI
            gui.render()
            
            # Cap frame rate
            pygame.time.delay(16)  # ~60 FPS
        
        # Clean up
        pygame.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
