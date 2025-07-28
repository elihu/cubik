"""
Utility functions and classes for the Rubik's Cube application.
"""

import logging
import sys

class CubeLogger:
    """Custom logger for the Rubik's Cube application."""
    
    def __init__(self, name="RubikCube", level=logging.INFO):
        """
        Initialize the logger.
        
        Args:
            name (str): Logger name
            level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.debug_enabled = False
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Create formatter without timestamp
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
        
        # Ensure handler level matches logger level
        for handler in self.logger.handlers:
            handler.setLevel(level)
    
    def toggle_debug(self):
        """Toggle debug mode on/off."""
        self.debug_enabled = not self.debug_enabled
        if self.debug_enabled:
            self.logger.setLevel(logging.DEBUG)
            # Also update the handler level
            for handler in self.logger.handlers:
                handler.setLevel(logging.DEBUG)
            self.info("🐛 Debug mode enabled")
        else:
            self.logger.setLevel(logging.INFO)
            # Also update the handler level
            for handler in self.logger.handlers:
                handler.setLevel(logging.INFO)
            self.info("🐛 Debug mode disabled")
    
    def debug(self, message):
        """Log debug message."""
        if self.debug_enabled:
            self.logger.debug(message)
    
    def info(self, message):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message):
        """Log critical message."""
        self.logger.critical(message)

# Global logger instance
logger = CubeLogger() 