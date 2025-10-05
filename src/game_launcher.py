"""
Main game launcher for NASA Farm Navigator.
"""

import os
import sys
import pygame
from game.core import Game

def main():
    """
    Main entry point for the game.
    """
    print("Launching NASA Farm Navigator...")
    
    # Initialize the game
    game = Game()
    
    # Set default selections
    game.active_tool = "plant"
    game.selected_crop = "corn"
    
    # Display welcome message and instructions
    print("Welcome to NASA Farm Navigator!")
    print("\nInstructions:")
    print("- Select tools with number keys (1-4) or buttons")
    print("- Select crops with C, W, T keys or buttons")
    print("- Click on farm tiles to interact with them")
    print("- Press SPACE to advance a day manually")
    print("- Press P to pause/unpause the game")
    print("- Press ESC to exit")
    
    # Run the game
    game.run()

if __name__ == "__main__":
    main()