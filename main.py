"""
Main entry point for the simplified Rubik's Cube application.
"""

import sys
from cube import Cube
from renderer import Renderer
from utils import logger

def main():
    """Main function."""
    logger.info("🎲 Starting Rubik's Cube")
    logger.info("=" * 50)
    
    # Initialize cube
    try:
        cube = Cube(size=3)
        logger.info("✓ Rubik's Cube initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize cube: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Initialize renderer
    try:
        renderer = Renderer()
        renderer.initialize()
        logger.info("Renderer initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize renderer: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Main game loop
    logger.info("🎮 Starting game loop...")
    logger.info("🎮 Controls:")
    logger.info("  - Left mouse: Click and drag to rotate the cube")
    logger.info("  - Right mouse: Click to select a face")
    logger.info("  - Left mouse + drag (with face selected): Rotate selected face")
    logger.info("  - R: Reset cube")
    logger.info("  - D: Toggle debug mode")
    logger.info("  - ESC: Quit")
    logger.info("=" * 50)
    
    running = True
    try:
        while running:
            running = renderer.handle_events(cube)
            renderer.render_frame(cube)
            renderer.tick(60)
    
    except KeyboardInterrupt:
        logger.warning("⚠️ Interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Error in game loop: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        renderer.cleanup()
        logger.info("✅ Application closed successfully")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 