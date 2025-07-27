"""
Main entry point for the simplified Rubik's Cube application.
"""

import sys
from cube import Cube
from renderer import Renderer

def main():
    """Main function."""
    print("🎲 Starting Rubik's Cube")
    print("=" * 50)
    
    # Initialize cube
    try:
        cube = Cube(size=3)
        print("✓ Rubik's Cube initialized")
    except Exception as e:
        print(f"❌ Failed to initialize cube: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Initialize renderer
    try:
        renderer = Renderer()
        renderer.initialize()
        print("✓ Renderer initialized")
    except Exception as e:
        print(f"❌ Failed to initialize renderer: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Main game loop
    print("\n🎮 Starting game loop...")
    print("Controls:")
    print("  - Left mouse: Click and drag to rotate the cube")
    print("  - Right mouse: Click to select a face")
    print("  - Left mouse + drag (with face selected): Rotate selected face")
    print("  - R: Reset cube")
    print("  - ESC: Quit")
    print("=" * 50)
    
    running = True
    try:
        while running:
            running = renderer.handle_events(cube)
            renderer.render_frame(cube)
            renderer.tick(60)
    
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error in game loop: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        renderer.cleanup()
        print("\n✅ Application closed successfully")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 