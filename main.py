"""
main.py

Main game loop for the 3D Rubik's Cube application.
Uses the RubiksCube and Renderer classes for clean separation of concerns.
"""

import sys
from rubiks_cube import RubiksCube
from renderer import Renderer
import config

def main():
    """Main game loop."""
    print("🎲 Starting Rubik's Cube 3D Application")
    print("=" * 50)
    
    # Initialize the cube
    try:
        cube = RubiksCube()
        cube.validate_parameters()
        print("✓ Rubik's Cube initialized")
    except Exception as e:
        print(f"❌ Failed to initialize cube: {e}")
        return 1
    
    # Initialize the renderer
    try:
        renderer = Renderer()
        renderer.initialize()
        print("✓ Renderer initialized")
    except Exception as e:
        print(f"❌ Failed to initialize renderer: {e}")
        return 1
    
    # Main game loop
    print("\n🎮 Starting game loop...")
    print("Controls:")
    print("  - Left mouse: Click and drag to rotate the cube")
    print("  - Right mouse: Click to select a face")
    print("  - R: Reset cube rotation")
    print("  - ESC: Quit")
    print("=" * 50)
    
    running = True
    try:
        while running:
            # Handle events
            running = renderer.handle_events()
            
            # Render frame
            renderer.render_frame(cube)
            
            # Limit frame rate
            renderer.tick(60)
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error in game loop: {e}")
        return 1
    finally:
        # Cleanup
        renderer.cleanup()
        print("\n✅ Application closed successfully")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())