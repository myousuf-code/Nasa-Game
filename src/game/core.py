"""
Core game module for the NASA Farm Navigator game.

This module contains the main Game class and game loop.
"""

import os
import sys
import pygame
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid GUI conflicts with pygame
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO

# Initialize pygame
pygame.init()

class Game:
    """
    Main Game class for NASA Farm Navigator.
    """
    
    def __init__(self, width=1280, height=800, title="NASA Farm Navigator", fullscreen=False):
        """
        Initialize the game.
        
        Args:
            width (int): Screen width
            height (int): Screen height
            title (str): Window title
            fullscreen (bool): Whether to run in fullscreen mode
        """
        self.title = title
        
        # Initialize the screen - use maximized window or set dimensions
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width, self.height = self.screen.get_size()
        else:
            self.width = width
            self.height = height
            # Create resizable window with title bar
            self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            
        pygame.display.set_caption(title)
        
        # Set up the clock
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.running = True
        self.paused = False
        
        # Farm state - adjust size based on screen resolution
        farm_size = min(30, max(10, int(self.width / 40)))  # Dynamic farm size
        self.farm = Farm(farm_size, farm_size)  # Create farm grid sized to screen
        
        # Game time (start with current date)
        self.current_date = datetime.now()
        self.day_length = 10  # seconds per in-game day
        self.last_day_update = pygame.time.get_ticks()
        
        # UI state
        self.active_tool = None
        self.selected_crop = None
        
        # Economic system
        self.money = 1000.0  # Starting money
        self.total_earned = 0.0
        self.total_spent = 0.0
        
        # Weather alerts system
        self.weather_alerts = []
        self.previous_alerts = []
        
        # Money transaction tracking for visual feedback
        self.recent_transactions = []  # List of (amount, timestamp, type)
        self.transaction_display_time = 2.0  # Show transactions for 2 seconds
        
        # NASA data integration
        self.location = {"lat": 36.7783, "lon": -119.4179}  # Default location (Central Valley, California)
        self.weather_data = {
            "temperature": 20.0,
            "temperature_min": 15.0,
            "temperature_max": 25.0,
            "precipitation": 0.0,
            "humidity": 65.0,
            "wind_speed": 3.0,
            "is_placeholder": True
        }
        self.weather_forecast = None
        self.show_weather_panel = False  # Start with weather panel hidden
        self.show_stats_panel = True     # Start with statistics panel shown
        
        # NASA data loading state
        self.nasa_data_loading = True
        self.nasa_loading_start_time = pygame.time.get_ticks()
        self.nasa_loading_dots = 0
        self.nasa_loading_message = "Connecting to NASA POWER API..."
        self.nasa_data_loaded = False
        
        # Scrolling system
        self.scroll_x = 0  # Horizontal scroll offset
        self.scroll_y = 0  # Vertical scroll offset
        self.scroll_speed = 20  # Pixels to scroll per step
        
        # Import data processor
        sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
        try:
            from data_processing import data_processor
            self.data_processor = data_processor.GameDataProcessor()
        except ImportError:
            print("Warning: Could not import data processor. Using placeholder data.")
            self.data_processor = None
        
        # Load assets
        self.assets = self._load_assets()
        
    def _load_assets(self):
        """Load game assets like images and sounds."""
        assets = {
            'images': {},
            'fonts': {},
            'sounds': {}
        }
        
        # Load default font
        assets['fonts']['default'] = pygame.font.SysFont(None, 24)
        
        # TODO: Load actual game assets
        # For now, create some placeholder graphics
        
        # Create enhanced soil textures with varied browns and natural patterns
        soil = pygame.Surface((32, 32))
        
        # Create a varied soil base with different shades of brown
        base_colors = [
            (139, 69, 19),   # Saddle brown
            (160, 82, 45),   # Dark brown
            (210, 180, 140), # Tan
            (205, 133, 63),  # Peru brown
            (139, 118, 76)   # Dark olive brown
        ]
        
        # Fill with random soil colors for natural variation
        for x in range(32):
            for y in range(32):
                # Create soil variation using noise-like pattern
                color_choice = ((x + y) * 7 + x * 3 + y * 5) % len(base_colors)
                base_color = base_colors[color_choice]
                
                # Add slight random variation to each pixel
                variation = (x * y) % 20 - 10  # -10 to +10 variation
                varied_color = (
                    max(0, min(255, base_color[0] + variation)),
                    max(0, min(255, base_color[1] + variation)),
                    max(0, min(255, base_color[2] + variation))
                )
                soil.set_at((x, y), varied_color)
        
        # Add subtle furrow lines to simulate tilled soil
        for i in range(0, 32, 4):
            pygame.draw.line(soil, (120, 60, 15), (0, i), (32, i), 1)  # Dark furrow lines
            if i + 1 < 32:
                pygame.draw.line(soil, (180, 120, 80), (0, i + 1), (32, i + 1), 1)  # Lighter ridge lines
        
        # Add small rocks and debris for realism
        for i in range(8):  # Add 8 small details
            x, y = (i * 4 + 2) % 32, (i * 3 + 3) % 32
            pygame.draw.circle(soil, (101, 67, 33), (x, y), 1)  # Small dark spots (rocks)
        
        assets['images']['soil'] = soil
        
        # Create enhanced crop textures for different crop types
        
        # Enhanced Corn texture with more detail
        corn = pygame.Surface((32, 32))
        corn.fill((0, 0, 0, 0))  # Transparent background
        corn = corn.convert_alpha()
        
        # Draw corn stalk with gradient
        for height in range(32, 8, -1):
            stalk_width = max(1, 4 - (32 - height) // 6)
            stalk_color = (0, 120 + (32 - height) * 2, 0)  # Gradient from dark to light green
            pygame.draw.circle(corn, stalk_color, (16, height), stalk_width // 2)
        
        # Draw corn leaves
        for i in range(3):
            leaf_y = 25 - i * 6
            # Left leaf
            pygame.draw.ellipse(corn, (34, 139, 34), (8, leaf_y - 2, 8, 12))
            # Right leaf  
            pygame.draw.ellipse(corn, (34, 139, 34), (16, leaf_y - 2, 8, 12))
        
        # Draw corn cobs
        for i in range(2):
            cob_y = 8 + i * 3
            pygame.draw.ellipse(corn, (255, 215, 0), (12 + i * 4, cob_y, 6, 14))  # Golden corn
            # Add corn kernel texture
            for row in range(7):
                for col in range(2):
                    kernel_x = 13 + i * 4 + col * 2
                    kernel_y = cob_y + 2 + row * 2
                    pygame.draw.circle(corn, (255, 235, 59), (kernel_x, kernel_y), 1)
        
        assets['images']['corn'] = corn
        
        # Enhanced Wheat texture with more realistic appearance
        wheat = pygame.Surface((32, 32))
        wheat.fill((0, 0, 0, 0))  # Transparent background
        wheat = wheat.convert_alpha()
        
        # Draw wheat field background
        pygame.draw.rect(wheat, (154, 205, 50), (0, 20, 32, 12))  # Light green base
        
        # Draw individual wheat stalks with more detail
        stalk_positions = [4, 8, 12, 16, 20, 24, 28]
        for i, x_pos in enumerate(stalk_positions):
            stalk_height = 22 + (i % 3) * 2  # Varying heights
            # Draw stalk
            pygame.draw.line(wheat, (218, 165, 32), (x_pos, 30), (x_pos, stalk_height), 2)
            
            # Draw wheat head
            head_color = (245, 222, 179) if i % 2 == 0 else (255, 228, 181)
            pygame.draw.ellipse(wheat, head_color, (x_pos - 2, stalk_height - 8, 4, 10))
            
            # Add wheat grain details
            for grain in range(4):
                grain_y = stalk_height - 6 + grain * 2
                pygame.draw.circle(wheat, (240, 230, 140), (x_pos, grain_y), 1)
        
        # Add wheat awns (the bristles)
        for i, x_pos in enumerate(stalk_positions):
            awn_start_y = 22 + (i % 3) * 2 - 8
            for awn in range(3):
                awn_x = x_pos + awn - 1
                pygame.draw.line(wheat, (210, 180, 140), (awn_x, awn_start_y), (awn_x - 1, awn_start_y - 6), 1)
        
        assets['images']['wheat'] = wheat
        
        # Enhanced Tomato texture with plant structure
        tomato = pygame.Surface((32, 32))
        tomato.fill((0, 0, 0, 0))  # Transparent background
        tomato = tomato.convert_alpha()
        
        # Draw tomato plant base and stem
        pygame.draw.rect(tomato, (34, 139, 34), (14, 20, 4, 12))  # Main stem
        
        # Draw tomato plant leaves with more detail
        leaf_positions = [(8, 18), (20, 16), (6, 22), (22, 24)]
        for leaf_x, leaf_y in leaf_positions:
            # Draw leaf shape
            pygame.draw.ellipse(tomato, (0, 128, 0), (leaf_x, leaf_y, 8, 6))
            # Add leaf veins
            pygame.draw.line(tomato, (0, 100, 0), (leaf_x + 1, leaf_y + 3), (leaf_x + 7, leaf_y + 3), 1)
            pygame.draw.line(tomato, (0, 100, 0), (leaf_x + 4, leaf_y + 1), (leaf_x + 4, leaf_y + 5), 1)
        
        # Draw tomatoes with shading
        tomato_positions = [(12, 8), (18, 12), (14, 16)]
        for i, (tom_x, tom_y) in enumerate(tomato_positions):
            size = 6 - i  # Varying sizes
            # Main tomato body
            pygame.draw.circle(tomato, (255, 69, 0), (tom_x, tom_y), size)
            # Highlight for 3D effect
            pygame.draw.circle(tomato, (255, 99, 71), (tom_x - 1, tom_y - 1), size // 2)
            # Tomato top (calyx)
            pygame.draw.circle(tomato, (34, 139, 34), (tom_x, tom_y - size), 2)
            # Small star pattern on top
            for angle in range(0, 360, 72):  # 5-pointed star
                import math
                end_x = tom_x + int(math.cos(math.radians(angle)) * 2)
                end_y = tom_y - size + int(math.sin(math.radians(angle)) * 2)
                pygame.draw.line(tomato, (0, 100, 0), (tom_x, tom_y - size), (end_x, end_y), 1)
        
        assets['images']['tomato'] = tomato
        
        # Create an enhanced default crop texture (fallback)
        crop = pygame.Surface((32, 32))
        crop.fill((0, 0, 0, 0))  # Transparent background
        crop = crop.convert_alpha()
        
        # Draw a generic plant with stem and leaves
        pygame.draw.line(crop, (34, 139, 34), (16, 30), (16, 10), 3)  # Main stem
        
        # Add leaves at different levels
        leaf_levels = [12, 16, 20, 24]
        for i, leaf_y in enumerate(leaf_levels):
            # Alternate leaf sides
            if i % 2 == 0:
                # Left leaf
                pygame.draw.ellipse(crop, (0, 128, 0), (8, leaf_y, 10, 6))
            else:
                # Right leaf
                pygame.draw.ellipse(crop, (0, 128, 0), (16, leaf_y, 10, 6))
        
        # Add a flower or fruit at the top
        pygame.draw.circle(crop, (255, 255, 100), (16, 8), 4)  # Yellow flower
        # Add small petals
        petal_positions = [(12, 8), (20, 8), (16, 4), (16, 12)]
        for petal_x, petal_y in petal_positions:
            pygame.draw.circle(crop, (255, 255, 255), (petal_x, petal_y), 2)
        
        assets['images']['crop'] = crop
        
        # Create a simple water texture
        water = pygame.Surface((32, 32))
        water.fill((0, 0, 255))  # Blue color
        assets['images']['water'] = water
        
        return assets
        
    def run(self):
        """Run the main game loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(self.fps)
            
        pygame.quit()
        
    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.width = event.w
                self.height = event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                print(f"Window resized to {self.width}x{self.height}")
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_SPACE:
                    # Advance one day when space is pressed
                    self.advance_day()
                
                # Tool selection shortcuts
                elif event.key == pygame.K_1:
                    self.active_tool = "plant"
                    print("Selected tool: plant")
                elif event.key == pygame.K_2:
                    self.active_tool = "water"
                    print("Selected tool: water")
                elif event.key == pygame.K_3:
                    self.active_tool = "fertilize"
                    print("Selected tool: fertilize")
                elif event.key == pygame.K_4:
                    self.active_tool = "harvest"
                    print("Selected tool: harvest")
                elif event.key == pygame.K_5:
                    self.active_tool = "treat"
                    print("Selected tool: treat")
                elif event.key == pygame.K_6:
                    self.active_tool = "protect"
                    print("Selected tool: protect")
                
                # Crop selection shortcuts
                elif event.key == pygame.K_c:
                    self.selected_crop = "corn"
                    print("Selected crop: corn")
                elif event.key == pygame.K_w:
                    self.selected_crop = "wheat"
                    print("Selected crop: wheat")
                elif event.key == pygame.K_t:
                    self.selected_crop = "tomato"
                    print("Selected crop: tomato")
                elif event.key == pygame.K_f:
                    # Toggle weather panel (turn off stats panel when weather panel is on)
                    self.show_weather_panel = not self.show_weather_panel
                    if self.show_weather_panel:
                        self.show_stats_panel = False
                    print(f"Weather panel: {'shown' if self.show_weather_panel else 'hidden'}")
                elif event.key == pygame.K_s:
                    # Toggle stats panel (turn off weather panel when stats panel is on)
                    self.show_stats_panel = not self.show_stats_panel
                    if self.show_stats_panel:
                        self.show_weather_panel = False
                    print(f"Stats panel: {'shown' if self.show_stats_panel else 'hidden'}")
                
                # Scrolling controls
                elif event.key == pygame.K_LEFT:
                    self.scroll_x = max(0, self.scroll_x - self.scroll_speed)
                elif event.key == pygame.K_RIGHT:
                    self.scroll_x = min(self._get_max_scroll_x(), self.scroll_x + self.scroll_speed)
                elif event.key == pygame.K_UP:
                    self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                elif event.key == pygame.K_DOWN:
                    self.scroll_y = min(self._get_max_scroll_y(), self.scroll_y + self.scroll_speed)
                    
            elif event.type == pygame.MOUSEWHEEL:
                # Mouse wheel scrolling (vertical)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    # Horizontal scroll with Shift + wheel
                    scroll_delta = event.y * self.scroll_speed
                    self.scroll_x = max(0, min(self._get_max_scroll_x(), self.scroll_x - scroll_delta))
                else:
                    # Vertical scroll
                    scroll_delta = event.y * self.scroll_speed
                    self.scroll_y = max(0, min(self._get_max_scroll_y(), self.scroll_y - scroll_delta))
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse clicks
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicking in the farm grid
                grid_x, grid_y = self._screen_to_grid(mouse_pos)
                if grid_x >= 0 and grid_x < self.farm.width and grid_y >= 0 and grid_y < self.farm.height:
                    # Handle farm interaction based on active tool
                    if self.active_tool == "plant" and self.selected_crop:
                        cost = self._get_planting_cost(self.selected_crop)
                        if self.money >= cost:
                            success = self.farm.plant_crop(grid_x, grid_y, self.selected_crop)
                            if success:
                                self.money -= cost
                                self.total_spent += cost
                                self._add_transaction(cost, 'expense')
                                print(f"Planted {self.selected_crop} for ${cost:.2f}")
                            else:
                                print("Cannot plant here")
                        else:
                            print(f"Not enough money! Need ${cost:.2f}, have ${self.money:.2f}")
                            
                    elif self.active_tool == "water":
                        cost = 2.0  # Cost per watering
                        if self.money >= cost:
                            success = self.farm.water_tile(grid_x, grid_y)
                            if success:
                                self.money -= cost
                                self.total_spent += cost
                                self._add_transaction(cost, 'expense')
                                print(f"Watered tile for ${cost:.2f}")
                            else:
                                print("Cannot water this tile")
                        else:
                            print(f"Not enough money! Need ${cost:.2f}, have ${self.money:.2f}")
                            
                    elif self.active_tool == "fertilize":
                        cost = 5.0  # Cost per fertilizing
                        if self.money >= cost:
                            success = self.farm.fertilize_tile(grid_x, grid_y)
                            if success:
                                self.money -= cost
                                self.total_spent += cost
                                self._add_transaction(cost, 'expense')
                                print(f"Fertilized tile for ${cost:.2f}")
                            else:
                                print("Cannot fertilize this tile")
                        else:
                            print(f"Not enough money! Need ${cost:.2f}, have ${self.money:.2f}")
                            
                    elif self.active_tool == "harvest":
                        yield_amount = self.farm.harvest_crop(grid_x, grid_y)
                        if yield_amount > 0:
                            # Calculate earnings based on crop type and yield
                            tile = self.farm.get_tile(grid_x, grid_y)
                            if hasattr(tile, 'harvested_crop_type'):
                                earnings = self._calculate_earnings(tile.harvested_crop_type, yield_amount)
                                self.money += earnings
                                self.total_earned += earnings
                                print(f"Harvested with yield: {yield_amount:.2f}, earned: ${earnings:.2f}")
                            else:
                                earnings = yield_amount * 10  # Default price
                                self.money += earnings
                                self.total_earned += earnings
                                self._add_transaction(earnings, 'income')
                                print(f"Harvested with yield: {yield_amount:.2f}, earned: ${earnings:.2f}")
                                
                    elif self.active_tool == "treat":
                        cost = 15.0  # Cost per treatment
                        if self.money >= cost:
                            success = self.farm.treat_tile(grid_x, grid_y)
                            if success:
                                self.money -= cost
                                self.total_spent += cost
                                self._add_transaction(cost, 'expense')
                                print(f"Applied treatment for ${cost:.2f}")
                            else:
                                print("No crop to treat at this location")
                        else:
                            print(f"Not enough money! Need ${cost:.2f}, have ${self.money:.2f}")
                            
                    elif self.active_tool == "protect":
                        cost = 25.0  # Cost per weather protection
                        if self.money >= cost:
                            success = self.farm.protect_tile(grid_x, grid_y)
                            if success:
                                self.money -= cost
                                self.total_spent += cost
                                self._add_transaction(cost, 'expense')
                                print(f"Applied weather protection for ${cost:.2f}")
                            else:
                                print("No crop to protect at this location")
                        else:
                            print(f"Not enough money! Need ${cost:.2f}, have ${self.money:.2f}")
                    
                    # If no tool is selected, show tile information
                    if not self.active_tool:
                        tile = self.farm.get_tile(grid_x, grid_y)
                        print(f"\nTile ({grid_x}, {grid_y}):")
                        print(f"Water: {tile.water_level:.1f}/{tile.max_water:.1f}")
                        print(f"Nutrients: {tile.nutrient_level:.1f}/{tile.max_nutrients:.1f}")
                        if tile.crop:
                            print(f"Crop: {tile.crop.type}")
                            print(f"Growth: {tile.crop.growth_stage*100:.1f}%")
                            print(f"Health: {tile.crop.health*100:.1f}%")
                            print(f"Days planted: {tile.crop.days_since_planted}")
                            
                            # Weather stress information
                            weather_stress = tile.crop.get_weather_stress_level()
                            if weather_stress > 0.05:
                                stress_type = tile.crop.get_dominant_weather_stress()
                                print(f"Weather stress: {stress_type} ({weather_stress*100:.1f}%)")
                                if tile.crop.frost_damage > 0.1:
                                    print(f"  Frost damage: {tile.crop.frost_damage*100:.1f}%")
                                if tile.crop.heat_stress > 0.1:
                                    print(f"  Heat stress: {tile.crop.heat_stress*100:.1f}%")
                                if tile.crop.drought_stress > 0.1:
                                    print(f"  Drought stress: {tile.crop.drought_stress*100:.1f}%")
                                if tile.crop.flood_damage > 0.1:
                                    print(f"  Flood damage: {tile.crop.flood_damage*100:.1f}%")
                                    
                            if tile.crop.weather_protection:
                                print("🛡️ Weather protection active")
                            
                            # Disease and pest information
                            if tile.crop.disease_status:
                                print(f"Disease: {tile.crop.disease_status} (severity: {tile.crop.disease_severity*100:.1f}%)")
                                print(f"Infected for {tile.crop.days_infected} days")
                            if tile.crop.pest_status:
                                print(f"Pests: {tile.crop.pest_status} (severity: {tile.crop.pest_severity*100:.1f}%)")
                                print(f"Infested for {tile.crop.days_infested} days")
                            if tile.crop.treatment_applied:
                                print("Treatment applied - recovering...")
                            
                            # Check if crop is in danger
                            if tile.crop.is_severely_damaged():
                                print("⚠️ CROP IS SEVERELY DAMAGED! Consider removing it.")
                                
                        else:
                            print("No crop planted")
                
    def _screen_to_grid(self, screen_pos):
        """
        Convert screen coordinates to farm grid coordinates.
        
        Args:
            screen_pos (tuple): (x, y) screen position
            
        Returns:
            tuple: (grid_x, grid_y) farm grid coordinates
        """
        # Use the farm rendering info calculated in _draw_farm
        if hasattr(self, 'farm_render_info'):
            cell_size = self.farm_render_info['cell_size']
            farm_start_x = self.farm_render_info['start_x']
            farm_start_y = self.farm_render_info['start_y']
            
            # Calculate grid coordinates from screen position (accounting for scroll)
            grid_x = (screen_pos[0] - farm_start_x + self.scroll_x) // cell_size
            grid_y = (screen_pos[1] - farm_start_y + self.scroll_y) // cell_size
            
            return grid_x, grid_y
        else:
            # Fallback if farm_render_info isn't available yet
            return -1, -1
    
    def _get_max_scroll_x(self):
        """Calculate maximum horizontal scroll distance."""
        if hasattr(self, 'farm_render_info'):
            total_farm_width = self.farm.width * self.farm_render_info['cell_size']
            visible_width = self.farm_render_info['farm_area_width']
            return max(0, total_farm_width - visible_width)
        return 0
    
    def _get_max_scroll_y(self):
        """Calculate maximum vertical scroll distance.""" 
        if hasattr(self, 'farm_render_info'):
            total_farm_height = self.farm.height * self.farm_render_info['cell_size']
            visible_height = self.farm_render_info['farm_area_height']
            return max(0, total_farm_height - visible_height)
        return 0
            
    def _get_planting_cost(self, crop_type):
        """Get the cost of planting a specific crop type."""
        costs = {
            "corn": 8.0,
            "wheat": 6.0,
            "tomato": 12.0
        }
        return costs.get(crop_type, 8.0)
        
    def _calculate_earnings(self, crop_type, yield_amount):
        """Calculate earnings from harvesting a crop."""
        # Base prices per unit yield
        prices = {
            "corn": 12.0,
            "wheat": 10.0,
            "tomato": 15.0
        }
        base_price = prices.get(crop_type, 10.0)
        return yield_amount * base_price
        
    def _update(self):
        """Update game state."""
        if self.paused:
            return
            
        # Update game time
        current_time = pygame.time.get_ticks()
        if current_time - self.last_day_update > self.day_length * 1000:
            self.advance_day()
            self.last_day_update = current_time
            
        # Update farm (pass weather data for crop stress calculations)
        self.farm.update(self.current_date, self.weather_data)
        
    def advance_day(self):
        """Advance the game by one day."""
        self.current_date += timedelta(days=1)
        print(f"Day advanced to: {self.current_date.strftime('%Y-%m-%d')}")
        
        # Update weather data based on NASA data
        self._update_weather_data()
        
        # Check for weather alerts
        self._check_weather_alerts()
        
    def _add_transaction(self, amount, transaction_type):
        """Add a transaction to the recent transactions list for visual feedback."""
        import time
        self.recent_transactions.append({
            'amount': amount,
            'type': transaction_type,  # 'income' or 'expense'
            'timestamp': time.time()
        })
        
        # Keep only recent transactions (last 5 seconds)
        current_time = time.time()
        self.recent_transactions = [
            t for t in self.recent_transactions 
            if current_time - t['timestamp'] < 5.0
        ]
        
    def _update_weather_data(self):
        """Update weather data using NASA data sources."""
        if self.data_processor:
            try:
                # Update loading message if still loading
                if self.nasa_data_loading:
                    current_time = pygame.time.get_ticks()
                    # Update loading dots animation
                    if current_time - self.nasa_loading_start_time > 500:  # Change every 500ms
                        self.nasa_loading_dots = (self.nasa_loading_dots + 1) % 4
                        self.nasa_loading_start_time = current_time
                
                # Get weather data from NASA POWER API through our data processor
                date_str = self.current_date.strftime("%Y-%m-%d")
                
                # Update loading message
                if self.nasa_data_loading:
                    self.nasa_loading_message = "Fetching NASA climate data..."
                
                weather = self.data_processor.get_daily_weather(
                    self.location["lat"],
                    self.location["lon"],
                    date_str
                )
                self.weather_data = weather
                
                # Mark NASA data as loaded successfully
                if self.nasa_data_loading and not weather.get("is_placeholder", False):
                    self.nasa_data_loading = False
                    self.nasa_data_loaded = True
                    print("NASA data loaded successfully!")
                
                # Update weather forecast every 7 days
                if not self.weather_forecast or self.current_date.day % 7 == 1:
                    if self.nasa_data_loading:
                        self.nasa_loading_message = "Generating weather forecast..."
                    self._update_weather_forecast()
                    
                # Weather events affect farm conditions
                self._apply_weather_effects()
                    
            except Exception as e:
                # Only print error once per session to avoid spam
                if not hasattr(self, '_weather_error_shown'):
                    print(f"NASA Weather API unavailable. Using simulated weather data.")
                    self._weather_error_shown = True
                
                # Mark loading as failed, switch to simulated data
                if self.nasa_data_loading:
                    self.nasa_data_loading = False
                    self.nasa_loading_message = "Using simulated weather data"
                
                # Fall back to simple weather model if API call fails
                self._generate_simulated_weather()
        else:
            # Use simulated weather if data processor is not available
            if self.nasa_data_loading:
                self.nasa_data_loading = False
                self.nasa_loading_message = "Using simulated weather data"
            self._generate_simulated_weather()
    
    def _update_weather_forecast(self):
        """Update the seasonal forecast data."""
        if self.data_processor:
            try:
                date_str = self.current_date.strftime("%Y-%m-%d")
                self.weather_forecast = self.data_processor.create_seasonal_forecast(
                    self.location["lat"],
                    self.location["lon"],
                    date_str,
                    days=30
                )
                
                # Generate forecast image
                self._generate_forecast_image()
                
            except Exception as e:
                # Only print forecast error once per session to avoid spam
                if not hasattr(self, '_forecast_error_shown'):
                    print("NASA Forecast API unavailable. Using simulated forecast data.")
                    self._forecast_error_shown = True
                self._create_simulated_forecast()
    
    def _check_weather_alerts(self):
        """Check for dangerous weather conditions and notify player."""
        alerts = []
        
        # Check current weather conditions
        temp = self.weather_data.get("temperature", 20)
        precipitation = self.weather_data.get("precipitation", 0)
        wind_speed = self.weather_data.get("wind_speed", 0)
        humidity = self.weather_data.get("humidity", 50)
        
        # Temperature alerts
        if temp <= -5:
            alerts.append("⚠️ FROST WARNING: Extreme cold may damage unprotected crops!")
        elif temp <= 0:
            alerts.append("🥶 Frost Alert: Cold temperatures detected. Consider protection.")
        elif temp >= 40:
            alerts.append("🔥 HEAT WARNING: Extreme heat stress on crops!")
        elif temp >= 35:
            alerts.append("☀️ Heat Alert: High temperatures may stress crops.")
        
        # Precipitation alerts
        if precipitation >= 50:
            alerts.append("🌊 FLOOD WARNING: Heavy rainfall may waterlog crops!")
        elif precipitation >= 25:
            alerts.append("🌧️ Heavy Rain Alert: High precipitation detected.")
        elif precipitation <= 1 and humidity < 30:
            alerts.append("🏜️ DROUGHT WARNING: Very low moisture conditions!")
        elif precipitation <= 5 and humidity < 40:
            alerts.append("☀️ Dry Conditions: Low moisture may stress crops.")
        
        # Wind alerts
        if wind_speed >= 15:
            alerts.append("💨 WIND WARNING: Strong winds may damage crops!")
        elif wind_speed >= 10:
            alerts.append("🌪️ Wind Alert: Moderate winds detected.")
        
        # Check forecast for upcoming severe weather
        if hasattr(self, 'weather_forecast') and self.weather_forecast is not None:
            try:
                # Handle DataFrame forecast data
                if hasattr(self.weather_forecast, 'get'):
                    # If it's a dictionary-like object
                    temp_data = self.weather_forecast.get('temperature', [])
                    precip_data = self.weather_forecast.get('precipitation', [])
                    
                    for i in range(min(3, len(temp_data))):  # Next 3 days
                        temp_forecast = temp_data[i] if i < len(temp_data) else 20
                        precip_forecast = precip_data[i] if i < len(precip_data) else 0
                        
                        if temp_forecast <= -5 or temp_forecast >= 40:
                            alerts.append(f"📅 Day {i+1}: Extreme weather forecast!")
                        elif precip_forecast >= 40:
                            alerts.append(f"📅 Day {i+1}: Heavy rain forecast!")
                elif hasattr(self.weather_forecast, 'iloc'):
                    # If it's a DataFrame
                    try:
                        for i in range(min(3, len(self.weather_forecast))):
                            row = self.weather_forecast.iloc[i]
                            temp_forecast = row.get('temperature', 20)
                            precip_forecast = row.get('precipitation', 0)
                            
                            if temp_forecast <= -5 or temp_forecast >= 40:
                                alerts.append(f"📅 Day {i+1}: Extreme weather forecast!")
                            elif precip_forecast >= 40:
                                alerts.append(f"📅 Day {i+1}: Heavy rain forecast!")
                    except (IndexError, KeyError):
                        pass  # Skip forecast alerts if data format is unexpected
            except Exception as e:
                print(f"Error processing weather forecast for alerts: {e}")
                # Skip forecast alerts if there's an error
        
        # Store alerts for display
        self.weather_alerts = alerts
        
        # Print new alerts to console
        for alert in alerts:
            if alert not in getattr(self, 'previous_alerts', []):
                print(f"Weather Alert: {alert}")
        
        self.previous_alerts = alerts.copy()
    
    def _create_simulated_forecast(self):
        """Create simulated weather forecast when NASA data is unavailable."""
        # Start with the current date
        start = self.current_date
        
        # Generate date range
        days = 30
        date_range = [start + timedelta(days=i) for i in range(days)]
        dates = [d.strftime("%Y-%m-%d") for d in date_range]
        
        # Base temperature and precipitation by season
        base_temp = 20  # Base temperature in Celsius
        amplitude = 8   # Annual temperature variation amplitude
        
        # Calculate day of year and simulate seasonal variation
        doy_values = [(start + timedelta(days=i)).timetuple().tm_yday for i in range(days)]
        seasonal_factor = [amplitude * np.sin(2 * np.pi * (doy - 80) / 365) for doy in doy_values]
        
        # Generate temperatures with seasonal trend and random variations
        temps = [base_temp + sf + np.random.normal(0, 2) for sf in seasonal_factor]
        temp_min = [t - np.random.uniform(3, 8) for t in temps]
        temp_max = [t + np.random.uniform(3, 8) for t in temps]
        
        # Generate precipitation (more likely in certain seasons)
        precip_prob = [0.3 + 0.2 * np.sin(2 * np.pi * (doy - 100) / 365) for doy in doy_values]
        precipitation = [np.random.exponential(5) if np.random.random() < p else 0 for p in precip_prob]
        
        # Create DataFrame
        self.weather_forecast = pd.DataFrame({
            'date': dates,
            'temperature': temps,
            'temperature_min': temp_min,
            'temperature_max': temp_max,
            'precipitation': precipitation
        })
        
        # Generate the forecast image
        self._generate_forecast_image()
        
        print("Simulated forecast data created successfully")

    def _generate_simulated_weather(self):
        """Generate simulated weather when NASA data is unavailable."""
        # Base temperature by season (assuming northern hemisphere)
        month = self.current_date.month
        day_of_year = self.current_date.timetuple().tm_yday
        
        # Seasonal base temperature (sine wave over the year)
        base_temp = 20 + 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Random daily variation
        daily_variation = np.random.normal(0, 3)
        
        # Calculate temperature
        temp = base_temp + daily_variation
        temp_min = temp - np.random.uniform(3, 8)
        temp_max = temp + np.random.uniform(3, 8)
        
        # Calculate precipitation (more in spring/fall, less in summer/winter)
        precip_chance = 0.3 + 0.2 * np.sin(2 * np.pi * (day_of_year - 100) / 365)
        precipitation = np.random.exponential(5) if np.random.random() < precip_chance else 0
        
        # Calculate humidity (related to precipitation and temperature)
        humidity = 50 + 30 * precip_chance + np.random.normal(0, 10)
        humidity = max(10, min(100, humidity))
        
        # Calculate wind speed
        wind_speed = np.random.gamma(2, 1.5)
        
        # Update weather data
        self.weather_data = {
            "temperature": temp,
            "temperature_min": temp_min,
            "temperature_max": temp_max,
            "precipitation": precipitation,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "is_placeholder": True
        }
    
    def _apply_weather_effects(self):
        """Apply weather effects to the farm."""
        # Apply precipitation to all tiles
        if self.weather_data["precipitation"] > 0:
            rain_amount = self.weather_data["precipitation"] / 10  # Scale to reasonable value
            
            for y in range(self.farm.height):
                for x in range(self.farm.width):
                    tile = self.farm.get_tile(x, y)
                    if tile:
                        # Add water from rain
                        before = tile.water_level
                        tile.water_level = min(tile.water_level + rain_amount * 0.1, tile.max_water)
                        self.farm.water_used += tile.water_level - before  # Count rainfall in water used
        
        # Temperature extremes affect crop health
        temp = self.weather_data["temperature"]
        if temp < 5 or temp > 35:  # Too cold or too hot
            damage_factor = 0.05  # 5% damage per day of extreme weather
            
            for y in range(self.farm.height):
                for x in range(self.farm.width):
                    tile = self.farm.get_tile(x, y)
                    if tile and tile.crop:
                        # Reduce crop health
                        tile.crop.health = max(0.1, tile.crop.health - damage_factor)
                        
    def _generate_forecast_image(self):
        """Generate a weather forecast image using matplotlib."""
        if self.weather_forecast is None:
            return
            
        # Check if forecast is a DataFrame and has enough data
        if not isinstance(self.weather_forecast, pd.DataFrame) or self.weather_forecast.empty or len(self.weather_forecast) < 7:
            return
        
        # Create figure and axes
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), dpi=80)
        fig.patch.set_alpha(0.0)  # Transparent background
        
        # Convert date strings to datetime objects for better x-axis formatting
        dates = [datetime.strptime(d, "%Y-%m-%d") for d in self.weather_forecast['date']]
        
        # Plot temperature
        ax1.plot(dates, self.weather_forecast['temperature'], label='Avg Temp', color='orange', linewidth=2)
        ax1.fill_between(dates, 
                        self.weather_forecast['temperature_min'], 
                        self.weather_forecast['temperature_max'], 
                        alpha=0.2, color='orange')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('30-Day Weather Forecast')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot precipitation
        ax2.bar(dates, self.weather_forecast['precipitation'], width=0.8, 
               label='Precipitation (mm)', color='blue', alpha=0.7)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Precipitation (mm)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Format the x-axis to show dates nicely
        fig.autofmt_xdate()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to a BytesIO object
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Load the image into a pygame surface
        forecast_image = pygame.image.load(buffer)
        self.assets['images']['forecast'] = forecast_image
        
        # Close the figure to free memory
        plt.close(fig)
        
    def _render(self):
        """Render the game."""
        # Clear the screen
        self.screen.fill((135, 206, 235))  # Sky blue background
        
        # Show loading screen if NASA data is still loading
        if self.nasa_data_loading:
            self._draw_nasa_loading_screen()
        else:
            # Draw the farm
            self._draw_farm()
            
            # Draw UI elements
            self._draw_ui()
            
            # Draw the active tool indicator
            self._draw_active_tool_indicator()
        
        # Update the display
        pygame.display.flip()
        
    def _draw_nasa_loading_screen(self):
        """Draw the NASA data loading screen."""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(240)
        overlay.fill((25, 25, 50))  # Dark blue overlay
        self.screen.blit(overlay, (0, 0))
        
        # Calculate responsive sizing based on screen dimensions
        center_x = self.width // 2
        center_y = self.height // 2
        
        # NASA logo area (responsive sizing) - adjusted for better text fit
        logo_width = min(350, self.width // 3)
        logo_height = 100
        logo_rect = pygame.Rect(center_x - logo_width // 2, center_y - 160, logo_width, logo_height)
        pygame.draw.rect(self.screen, (255, 255, 255), logo_rect, 2)
        
        # NASA text (responsive font size) - positioned in upper part of box
        font_size_large = min(48, self.width // 20)
        font_large = pygame.font.SysFont('Arial', font_size_large, bold=True)
        nasa_text = font_large.render("NASA", True, (255, 255, 255))
        nasa_rect = nasa_text.get_rect(center=(center_x, center_y - 135))
        self.screen.blit(nasa_text, nasa_rect)
        
        # Subtitle (responsive font size) - positioned in lower part of box
        font_size_medium = min(20, self.width // 50)
        font_medium = pygame.font.SysFont('Arial', font_size_medium)
        subtitle_text = font_medium.render("Farm Navigator", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(center_x, center_y - 105))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Loading message with animated dots (with text wrapping)
        font_size_regular = min(28, self.width // 35)
        font_regular = pygame.font.SysFont('Arial', font_size_regular)
        dots = "." * self.nasa_loading_dots
        loading_text = f"{self.nasa_loading_message}{dots}"
        
        # Check if text fits, if not, truncate or wrap
        max_width = self.width - 100  # Leave 50px margin on each side
        loading_surface = font_regular.render(loading_text, True, (255, 255, 255))
        
        if loading_surface.get_width() > max_width:
            # Truncate the message if it's too long
            base_message = self.nasa_loading_message[:30] + "..." if len(self.nasa_loading_message) > 30 else self.nasa_loading_message
            loading_text = f"{base_message}{dots}"
            loading_surface = font_regular.render(loading_text, True, (255, 255, 255))
        
        loading_rect = loading_surface.get_rect(center=(center_x, center_y - 20))
        self.screen.blit(loading_surface, loading_rect)
        
        # Progress indicator (spinning circle) - responsive size
        progress_y = center_y + 40
        radius = min(30, self.width // 30)
        
        # Calculate rotation angle based on time
        current_time = pygame.time.get_ticks()
        angle = (current_time // 50) % 360  # Rotate every 50ms
        
        # Draw spinning segments
        segment_count = 8
        for i in range(segment_count):
            segment_angle = (angle + i * 45) % 360
            # Calculate segment opacity (fade effect)
            opacity = 255 - (i * 30)
            if opacity < 50:
                opacity = 50
                
            # Calculate segment end position
            import math
            end_x = center_x + radius * math.cos(math.radians(segment_angle))
            end_y = progress_y + radius * math.sin(math.radians(segment_angle))
            
            # Draw segment
            pygame.draw.line(self.screen, (opacity, opacity, opacity), 
                           (center_x, progress_y), (end_x, end_y), 4)
        
        # Status information (responsive and with wrapping)
        font_size_small = min(18, self.width // 60)
        font_small = pygame.font.SysFont('Arial', font_size_small)
        status_lines = [
            "Connecting to NASA POWER API",
            "Fetching climate data for simulation",
            "Please wait for real satellite data..."
        ]
        
        # Calculate starting position for status text to ensure it fits
        status_start_y = center_y + 100
        max_status_width = self.width - 80  # Leave 40px margin on each side
        
        for i, line in enumerate(status_lines):
            # Check if line fits, if not, truncate
            status_surface = font_small.render(line, True, (180, 180, 180))
            if status_surface.get_width() > max_status_width:
                # Truncate line if too long
                truncated_line = line[:max(20, max_status_width // (font_size_small // 2))] + "..."
                status_surface = font_small.render(truncated_line, True, (180, 180, 180))
            
            status_y = status_start_y + i * (font_size_small + 5)
            # Ensure status text doesn't go off screen
            if status_y + font_size_small < self.height - 80:
                status_rect = status_surface.get_rect(center=(center_x, status_y))
                self.screen.blit(status_surface, status_rect)
        
        # NASA branding footer (ensure it fits)
        footer_text = "Powered by NASA Earth Science Data"
        footer_surface = font_small.render(footer_text, True, (150, 150, 150))
        if footer_surface.get_width() > max_status_width:
            footer_text = "NASA Earth Science Data"
            footer_surface = font_small.render(footer_text, True, (150, 150, 150))
        
        footer_rect = footer_surface.get_rect(center=(center_x, self.height - 50))
        self.screen.blit(footer_surface, footer_rect)
    
    def _draw_active_tool_indicator(self):
        """Draw an indicator showing the current active tool."""
        if not self.active_tool:
            return
            
        # Tool properties
        tool_colors = {
            "plant": (0, 128, 0),      # Green
            "water": (0, 0, 255),      # Blue
            "fertilize": (139, 69, 19), # Brown
            "harvest": (255, 215, 0)    # Gold
        }
        
        # Create a semi-transparent indicator at the mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Only show indicator when over the farm area
        grid_x, grid_y = self._screen_to_grid(mouse_pos)
        if grid_x < 0 or grid_x >= self.farm.width or grid_y < 0 or grid_y >= self.farm.height:
            return
        
        # Draw a translucent tool indicator that follows the mouse
        indicator_size = 40
        indicator_surf = pygame.Surface((indicator_size, indicator_size), pygame.SRCALPHA)
        
        # Fill with tool color
        indicator_color = tool_colors.get(self.active_tool, (100, 100, 100))
        pygame.draw.circle(indicator_surf, (*indicator_color, 100), (indicator_size//2, indicator_size//2), indicator_size//2)
        
        # Add border
        pygame.draw.circle(indicator_surf, (255, 255, 255, 180), (indicator_size//2, indicator_size//2), indicator_size//2, 2)
        
        # Draw tool icon or letter
        font = pygame.font.SysFont(None, 24)
        letter = self.active_tool[0].upper()  # First letter of tool name
        letter_surf = font.render(letter, True, (255, 255, 255))
        letter_rect = letter_surf.get_rect(center=(indicator_size//2, indicator_size//2))
        indicator_surf.blit(letter_surf, letter_rect)
        
        # Draw at mouse position
        self.screen.blit(indicator_surf, (mouse_pos[0] - indicator_size//2, mouse_pos[1] - indicator_size//2))
        
    def _draw_farm(self):
        """Draw the farm grid."""
        # Calculate the available space for the farm (accounting for sidebar and panels on the right)
        sidebar_width = 300
        right_panels_width = 350  # Fixed width for panels on the right side
        farm_area_width = self.width - sidebar_width - right_panels_width - 60  # Add padding on both sides
        farm_area_height = self.height - 100  # 100px for top UI
        
        # Calculate cell size to fit the farm in the available space
        cell_size = min(farm_area_width // self.farm.width, farm_area_height // self.farm.height)
        
        # Calculate farm rendering position (centered in available space)
        # Position between the sidebar on the left and panels on the right
        farm_start_x = sidebar_width + 30 + (farm_area_width - (cell_size * self.farm.width)) // 2
        farm_start_y = 100 + (farm_area_height - (cell_size * self.farm.height)) // 2
        
        # Store these values for future reference (like mouse interaction)
        self.farm_render_info = {
            'cell_size': cell_size,
            'start_x': farm_start_x,
            'start_y': farm_start_y,
            'farm_area_width': farm_area_width,
            'farm_area_height': farm_area_height
        }
        
        # Create a clipping rectangle for the farm area
        farm_clip_rect = pygame.Rect(farm_start_x, farm_start_y, farm_area_width, farm_area_height)
        self.screen.set_clip(farm_clip_rect)
        
        # Draw enhanced farm background with natural field patterns
        farm_bg = pygame.Rect(farm_start_x - 5 - self.scroll_x, farm_start_y - 5 - self.scroll_y, 
                             cell_size * self.farm.width + 10, 
                             cell_size * self.farm.height + 10)
        
        # Create a gradient background for the farm area
        for i in range(farm_bg.height):
            gradient_color = (
                max(80, 100 - i // 3),   # Slightly varying brown
                max(50, 70 - i // 4), 
                max(20, 40 - i // 5)
            )
            pygame.draw.rect(self.screen, gradient_color, 
                           (farm_bg.x, farm_bg.y + i, farm_bg.width, 1))
        
        # Add farm boundary fence with posts
        fence_color = (101, 67, 33)  # Dark brown for fence
        pygame.draw.rect(self.screen, fence_color, farm_bg, 3)  # Thick border
        
        # Add fence posts at corners and intervals
        post_size = max(4, cell_size // 6)
        post_color = (80, 53, 26)  # Darker brown for posts
        
        # Corner posts
        corners = [
            (farm_bg.left - post_size//2, farm_bg.top - post_size//2),
            (farm_bg.right - post_size//2, farm_bg.top - post_size//2),
            (farm_bg.left - post_size//2, farm_bg.bottom - post_size//2),
            (farm_bg.right - post_size//2, farm_bg.bottom - post_size//2)
        ]
        
        for corner_x, corner_y in corners:
            pygame.draw.rect(self.screen, post_color, (corner_x, corner_y, post_size, post_size))
        
        # Add gate entrance (decorative)
        gate_width = cell_size * 2
        gate_x = farm_bg.centerx - gate_width // 2
        gate_y = farm_bg.bottom - 3
        pygame.draw.rect(self.screen, (139, 118, 76), (gate_x, gate_y, gate_width, 6))  # Dirt entrance
        
        # Add small decorative elements around the farm
        # Water trough (if farm is large enough)
        if self.farm.width > 8 and self.farm.height > 8:
            trough_x = farm_bg.right + 10
            trough_y = farm_bg.top + cell_size * 2
            trough_rect = pygame.Rect(trough_x, trough_y, cell_size//2, cell_size//3)
            pygame.draw.rect(self.screen, (100, 100, 100), trough_rect)  # Gray trough
            pygame.draw.rect(self.screen, (0, 100, 255), trough_rect.inflate(-4, -2))  # Blue water
        
        # Add tool shed (decorative)
        if self.farm.width > 10:
            shed_x = farm_bg.left - cell_size
            shed_y = farm_bg.top
            shed_rect = pygame.Rect(shed_x, shed_y, cell_size//2, cell_size//2)
            pygame.draw.rect(self.screen, (139, 69, 19), shed_rect)  # Brown shed
            # Shed roof
            roof_points = [
                (shed_rect.left, shed_rect.top),
                (shed_rect.centerx, shed_rect.top - cell_size//6),
                (shed_rect.right, shed_rect.top)
            ]
            pygame.draw.polygon(self.screen, (101, 67, 33), roof_points)
        
        # Draw field pathways every 5-6 rows/columns for realistic farm layout
        path_color = (160, 130, 80)  # Dirt path color
        path_width = max(2, cell_size // 8)
        
        # Horizontal paths
        for path_row in range(5, self.farm.height, 6):
            path_y = farm_start_y + path_row * cell_size - self.scroll_y
            pygame.draw.rect(self.screen, path_color, 
                           (farm_start_x - self.scroll_x, path_y - path_width//2, 
                            cell_size * self.farm.width, path_width))
        
        # Vertical paths  
        for path_col in range(5, self.farm.width, 6):
            path_x = farm_start_x + path_col * cell_size - self.scroll_x
            pygame.draw.rect(self.screen, path_color,
                           (path_x - path_width//2, farm_start_y - self.scroll_y,
                            path_width, cell_size * self.farm.height))
        
        # Add field section markers (lighter borders every 3x3 sections)
        section_color = (120, 90, 50)  # Medium brown for section borders
        for section_y in range(0, self.farm.height, 3):
            for section_x in range(0, self.farm.width, 3):
                section_rect = pygame.Rect(
                    farm_start_x + section_x * cell_size - self.scroll_x,
                    farm_start_y + section_y * cell_size - self.scroll_y,
                    min(3 * cell_size, (self.farm.width - section_x) * cell_size),
                    min(3 * cell_size, (self.farm.height - section_y) * cell_size)
                )
                pygame.draw.rect(self.screen, section_color, section_rect, 1)
        
        # Draw the farm grid (with scroll offset)
        for y in range(self.farm.height):
            for x in range(self.farm.width):
                rect = pygame.Rect(
                    farm_start_x + x * cell_size - self.scroll_x, 
                    farm_start_y + y * cell_size - self.scroll_y, 
                    cell_size, 
                    cell_size
                )
                
                # Only draw tiles that are visible
                if rect.right < farm_start_x or rect.left > farm_start_x + farm_area_width:
                    continue
                if rect.bottom < farm_start_y or rect.top > farm_start_y + farm_area_height:
                    continue
                rect = pygame.Rect(
                    farm_start_x + x * cell_size, 
                    farm_start_y + y * cell_size, 
                    cell_size, 
                    cell_size
                )
                
                # Draw soil with enhanced appearance
                soil_img = pygame.transform.scale(self.assets['images']['soil'], (cell_size, cell_size))
                self.screen.blit(soil_img, rect)
                
                # Add subtle tile borders for definition
                border_color = (120, 80, 40)  # Darker brown for tile borders
                pygame.draw.rect(self.screen, border_color, rect, 1)
                
                # Draw crop if present
                tile = self.farm.get_tile(x, y)
                if tile.crop:
                    # Add subtle shadow behind crop for depth
                    shadow_offset = max(1, cell_size // 16)
                    shadow_rect = pygame.Rect(rect.x + shadow_offset, rect.y + shadow_offset, 
                                            rect.width, rect.height)
                    shadow_surface = pygame.Surface((cell_size, cell_size))
                    shadow_surface.set_alpha(30)
                    shadow_surface.fill((0, 0, 0))
                    self.screen.blit(shadow_surface, shadow_rect)
                    
                    crop_type = tile.crop.type
                    if crop_type in self.assets['images']:
                        # Scale and apply the crop image
                        crop_img = pygame.transform.scale(self.assets['images'][crop_type], (cell_size, cell_size))
                        
                        # Apply growth stage scaling effect
                        growth = tile.crop.growth_stage
                        if growth < 1.0:
                            # Scale crop based on growth stage for visual progression
                            # Start at 90% size so newly planted crops almost fill the entire cell
                            scale_factor = 0.9 + (growth * 0.1)  # 90% to 100% size
                            scaled_size = int(cell_size * scale_factor)
                            if scaled_size > 0:
                                crop_img = pygame.transform.scale(crop_img, (scaled_size, scaled_size))
                                # Center the scaled crop in the cell
                                crop_rect = pygame.Rect(
                                    rect.x + (cell_size - scaled_size) // 2,
                                    rect.y + (cell_size - scaled_size) // 2,
                                    scaled_size, scaled_size
                                )
                                self.screen.blit(crop_img, crop_rect)
                            else:
                                # Fallback - show small green sprout
                                pygame.draw.circle(self.screen, (0, 150, 0), rect.center, max(3, cell_size // 8))
                                pygame.draw.line(self.screen, (34, 139, 34), 
                                               (rect.centerx, rect.centery + max(3, cell_size // 8)), 
                                               (rect.centerx, rect.centery - max(3, cell_size // 8)), 2)
                        else:
                            self.screen.blit(crop_img, rect)
                    else:
                        # Scale the default crop image to fit the cell size
                        crop_img = pygame.transform.scale(self.assets['images']['crop'], (cell_size, cell_size))
                        self.screen.blit(crop_img, rect)
                    
                    # Enhanced crop growth progress bar
                    growth = tile.crop.growth_stage
                    if growth > 0:
                        # Create a more attractive progress bar
                        bar_height = max(3, cell_size // 8)
                        bar_y = rect.y - bar_height - 2
                        
                        # Background for progress bar
                        bar_bg = pygame.Rect(rect.x + 2, bar_y, rect.width - 4, bar_height)
                        pygame.draw.rect(self.screen, (0, 0, 0), bar_bg)
                        pygame.draw.rect(self.screen, (60, 60, 60), bar_bg, 1)
                        
                        # Progress fill with gradient effect
                        progress_width = int((rect.width - 6) * growth)
                        if progress_width > 0:
                            progress_rect = pygame.Rect(rect.x + 3, bar_y + 1, progress_width, bar_height - 2)
                            
                            # Color changes based on growth stage
                            if growth < 0.3:
                                bar_color = (255, 100, 100)  # Red for early growth
                            elif growth < 0.7:
                                bar_color = (255, 255, 100)  # Yellow for mid growth
                            else:
                                bar_color = (100, 255, 100)  # Green for near maturity
                            
                            pygame.draw.rect(self.screen, bar_color, progress_rect)
                            
                            # Add highlight for 3D effect
                            highlight_rect = pygame.Rect(progress_rect.x, progress_rect.y, 
                                                       progress_rect.width, 1)
                            highlight_color = tuple(min(255, c + 40) for c in bar_color)
                            pygame.draw.rect(self.screen, highlight_color, highlight_rect)
                    
                    # Visualize crop health issues
                    if tile.crop.disease_status:
                        # Red overlay for disease
                        disease_overlay = pygame.Surface((cell_size, cell_size))
                        disease_overlay.set_alpha(60 + int(tile.crop.disease_severity * 100))  # Opacity based on severity
                        disease_overlay.fill((255, 0, 0))  # Red
                        self.screen.blit(disease_overlay, rect)
                        
                        # Disease icon (red X)
                        pygame.draw.line(self.screen, (255, 0, 0), 
                                       (rect.x + 2, rect.y + 2), 
                                       (rect.x + 8, rect.y + 8), 2)
                        pygame.draw.line(self.screen, (255, 0, 0), 
                                       (rect.x + 8, rect.y + 2), 
                                       (rect.x + 2, rect.y + 8), 2)
                    
                    if tile.crop.pest_status:
                        # Yellow overlay for pests
                        pest_overlay = pygame.Surface((cell_size, cell_size))
                        pest_overlay.set_alpha(40 + int(tile.crop.pest_severity * 80))  # Opacity based on severity
                        pest_overlay.fill((255, 255, 0))  # Yellow
                        self.screen.blit(pest_overlay, rect)
                        
                        # Pest icon (small yellow circles)
                        for i in range(3):
                            for j in range(3):
                                if (i + j) % 2 == 0:  # Checkerboard pattern
                                    pygame.draw.circle(self.screen, (255, 200, 0), 
                                                     (rect.x + 2 + i * 3, rect.y + 2 + j * 3), 1)
                    
                    # Weather stress visualization
                    weather_stress = tile.crop.get_weather_stress_level()
                    if weather_stress > 0.1:
                        stress_type = tile.crop.get_dominant_weather_stress()
                        stress_colors = {
                            "frost": (150, 200, 255),    # Light blue for frost
                            "heat": (255, 150, 100),     # Orange for heat
                            "drought": (200, 150, 100),  # Brown for drought  
                            "flood": (100, 150, 255)     # Blue for flood
                        }
                        
                        if stress_type in stress_colors:
                            # Weather stress overlay
                            weather_overlay = pygame.Surface((cell_size, cell_size))
                            weather_overlay.set_alpha(30 + int(weather_stress * 70))
                            weather_overlay.fill(stress_colors[stress_type])
                            self.screen.blit(weather_overlay, rect)
                            
                            # Weather stress icon in corner
                            icon_symbols = {
                                "frost": "❄",
                                "heat": "🌡",
                                "drought": "🏜",
                                "flood": "🌊"
                            }
                            # Draw simple symbol (using basic shapes since emoji might not render)
                            if stress_type == "frost":
                                # Draw frost symbol (asterisk-like)
                                center_x, center_y = rect.right - 8, rect.y + 8
                                pygame.draw.line(self.screen, (150, 200, 255), 
                                               (center_x - 3, center_y), (center_x + 3, center_y), 2)
                                pygame.draw.line(self.screen, (150, 200, 255), 
                                               (center_x, center_y - 3), (center_x, center_y + 3), 2)
                            elif stress_type == "heat":
                                # Draw heat symbol (small circles)
                                center_x, center_y = rect.right - 8, rect.y + 8
                                pygame.draw.circle(self.screen, (255, 150, 100), (center_x, center_y), 3)
                            elif stress_type == "drought":
                                # Draw drought symbol (wavy line)
                                start_x, start_y = rect.right - 12, rect.y + 8
                                pygame.draw.line(self.screen, (200, 150, 100), 
                                               (start_x, start_y), (start_x + 8, start_y), 2)
                            elif stress_type == "flood":
                                # Draw flood symbol (wave pattern)
                                start_x, start_y = rect.right - 12, rect.y + 8
                                for i in range(0, 8, 2):
                                    pygame.draw.line(self.screen, (100, 150, 255), 
                                                   (start_x + i, start_y - 1), (start_x + i + 1, start_y + 1), 1)
                    
                    # Protection indicator (enhanced visibility)
                    if tile.crop.weather_protection:
                        # Larger, more visible shield indicator
                        shield_center_x = rect.x + 8
                        shield_center_y = rect.y + 8
                        
                        # Draw shield shape
                        shield_points = [
                            (shield_center_x, shield_center_y - 6),      # Top
                            (shield_center_x - 4, shield_center_y - 2), # Top left
                            (shield_center_x - 4, shield_center_y + 2), # Bottom left
                            (shield_center_x, shield_center_y + 6),      # Bottom point
                            (shield_center_x + 4, shield_center_y + 2), # Bottom right
                            (shield_center_x + 4, shield_center_y - 2)  # Top right
                        ]
                        
                        pygame.draw.polygon(self.screen, (0, 255, 0), shield_points)
                        pygame.draw.polygon(self.screen, (0, 150, 0), shield_points, 2)
                        
                        # Show remaining protection days
                        if hasattr(tile.crop, 'protection_days_left'):
                            days_font = pygame.font.SysFont(None, 14)
                            days_text = str(tile.crop.protection_days_left)
                            days_color = (255, 255, 255) if tile.crop.protection_days_left > 2 else (255, 200, 0)
                            days_surface = days_font.render(days_text, True, days_color)
                            text_x = shield_center_x - days_surface.get_width() // 2
                            text_y = shield_center_y - days_surface.get_height() // 2
                            self.screen.blit(days_surface, (text_x, text_y))
                        else:
                            # Add a small cross or plus sign in the center for legacy protection
                            pygame.draw.line(self.screen, (255, 255, 255), 
                                           (shield_center_x - 2, shield_center_y), 
                                           (shield_center_x + 2, shield_center_y), 2)
                            pygame.draw.line(self.screen, (255, 255, 255), 
                                           (shield_center_x, shield_center_y - 2), 
                                           (shield_center_x, shield_center_y + 2), 2)
                    
                    # Health indicator border
                    if tile.crop.health < 0.5:
                        # Draw red border for unhealthy crops
                        border_thickness = max(1, int((1 - tile.crop.health) * 3))
                        pygame.draw.rect(self.screen, (255, 0, 0), rect, border_thickness)
                    
                    # Urgent warning system - ONLY for diseases and pests (not weather stress)
                    is_diseased = tile.crop.disease_status is not None
                    is_infested = tile.crop.pest_status is not None
                    
                    # ONLY show urgent warning for actual diseases or pests
                    if is_diseased or is_infested:
                        # Flashing red border for urgent attention
                        import time
                        if int(time.time() * 3) % 2:  # Flash every 0.33 seconds
                            urgent_rect = pygame.Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 4)
                            pygame.draw.rect(self.screen, (255, 0, 0), urgent_rect, 3)
                            
                            # Add urgent text
                            urgent_text = pygame.font.SysFont(None, 14).render("!", True, (255, 255, 255))
                            urgent_bg = pygame.Rect(rect.right - 12, rect.bottom - 12, 10, 10)
                            pygame.draw.rect(self.screen, (255, 0, 0), urgent_bg)
                            pygame.draw.circle(self.screen, (255, 0, 0), (rect.right - 7, rect.bottom - 7), 6)
                            self.screen.blit(urgent_text, (rect.right - 10, rect.bottom - 11))
                
                # Draw water indicator if watered
                if tile.water_level > 0:
                    water_height_pct = tile.water_level / tile.max_water
                    water_height = int(rect.height * 0.25 * water_height_pct)  # Max 25% of cell height
                    
                    if water_height > 0:
                        water_rect = pygame.Rect(
                            rect.x, rect.y + rect.height - water_height, 
                            rect.width, water_height
                        )
                        water = pygame.Surface((rect.width, water_height))
                        water.fill((0, 0, 255))  # Blue
                        water.set_alpha(128)  # Semi-transparent
                        self.screen.blit(water, water_rect)
                
                # Draw watering animation if active
                if tile.showing_water_effect:
                    current_time = pygame.time.get_ticks()
                    elapsed = current_time - tile.water_effect_start
                    
                    if elapsed < tile.water_effect_duration:
                        # Calculate animation progress (0.0 to 1.0)
                        progress = elapsed / tile.water_effect_duration
                        
                        # Draw animated water droplets
                        num_droplets = 8
                        droplet_size = cell_size // 6
                        
                        for i in range(num_droplets):
                            # Calculate droplet position with animation
                            angle = 2 * np.pi * i / num_droplets
                            radius = cell_size/3 * (1 - progress)  # Shrinking radius
                            
                            drop_x = rect.centerx + radius * np.cos(angle)
                            drop_y = rect.centery + radius * np.sin(angle)
                            
                            # Make droplets fade out over time
                            alpha = 255 * (1 - progress)
                            
                            # Draw water droplet
                            droplet_surf = pygame.Surface((droplet_size, droplet_size), pygame.SRCALPHA)
                            pygame.draw.circle(droplet_surf, (0, 100, 255, int(alpha)), 
                                             (droplet_size//2, droplet_size//2), droplet_size//2)
                            self.screen.blit(droplet_surf, (drop_x - droplet_size//2, drop_y - droplet_size//2))
                    else:
                        # Animation complete
                        tile.showing_water_effect = False
                
                # Draw harvest animation if active
                if tile.showing_harvest_effect:
                    current_time = pygame.time.get_ticks()
                    elapsed = current_time - tile.harvest_effect_start
                    
                    if elapsed < tile.harvest_effect_duration:
                        # Calculate animation progress (0.0 to 1.0)
                        progress = elapsed / tile.harvest_effect_duration
                        
                        # Draw flying crop yield indicators
                        yield_text = f"+{tile.harvest_yield:.1f}"
                        font_size = int(24 + 12 * (1-progress))  # Font grows smaller
                        yield_font = pygame.font.SysFont(None, font_size)
                        
                        # Calculate text position with upward movement
                        text_y_offset = -40 * progress  # Text moves up
                        text_surf = yield_font.render(yield_text, True, (50, 205, 50))  # Green text
                        
                        # Position text above the tile
                        text_x = rect.centerx - text_surf.get_width() // 2
                        text_y = rect.y + text_y_offset
                        
                        # Draw with fade out
                        text_surf.set_alpha(int(255 * (1-progress)))
                        self.screen.blit(text_surf, (text_x, text_y))
                        
                        # Draw sparkle effects around the tile
                        num_sparkles = 12
                        sparkle_size = int(cell_size/8 * (1-progress))
                        
                        for i in range(num_sparkles):
                            # Calculate sparkle position with animation
                            angle = 2 * np.pi * i / num_sparkles
                            radius = cell_size/2 + cell_size/3 * progress  # Expanding radius
                            
                            sparkle_x = rect.centerx + radius * np.cos(angle)
                            sparkle_y = rect.centery + radius * np.sin(angle)
                            
                            # Alternate sparkle colors based on crop type
                            if tile.harvested_crop_type == "corn":
                                color = (255, 255, 0)  # Yellow for corn
                            elif tile.harvested_crop_type == "wheat":
                                color = (245, 222, 179)  # Tan for wheat
                            elif tile.harvested_crop_type == "tomato":
                                color = (255, 0, 0)  # Red for tomato
                            else:
                                color = (255, 215, 0)  # Gold by default
                                
                            # Make sparkles fade out over time
                            sparkle_alpha = int(255 * (1-progress))
                            
                            # Draw sparkle
                            pygame.draw.circle(self.screen, (*color, sparkle_alpha), 
                                            (int(sparkle_x), int(sparkle_y)), sparkle_size)
                    else:
                        # Animation complete
                        tile.showing_harvest_effect = False
                
                # Draw grid lines
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        
        # Reset clipping
        self.screen.set_clip(None)
        
        # Draw scroll bars
        self._draw_scroll_bars()
    
    def _draw_scroll_bars(self):
        """Draw horizontal and vertical scroll bars."""
        if not hasattr(self, 'farm_render_info'):
            return
            
        info = self.farm_render_info
        max_scroll_x = self._get_max_scroll_x()
        max_scroll_y = self._get_max_scroll_y()
        
        # Only draw scroll bars if scrolling is possible
        if max_scroll_x > 0 or max_scroll_y > 0:
            bar_thickness = 12
            bar_color = (128, 128, 128)
            thumb_color = (64, 64, 64)
            
            # Horizontal scroll bar
            if max_scroll_x > 0:
                bar_x = info['start_x']
                bar_y = info['start_y'] + info['farm_area_height'] - bar_thickness
                bar_width = info['farm_area_width']
                
                # Draw bar background
                pygame.draw.rect(self.screen, bar_color, 
                               (bar_x, bar_y, bar_width, bar_thickness))
                
                # Draw thumb
                thumb_width = max(20, int(bar_width * info['farm_area_width'] / (self.farm.width * info['cell_size'])))
                thumb_x = bar_x + int((bar_width - thumb_width) * self.scroll_x / max_scroll_x)
                pygame.draw.rect(self.screen, thumb_color,
                               (thumb_x, bar_y, thumb_width, bar_thickness))
            
            # Vertical scroll bar  
            if max_scroll_y > 0:
                bar_x = info['start_x'] + info['farm_area_width'] - bar_thickness
                bar_y = info['start_y']
                bar_height = info['farm_area_height']
                
                # Draw bar background
                pygame.draw.rect(self.screen, bar_color,
                               (bar_x, bar_y, bar_thickness, bar_height))
                
                # Draw thumb
                thumb_height = max(20, int(bar_height * info['farm_area_height'] / (self.farm.height * info['cell_size'])))
                thumb_y = bar_y + int((bar_height - thumb_height) * self.scroll_y / max_scroll_y)
                pygame.draw.rect(self.screen, thumb_color,
                               (bar_x, thumb_y, bar_thickness, thumb_height))
    
    def _draw_ui(self):
        """Draw UI elements."""
        # Draw sidebar background
        sidebar_width = 300
        sidebar = pygame.Rect(0, 0, sidebar_width, self.height)
        pygame.draw.rect(self.screen, (173, 216, 230), sidebar)  # Light blue
        
        # Draw top bar background
        top_bar = pygame.Rect(0, 0, self.width, 100)
        pygame.draw.rect(self.screen, (135, 206, 235), top_bar)  # Sky blue
        
        # Draw separator lines
        pygame.draw.line(self.screen, (0, 0, 0), (sidebar_width, 0), (sidebar_width, self.height), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (0, 100), (self.width, 100), 2)
        
        # Draw game date
        date_text = self.assets['fonts']['default'].render(
            f"Date: {self.current_date.strftime('%Y-%m-%d')}", True, (0, 0, 0)
        )
        self.screen.blit(date_text, (self.width // 2 - date_text.get_width() // 2, 10))
        
        # Draw graphical money display
        self._draw_money_display()
        
        # Draw profit display
        self._draw_profit_display()
        
        # Draw pause indicator if paused
        if self.paused:
            pause_text = self.assets['fonts']['default'].render(
                "PAUSED", True, (255, 0, 0)
            )
            self.screen.blit(pause_text, (self.width // 2 - 40, 35))
        
        # Draw game title
        title_text = pygame.font.SysFont(None, 36).render("NASA Farm Navigator", True, (0, 0, 100))
        self.screen.blit(title_text, (sidebar_width // 2 - title_text.get_width() // 2, 20))
        
        # Draw tool selection UI
        self._draw_tool_selection()
        
        # Draw crop selection UI
        self._draw_crop_selection()
        
        # Draw instructions
        self._draw_instructions()
        
        # Draw both panels by default
        self._draw_weather_panel()
        self._draw_weather_alerts_panel()
        self._draw_stats_panel()
    
    def _draw_tool_selection(self):
        """Draw the tool selection UI."""
        sidebar_width = 300
        
        # Create a background for the tool selection area
        tool_area = pygame.Rect(10, 100, sidebar_width - 20, 150)
        pygame.draw.rect(self.screen, (200, 200, 200), tool_area)
        pygame.draw.rect(self.screen, (0, 0, 0), tool_area, 2)
        
        # Display title
        title_text = pygame.font.SysFont(None, 30).render("Tools:", True, (0, 0, 0))
        self.screen.blit(title_text, (tool_area.centerx - title_text.get_width() // 2, tool_area.y + 10))
        
        # Tool options
        tools = ["plant", "water", "fertilize", "harvest", "treat", "protect"]
        tool_names = {"plant": "Plant", "water": "Water", "fertilize": "Fertilize", "harvest": "Harvest", "treat": "Treat", "protect": "Protect"}
        tool_colors = {
            "plant": (0, 128, 0),      # Green
            "water": (0, 0, 255),      # Blue
            "fertilize": (139, 69, 19), # Brown
            "harvest": (255, 215, 0),   # Gold
            "treat": (255, 0, 255),     # Magenta
            "protect": (0, 255, 255)    # Cyan
        }
        
        button_width = (sidebar_width - 60) // 3  # 3 columns for 6 tools
        button_height = 30  # Smaller height to fit 2 rows
        
        for i, tool in enumerate(tools):
            # Calculate button position (3x2 grid)
            row = i // 3
            col = i % 3
            
            button_rect = pygame.Rect(
                tool_area.x + 10 + col * (button_width + 5),
                tool_area.y + 40 + row * (button_height + 10),
                button_width,
                button_height
            )
            
            # Draw button with base color
            pygame.draw.rect(self.screen, tool_colors.get(tool, (100, 100, 100)), button_rect, 0)
            
            # Highlight the active tool with a more noticeable effect
            if self.active_tool == tool:
                # Draw a brighter button with a glowing effect
                glow_color = tuple(min(c + 80, 255) for c in tool_colors.get(tool, (100, 100, 100)))
                pygame.draw.rect(self.screen, glow_color, button_rect, 0)
                
                # Add an outer glow/border
                for thickness in range(1, 4):
                    glow_rect = pygame.Rect(
                        button_rect.x - thickness, 
                        button_rect.y - thickness,
                        button_rect.width + thickness * 2, 
                        button_rect.height + thickness * 2
                    )
                    # Decreasing alpha for outer glow
                    alpha = 150 - thickness * 40
                    color = (255, 255, 200, alpha)  # Yellow glow with alpha
                    
                    # Draw the glow using a surface with alpha
                    glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, color, 
                                   pygame.Rect(0, 0, glow_rect.width, glow_rect.height), 1)
                    self.screen.blit(glow_surf, glow_rect)
                
                # Draw a small indicator icon in the corner
                indicator_size = 15
                indicator_pos = (button_rect.x + 5, button_rect.y + 5)
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                  (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2), 
                                  indicator_size//2)
                pygame.draw.circle(self.screen, (0, 0, 0), 
                                  (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2), 
                                  indicator_size//2 - 2)
                pygame.draw.circle(self.screen, (255, 255, 0), 
                                  (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2), 
                                  indicator_size//2 - 4)
            
            # Always draw the border
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 1)
            
            # Display tool name with better contrast depending on active state
            text_color = (255, 255, 255)  # Default white text
            if self.active_tool == tool:
                text_color = (0, 0, 0)  # Black text for better contrast on active button
                
            tool_text = self.assets['fonts']['default'].render(tool_names[tool], True, text_color)
            self.screen.blit(tool_text, (button_rect.centerx - tool_text.get_width() // 2, button_rect.centery - tool_text.get_height() // 2 - 6))
            
            # Add cost information
            costs = {"plant": "Varies", "water": "$2", "fertilize": "$5", "harvest": "Free", "treat": "$15", "protect": "$25"}
            cost_font = pygame.font.SysFont(None, 18)
            cost_text = cost_font.render(costs.get(tool, ""), True, text_color)
            self.screen.blit(cost_text, (button_rect.centerx - cost_text.get_width() // 2, button_rect.centery + 6))
            
            # Add key shortcut hint
            key_hint = self.assets['fonts']['default'].render(f"({i+1})", True, (255, 255, 255))
            self.screen.blit(key_hint, (button_rect.right - key_hint.get_width() - 5, button_rect.bottom - key_hint.get_height() - 2))
            
            # Check for mouse click
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button
            
            if button_rect.collidepoint(mouse_pos) and mouse_pressed:
                self.active_tool = tool
                print(f"Selected tool: {tool}")
    
    def _draw_crop_selection(self):
        """Draw the crop selection UI."""
        sidebar_width = 300
        
        # Create a background for the crop selection area (smaller height)
        crop_area = pygame.Rect(10, 260, sidebar_width - 20, 100)
        pygame.draw.rect(self.screen, (200, 200, 200), crop_area)
        pygame.draw.rect(self.screen, (0, 0, 0), crop_area, 2)
        
        # Display title
        title_text = pygame.font.SysFont(None, 26).render("Crops:", True, (0, 0, 0))
        self.screen.blit(title_text, (crop_area.centerx - title_text.get_width() // 2, crop_area.y + 5))
        
        # Crop options
        crops = ["corn", "wheat", "tomato"]
        crop_names = {"corn": "Corn", "wheat": "Wheat", "tomato": "Tomato"}
        crop_keys = {"corn": "C", "wheat": "W", "tomato": "T"}
        crop_colors = {
            "corn": (255, 255, 0),    # Yellow
            "wheat": (245, 222, 179),  # Tan
            "tomato": (255, 0, 0)      # Red
        }
        
        button_width = (sidebar_width - 50) // 3
        button_height = 45  # Reduced height
        
        for i, crop in enumerate(crops):
            # Create button
            button_rect = pygame.Rect(
                crop_area.x + 10 + i * (button_width + 5),
                crop_area.y + 30,  # Adjusted y position
                button_width,
                button_height
            )
            
            # Draw button with base color
            pygame.draw.rect(self.screen, crop_colors.get(crop, (100, 100, 100)), button_rect, 0)
            
            # Highlight the selected crop with a more noticeable effect
            if self.selected_crop == crop:
                # Draw a brighter button with a glowing effect
                glow_color = tuple(min(c + 80, 255) for c in crop_colors.get(crop, (100, 100, 100)))
                pygame.draw.rect(self.screen, glow_color, button_rect, 0)
                
                # Add an outer glow/border
                for thickness in range(1, 4):
                    glow_rect = pygame.Rect(
                        button_rect.x - thickness, 
                        button_rect.y - thickness,
                        button_rect.width + thickness * 2, 
                        button_rect.height + thickness * 2
                    )
                    # Decreasing alpha for outer glow
                    alpha = 150 - thickness * 40
                    color = (255, 255, 200, alpha)  # Yellow glow with alpha
                    
                    # Draw the glow using a surface with alpha
                    glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, color, 
                                   pygame.Rect(0, 0, glow_rect.width, glow_rect.height), 1)
                    self.screen.blit(glow_surf, glow_rect)
                    
                # Add a "selected" indicator at the top right
                indicator_size = 15
                indicator_pos = (button_rect.right - indicator_size - 5, button_rect.y + 5)
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                  (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2), 
                                  indicator_size//2)
                pygame.draw.circle(self.screen, (0, 0, 0), 
                                  (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2), 
                                  indicator_size//2 - 2)
                pygame.draw.circle(self.screen, (255, 255, 0), 
                                  (indicator_pos[0] + indicator_size//2, indicator_pos[1] + indicator_size//2), 
                                  indicator_size//2 - 4)
            
            # Always draw the border
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 1)
            
            # Create a scaled version of the crop image as a preview
            if crop in self.assets['images']:
                preview_size = min(button_width - 10, button_height - 25)
                preview_img = pygame.transform.scale(self.assets['images'][crop], (preview_size, preview_size))
                preview_rect = preview_img.get_rect(center=(button_rect.centerx, button_rect.centery - 10))
                self.screen.blit(preview_img, preview_rect)
            
            # Display crop name
            crop_text = self.assets['fonts']['default'].render(crop_names[crop], True, (0, 0, 0))
            self.screen.blit(crop_text, (button_rect.centerx - crop_text.get_width() // 2, button_rect.bottom - 20))
            
            # Add key shortcut hint
            key_hint = self.assets['fonts']['default'].render(f"({crop_keys[crop]})", True, (0, 0, 0))
            self.screen.blit(key_hint, (button_rect.centerx - key_hint.get_width() // 2, button_rect.bottom - 5))
            
            # Check for mouse click
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button
            
            if button_rect.collidepoint(mouse_pos) and mouse_pressed:
                self.selected_crop = crop
                print(f"Selected crop: {crop}")
    
    def _draw_weather_panel(self):
        """Draw the weather forecast panel."""
        # Create forecast image if needed and valid weather data exists
        if 'forecast' not in self.assets['images'] and self.weather_forecast is not None:
            if isinstance(self.weather_forecast, pd.DataFrame) and not self.weather_forecast.empty and len(self.weather_forecast) >= 7:
                self._generate_forecast_image()
        
        # Draw current weather conditions in the top bar area
        weather_text = self.assets['fonts']['default'].render(
            f"Weather: {self.weather_data['temperature']:.1f}°C, {self.weather_data['precipitation']:.1f}mm rain", 
            True, (0, 0, 0)
        )
        self.screen.blit(weather_text, (self.width // 2 - weather_text.get_width() // 2, 40))
        
        # Draw weather icon based on conditions
        weather_icon_size = 40
        weather_icon_pos = (self.width // 2 + weather_text.get_width() // 2 + 20, 30)
        
        if self.weather_data["precipitation"] > 5:
            # Rainy weather icon - blue raindrop
            pygame.draw.polygon(self.screen, (0, 0, 255), 
                               [(weather_icon_pos[0], weather_icon_pos[1]), 
                                (weather_icon_pos[0] + weather_icon_size, weather_icon_pos[1]),
                                (weather_icon_pos[0] + weather_icon_size//2, weather_icon_pos[1] + weather_icon_size)])
        elif self.weather_data["temperature"] > 30:
            # Hot weather icon - red sun
            pygame.draw.circle(self.screen, (255, 0, 0), 
                              (weather_icon_pos[0] + weather_icon_size//2, weather_icon_pos[1] + weather_icon_size//2), 
                              weather_icon_size//2)
        elif self.weather_data["temperature"] < 10:
            # Cold weather icon - blue snowflake
            pygame.draw.circle(self.screen, (0, 191, 255), 
                              (weather_icon_pos[0] + weather_icon_size//2, weather_icon_pos[1] + weather_icon_size//2), 
                              weather_icon_size//2)
        else:
            # Fair weather icon - yellow sun
            pygame.draw.circle(self.screen, (255, 255, 0), 
                              (weather_icon_pos[0] + weather_icon_size//2, weather_icon_pos[1] + weather_icon_size//2), 
                              weather_icon_size//2)
        
        # Draw the forecast panel on the right side if available
        if 'forecast' in self.assets['images']:
            sidebar_width = 300
            
            # Create a dedicated panel for the forecast with a nice background - standardized width
            forecast_panel_width = 320  # Standardized width for all panels
            forecast_panel_height = 300  # Adjusted height for better spacing
            
            # Position the panel on the right side of the screen, below alerts panel
            forecast_panel_x = self.width - forecast_panel_width - 10
            forecast_panel_y = 285  # Moved down to accommodate compact alerts panel
            
            # Draw panel background with gradient
            forecast_panel = pygame.Rect(forecast_panel_x, forecast_panel_y, 
                                       forecast_panel_width, forecast_panel_height)
            
            # Create a gradient background (light blue to darker blue)
            for i in range(forecast_panel_height):
                # Gradient from light to slightly darker blue
                color = (173 - i/10, 216 - i/10, 230 - i/10)
                pygame.draw.line(self.screen, color, 
                               (forecast_panel_x, forecast_panel_y + i),
                               (forecast_panel_x + forecast_panel_width, forecast_panel_y + i))
            
            # Add a border
            pygame.draw.rect(self.screen, (0, 0, 100), forecast_panel, 2)
            
            # Add a title with a header bar
            header_rect = pygame.Rect(forecast_panel_x, forecast_panel_y, 
                                    forecast_panel_width, 40)
            pygame.draw.rect(self.screen, (0, 0, 100), header_rect)
            
            # Add title text
            forecast_title = pygame.font.SysFont(None, 32).render("NASA Weather Forecast", True, (255, 255, 255))
            self.screen.blit(forecast_title, (header_rect.centerx - forecast_title.get_width() // 2, 
                                             header_rect.y + 10))
            
            # Get the forecast image
            forecast_img = self.assets['images']['forecast']
            
            # Scale the forecast image to fit the panel, leaving more space for text
            max_width = forecast_panel_width - 20
            max_height = forecast_panel_height - 150  # Increased space for additional info
            
            img_ratio = min(max_width / forecast_img.get_width(), max_height / forecast_img.get_height())
            new_size = (int(forecast_img.get_width() * img_ratio), int(forecast_img.get_height() * img_ratio))
            
            forecast_img = pygame.transform.scale(forecast_img, new_size)
            
            # Center the image in the panel
            img_x = forecast_panel_x + (forecast_panel_width - new_size[0]) // 2
            img_y = forecast_panel_y + 50  # Below the header
            self.screen.blit(forecast_img, (img_x, img_y))
            
            # Add additional weather information below the image
            info_y = img_y + new_size[1] + 20  # Increased spacing
            
            # Add a data source credit
            data_source = pygame.font.SysFont(None, 18).render("Data source: NASA POWER API", True, (0, 0, 100))
            self.screen.blit(data_source, (forecast_panel_x + 10, info_y))
            
            # Add some weather advice based on the forecast
            avg_temp = sum(self.weather_forecast['temperature'][:7]) / 7
            avg_precip = sum(self.weather_forecast['precipitation'][:7]) / 7
            
            if avg_temp > 25:
                advice = "Weather Tip: High temperatures ahead."
                advice2 = "Water crops frequently to prevent drought stress."
            elif avg_temp < 10:
                advice = "Weather Tip: Cold temperatures ahead."
                advice2 = "Protect sensitive crops from frost damage."
            elif avg_precip > 5:
                advice = "Weather Tip: Rainy days ahead."
                advice2 = "Reduce manual watering to prevent overwatering."
            else:
                advice = "Weather Tip: Mild conditions ahead."
                advice2 = "Ideal growing weather for most crops."
                
            # Split the advice into two lines to prevent cutoff
            advice_text1 = pygame.font.SysFont(None, 22).render(advice, True, (0, 0, 100))
            advice_text2 = pygame.font.SysFont(None, 22).render(advice2, True, (0, 0, 100))
            
            self.screen.blit(advice_text1, (forecast_panel_x + 10, info_y + 25))
            self.screen.blit(advice_text2, (forecast_panel_x + 10, info_y + 50))
            
    def _draw_weather_alerts_panel(self):
        """Draw the weather alerts panel."""
        if not self.weather_alerts:
            return  # Don't draw if no alerts
            
        # Panel position - fit between profit and forecast panels with standardized width
        alert_panel_x = self.width - 320 - 10  # Standardized width alignment
        alert_panel_y = 195  # Position between profit (190) and forecast (210)  
        alert_panel_width = 320  # Standardized width for all panels
        alert_panel_height = min(85, len(self.weather_alerts) * 25 + 35)  # Much more compact
        
        # Draw panel background
        alert_panel = pygame.Rect(alert_panel_x, alert_panel_y, alert_panel_width, alert_panel_height)
        pygame.draw.rect(self.screen, (255, 235, 205), alert_panel)  # Pale orange background
        pygame.draw.rect(self.screen, (255, 140, 0), alert_panel, 2)  # Orange border
        
        # Draw header - more compact
        header_rect = pygame.Rect(alert_panel_x, alert_panel_y, alert_panel_width, 25)
        pygame.draw.rect(self.screen, (255, 140, 0), header_rect)
        
        # Header text - smaller font
        header_text = pygame.font.SysFont(None, 22).render("⚠️ Weather Alerts", True, (255, 255, 255))
        self.screen.blit(header_text, (alert_panel_x + 8, alert_panel_y + 4))
        
        # Draw alerts - more compact
        y_offset = alert_panel_y + 30
        font = pygame.font.SysFont(None, 18)  # Smaller font
        
        for i, alert in enumerate(self.weather_alerts[:3]):  # Limit to 3 alerts for compactness
            # Determine alert color based on severity
            if "WARNING" in alert:
                alert_color = (255, 0, 0)  # Red for warnings
                bg_color = (255, 220, 220)  # Light red background
            elif "Alert" in alert:
                alert_color = (255, 140, 0)  # Orange for alerts
                bg_color = (255, 240, 200)  # Light orange background
            else:
                alert_color = (0, 100, 0)  # Green for tips
                bg_color = (220, 255, 220)  # Light green background
            
            # Draw alert background - more compact
            alert_bg = pygame.Rect(alert_panel_x + 3, y_offset - 2, alert_panel_width - 6, 20)
            pygame.draw.rect(self.screen, bg_color, alert_bg, 0, 3)  # Rounded corners
            
            # Truncate long alert text for compact display
            alert_text = alert
            if len(alert_text) > 50:
                alert_text = alert_text[:47] + "..."
                
            # Single line alert - compact
            alert_surface = font.render(alert_text, True, alert_color)
            self.screen.blit(alert_surface, (alert_panel_x + 8, y_offset))
            y_offset += 22  # Compact spacing
        
        # Show if there are more alerts - more compact
        if len(self.weather_alerts) > 3:
            more_text = f"...+{len(self.weather_alerts) - 3} more"
            more_surface = pygame.font.SysFont(None, 16).render(more_text, True, (100, 100, 100))
            self.screen.blit(more_surface, (alert_panel_x + 8, y_offset))
            
    def _draw_stats_panel(self):
        """Draw a dedicated statistics panel."""
        # Smaller, more compact panel - standardized width
        panel_width = 320  # Standardized width for all panels
        panel_height = 180  # Reduced height to fit at bottom
        
        # Position the panel at the bottom right, with proper spacing after forecast
        panel_x = self.width - panel_width - 10
        panel_y = 600  # Adjusted to accommodate forecast panel repositioning
        
        # Create stats panel with simple background
        stats_panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (240, 248, 255), stats_panel)  # Light blue background
        pygame.draw.rect(self.screen, (0, 0, 100), stats_panel, 2)  # Blue border
        
        # Add title bar
        header_height = 30
        header_rect = pygame.Rect(panel_x, panel_y, panel_width, header_height)
        pygame.draw.rect(self.screen, (0, 0, 100), header_rect)
        
        # Title text
        title_font = pygame.font.SysFont(None, 24)
        title_text = title_font.render("Farm Stats", True, (255, 255, 255))
        self.screen.blit(title_text, (header_rect.centerx - title_text.get_width() // 2, 
                                    header_rect.y + 5))
        
        # Statistics content - simple list format
        content_y = panel_y + header_height + 10
        line_height = 22
        font = pygame.font.SysFont(None, 18)
        
        # Compact stats list
        stats = [
            f"Money: ${self.money:.0f}",
            f"Planted: {self.farm.total_planted}",
            f"Harvested: {self.farm.total_harvested}",
            f"Earned: ${self.total_earned:.0f}",
            f"Spent: ${self.total_spent:.0f}",
            f"Profit: ${self.total_earned - self.total_spent:.0f}",
        ]
        
        # Draw each stat on its own line
        for i, stat in enumerate(stats):
            if i * line_height + content_y + line_height > panel_y + panel_height - 5:
                break  # Stop if we run out of space
                
            # Choose color based on content
            if "Money:" in stat or "Profit:" in stat:
                color = (0, 150, 0) if self.money >= 0 else (150, 0, 0)
            elif "Earned:" in stat:
                color = (0, 120, 0)
            elif "Spent:" in stat:
                color = (120, 0, 0)
            else:
                color = (0, 0, 0)
            
            stat_text = font.render(stat, True, color)
            self.screen.blit(stat_text, (panel_x + 10, content_y + i * line_height))

    def _draw_money_display(self):
        """Draw a graphical money display with transaction indicators."""
        import time
        
        # Money display position (top right) - standardized width
        money_panel_width = 320  # Standardized width for all panels
        money_panel_height = 80
        money_panel_x = self.width - money_panel_width - 10
        money_panel_y = 10
        
        # Create money panel background
        money_panel = pygame.Rect(money_panel_x, money_panel_y, money_panel_width, money_panel_height)
        
        # Gradient background based on money amount
        if self.money >= 500:
            base_color = (20, 80, 20)  # Dark green for good money
        elif self.money >= 100:
            base_color = (60, 60, 20)  # Yellow-green for moderate money
        else:
            base_color = (80, 20, 20)  # Dark red for low money
            
        # Draw gradient background
        for i in range(money_panel_height):
            color = tuple(min(c + i//3, 255) for c in base_color)
            pygame.draw.line(self.screen, color, 
                          (money_panel_x, money_panel_y + i),
                          (money_panel_x + money_panel_width, money_panel_y + i))
        
        # Draw border
        border_color = (0, 255, 0) if self.money >= 0 else (255, 0, 0)
        pygame.draw.rect(self.screen, border_color, money_panel, 2)
        
        # Draw dollar sign icon
        dollar_font = pygame.font.SysFont(None, 36)
        dollar_text = dollar_font.render("$", True, (255, 255, 255))
        self.screen.blit(dollar_text, (money_panel_x + 10, money_panel_y + 10))
        
        # Draw money amount
        money_font = pygame.font.SysFont(None, 28)
        money_color = (255, 255, 255)
        money_text = money_font.render(f"{self.money:.0f}", True, money_color)
        self.screen.blit(money_text, (money_panel_x + 35, money_panel_y + 15))
        
        # Draw money bar (visual representation)
        bar_width = money_panel_width - 40
        bar_height = 8
        bar_x = money_panel_x + 10
        bar_y = money_panel_y + 45
        
        # Background bar
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        pygame.Rect(bar_x, bar_y, bar_width, bar_height))
        
        # Filled bar based on money amount (max 1000 for full bar)
        max_money_display = 1000
        fill_ratio = min(self.money / max_money_display, 1.0)
        fill_width = int(bar_width * fill_ratio)
        
        # Color based on money amount
        if fill_ratio > 0.7:
            fill_color = (0, 255, 0)  # Green
        elif fill_ratio > 0.3:
            fill_color = (255, 255, 0)  # Yellow
        else:
            fill_color = (255, 100, 0)  # Orange
            
        pygame.draw.rect(self.screen, fill_color, 
                        pygame.Rect(bar_x, bar_y, fill_width, bar_height))
        
        # Draw recent transactions
        current_time = time.time()
        y_offset = money_panel_y + 60
        
        for transaction in self.recent_transactions[-3:]:  # Show last 3 transactions
            age = current_time - transaction['timestamp']
            if age < 3.0:  # Show for 3 seconds
                alpha = int(255 * (1.0 - age / 3.0))  # Fade out over time
                
                if transaction['type'] == 'income':
                    color = (0, 255, 0)  # Green for income
                    prefix = "+"
                else:
                    color = (255, 100, 100)  # Light red for expenses
                    prefix = "-"
                
                # Create surface with alpha for fading effect
                trans_text = f"{prefix}${transaction['amount']:.0f}"
                trans_font = pygame.font.SysFont(None, 18)
                trans_surface = trans_font.render(trans_text, True, color)
                trans_surface.set_alpha(alpha)
                
                self.screen.blit(trans_surface, (money_panel_x + 10, y_offset))
                y_offset -= 15

    def _draw_profit_display(self):
        """Draw a separate profit/loss display panel."""
        # Profit display position (below money display) - standardized width
        profit_panel_width = 320  # Standardized width for all panels
        profit_panel_height = 90
        profit_panel_x = self.width - profit_panel_width - 10
        profit_panel_y = 100  # Better spacing from money panel
        
        # Calculate profit/loss
        profit = self.total_earned - self.total_spent
        
        # Create profit panel background
        profit_panel = pygame.Rect(profit_panel_x, profit_panel_y, profit_panel_width, profit_panel_height)
        
        # Gradient background based on profit
        if profit > 100:
            base_color = (0, 60, 0)  # Dark green for good profit
        elif profit > 0:
            base_color = (40, 60, 0)  # Yellow-green for small profit
        elif profit >= -50:
            base_color = (60, 40, 0)  # Orange for small loss
        else:
            base_color = (60, 0, 0)  # Dark red for big loss
            
        # Draw gradient background
        for i in range(profit_panel_height):
            color = tuple(min(c + i//4, 255) for c in base_color)
            pygame.draw.line(self.screen, color, 
                          (profit_panel_x, profit_panel_y + i),
                          (profit_panel_x + profit_panel_width, profit_panel_y + i))
        
        # Draw border
        border_color = (0, 255, 0) if profit >= 0 else (255, 0, 0)
        pygame.draw.rect(self.screen, border_color, profit_panel, 2)
        
        # Draw profit/loss icon
        icon_font = pygame.font.SysFont(None, 32)
        icon = "📈" if profit >= 0 else "📉"
        icon_text = icon_font.render(icon, True, (255, 255, 255))
        self.screen.blit(icon_text, (profit_panel_x + 10, profit_panel_y + 10))
        
        # Draw "PROFIT" or "LOSS" label
        label_font = pygame.font.SysFont(None, 20)
        label = "PROFIT" if profit >= 0 else "LOSS"
        label_color = (0, 255, 0) if profit >= 0 else (255, 100, 100)
        label_text = label_font.render(label, True, label_color)
        self.screen.blit(label_text, (profit_panel_x + 45, profit_panel_y + 15))
        
        # Draw profit amount
        amount_font = pygame.font.SysFont(None, 24)
        prefix = "+" if profit > 0 else ""
        amount_text = f"{prefix}${profit:.0f}"
        amount_color = (255, 255, 255)
        amount_surface = amount_font.render(amount_text, True, amount_color)
        self.screen.blit(amount_surface, (profit_panel_x + 10, profit_panel_y + 40))
        
        # Draw breakdown
        breakdown_font = pygame.font.SysFont(None, 16)
        earned_text = f"Earned: ${self.total_earned:.0f}"
        spent_text = f"Spent: ${self.total_spent:.0f}"
        
        earned_surface = breakdown_font.render(earned_text, True, (200, 255, 200))
        spent_surface = breakdown_font.render(spent_text, True, (255, 200, 200))
        
        self.screen.blit(earned_surface, (profit_panel_x + 10, profit_panel_y + 65))
        self.screen.blit(spent_surface, (profit_panel_x + 10, profit_panel_y + 75))

    def _draw_instructions(self):
        """Draw game instructions."""
        sidebar_width = 300
        
        # Create a background for the instructions area
        instr_area = pygame.Rect(10, 390, sidebar_width - 20, self.height - 400)
        pygame.draw.rect(self.screen, (200, 200, 200), instr_area)
        pygame.draw.rect(self.screen, (0, 0, 0), instr_area, 2)
        
        # Display title
        title_text = pygame.font.SysFont(None, 30).render("Controls:", True, (0, 0, 0))
        self.screen.blit(title_text, (instr_area.centerx - title_text.get_width() // 2, instr_area.y + 10))
        
        instructions = [
            "ESC - Exit",
            "P - Pause/Unpause",
            "SPACE - Advance one day",
            "",
            "Scrolling:",
            "Arrow Keys - Scroll farm",
            "Mouse Wheel - Scroll vertical",
            "Shift+Wheel - Scroll horizontal",
            "",
            "Tools (1-6):",
            "1-Plant, 2-Water, 3-Fertilize",
            "4-Harvest, 5-Treat, 6-Protect",
            "",
            "Click on grid tiles to use",
            "the selected tool",
            "",
            "Current Tool: " + (self.active_tool.capitalize() if self.active_tool else "None"),
            "Current Crop: " + (self.selected_crop.capitalize() if self.selected_crop else "None"),
        ]
        
        # Display status of selected farm area
        instructions.append("")
        instructions.append("Farm Size: " + str(self.farm.width) + " x " + str(self.farm.height))
        
        # Draw instructions
        y_offset = instr_area.y + 50
        for instruction in instructions:
            text = self.assets['fonts']['default'].render(instruction, True, (0, 0, 0))
            self.screen.blit(text, (instr_area.x + 15, y_offset))
            y_offset += 25
            
        # Draw statistics section with graphical elements
        self._draw_statistics(instr_area, y_offset)
        
    def _draw_statistics(self, instr_area, y_start):
        """Draw game statistics with graphical elements."""
        # Make sure we're not going outside the instructions area
        if y_start > instr_area.y + instr_area.height - 40:
            return  # Not enough space to draw statistics
            
        # Add a header with a colored background
        header_height = 25  # Slightly smaller header
        stats_header = pygame.Rect(instr_area.x, y_start, instr_area.width, header_height)
        pygame.draw.rect(self.screen, (0, 100, 0), stats_header)  # Dark green header
        
        # Add header text
        header_text = pygame.font.SysFont(None, 20).render("FARM STATISTICS", True, (255, 255, 255))
        self.screen.blit(header_text, (stats_header.centerx - header_text.get_width() // 2, 
                                      stats_header.y + (header_height - header_text.get_height()) // 2))
        
        # Starting position for statistics
        y_offset = y_start + header_height + 5  # Less space after header
        
        # Define the statistics and their associated colors and icons
        stats = [
            {
                "name": "Crops Planted", 
                "value": self.farm.total_planted,
                "color": (0, 150, 0),  # Green
                "icon_type": "rect"
            },
            {
                "name": "Crops Harvested", 
                "value": f"{self.farm.total_harvested}",
                "color": (218, 165, 32),  # Gold
                "icon_type": "circle"
            },
            {
                "name": "Water Used", 
                "value": f"{self.farm.water_used:.1f}",
                "color": (30, 144, 255),  # Blue
                "icon_type": "droplet"
            },
            {
                "name": "Fertilizer Used", 
                "value": f"{self.farm.fertilizer_used:.1f}",
                "color": (139, 69, 19),  # Brown
                "icon_type": "triangle"
            }
        ]
        
        # Organize stats in a two-column grid to save space
        for i, stat in enumerate(stats):
            # Calculate position in the grid
            row = i // 2
            col = i % 2
            
            # Set column starting positions
            col_width = instr_area.width // 2 - 10
            col_x = instr_area.x + 10 + (col * col_width)
            
            # Calculate y position
            row_height = 40  # Compact row height
            item_y = y_offset + (row * row_height)
            
            # Skip if we've run out of vertical space
            if item_y + 30 > instr_area.y + instr_area.height:
                break
            
            # Draw a small colored square icon
            icon_size = 10
            pygame.draw.rect(self.screen, stat["color"], 
                          pygame.Rect(col_x, item_y + 5, icon_size, icon_size))
            
            # Draw the stat name in smaller font
            name_font = pygame.font.SysFont(None, 14)
            name_text = name_font.render(stat["name"] + ":", True, (0, 0, 0))
            self.screen.blit(name_text, (col_x + icon_size + 5, item_y))
            
            # Draw the value below the name
            value_font = pygame.font.SysFont(None, 16)
            value_text = value_font.render(str(stat["value"]), True, stat["color"])
            self.screen.blit(value_text, (col_x + 5, item_y + 18))
            
            # Draw a mini progress bar
            bar_width = col_width - 30
            bar_height = 3
            bar_y = item_y + 28
            
            # Draw bar background
            pygame.draw.rect(self.screen, (220, 220, 220), 
                          pygame.Rect(col_x + 5, bar_y, bar_width, bar_height))
            
            # Calculate fill width
            max_values = {"Crops Planted": 100, "Crops Harvested": 100, "Water Used": 200, "Fertilizer Used": 50}
            max_val = max_values.get(stat["name"], 100)
            
            try:
                value_float = float(stat["value"])
            except ValueError:
                value_float = 0
                
            fill_width = int((value_float / max_val) * bar_width)
            fill_width = max(0, min(fill_width, bar_width))
            
            # Draw filled portion
            if fill_width > 0:
                pygame.draw.rect(self.screen, stat["color"], 
                              pygame.Rect(col_x + 5, bar_y, fill_width, bar_height))
                              
            # Draw thin border
            pygame.draw.rect(self.screen, (0, 0, 0), 
                          pygame.Rect(col_x + 5, bar_y, bar_width, bar_height), 1)

class Farm:
    """
    Represents the farm grid and its state.
    """
    
    def __init__(self, width, height):
        """
        Initialize a farm with the given dimensions.
        
        Args:
            width (int): Width of the farm grid
            height (int): Height of the farm grid
        """
        self.width = width
        self.height = height
        
        # Initialize the farm grid with empty tiles
        self.grid = [[FarmTile() for _ in range(width)] for _ in range(height)]
        
        # Farm statistics
        self.total_harvested = 0
        self.total_planted = 0
        self.water_used = 0
        self.fertilizer_used = 0
        
    def get_tile(self, x, y):
        """Get the farm tile at the given coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
        
    def plant_crop(self, x, y, crop_type):
        """
        Plant a crop at the given coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            crop_type (str): Type of crop to plant
            
        Returns:
            bool: True if planting was successful, False otherwise
        """
        tile = self.get_tile(x, y)
        if tile and not tile.crop:
            tile.crop = Crop(crop_type)
            self.total_planted += 1
            print(f"Planted {crop_type} at ({x}, {y})")
            return True
        return False
            
    def water_tile(self, x, y):
        """
        Water the tile at the given coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: True if watering was successful, False otherwise
        """
        tile = self.get_tile(x, y)
        if tile:
            before = tile.water_level
            tile.water_level = min(tile.water_level + 0.5, tile.max_water)
            self.water_used += tile.water_level - before
            
            # Set flag to show watering animation
            tile.showing_water_effect = True
            tile.water_effect_start = pygame.time.get_ticks()
            tile.water_effect_duration = 1000  # 1 second animation
            return True
        return False
            
    def fertilize_tile(self, x, y):
        """
        Apply fertilizer to the tile at the given coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            bool: True if fertilizing was successful, False otherwise
        """
        tile = self.get_tile(x, y)
        if tile:
            before = tile.nutrient_level
            tile.nutrient_level = min(tile.nutrient_level + 0.3, tile.max_nutrients)
            self.fertilizer_used += tile.nutrient_level - before
            print(f"Fertilized tile at ({x}, {y}). New nutrient level: {tile.nutrient_level:.1f}")
            return True
        return False
            
    def harvest_crop(self, x, y):
        """
        Harvest the crop at the given coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            float: Yield of the harvested crop, or 0 if no crop was harvested
        """
        tile = self.get_tile(x, y)
        if tile and tile.crop and tile.crop.is_mature():
            crop_yield = tile.crop.get_yield(tile.water_level / tile.max_water, 
                                            tile.nutrient_level / tile.max_nutrients)
            self.total_harvested += 1  # Count each harvested crop as 1, not by yield amount
            
            # Store the crop type before clearing it (for the animation)
            harvested_crop_type = tile.crop.type
            
            print(f"Harvested {harvested_crop_type} at ({x}, {y}) with yield: {crop_yield:.2f}")
            
            # Set flags to show harvest animation
            tile.showing_harvest_effect = True
            tile.harvest_effect_start = pygame.time.get_ticks()
            tile.harvested_crop_type = harvested_crop_type
            tile.harvest_yield = crop_yield
            
            # Clear the crop
            tile.crop = None
            
            return crop_yield
        return 0
        
    def treat_tile(self, x, y):
        """
        Apply treatment to a crop.
        
        Args:
            x (int): Grid x coordinate
            y (int): Grid y coordinate
            
        Returns:
            bool: True if treatment was applied, False otherwise
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.grid[y][x]
            if tile.crop:
                print(f"🏥 Treating crop at ({x}, {y})...")
                success = tile.crop.apply_treatment()
                if success:
                    print(f"🏥 Treatment successful at ({x}, {y})")
                else:
                    print(f"💊 No treatment needed at ({x}, {y}) - crop is healthy!")
                return True
            else:
                print(f"❌ No crop to treat at ({x}, {y})")
        else:
            print(f"❌ Invalid coordinates ({x}, {y})")
        return False
        
    def protect_tile(self, x, y):
        """
        Apply weather protection to a crop.
        
        Args:
            x (int): Grid x coordinate
            y (int): Grid y coordinate
            
        Returns:
            bool: True if protection was applied, False otherwise
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.grid[y][x]
            if tile.crop:
                print(f"🛡️ Protecting crop at ({x}, {y})...")
                success = tile.crop.apply_weather_protection()
                if success:
                    print(f"🛡️ Weather protection successful at ({x}, {y})")
                else:
                    print(f"🛡️ Crop at ({x}, {y}) already protected!")
                return True
            else:
                print(f"❌ No crop to protect at ({x}, {y})")
        else:
            print(f"❌ Invalid coordinates ({x}, {y})")
        return False
        
    def update(self, current_date, weather_data=None):
        """
        Update the farm state.
        
        Args:
            current_date (datetime): Current game date
            weather_data (dict): Current weather conditions
        """
        # Update each tile
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                
                # Natural water loss
                tile.water_level = max(0, tile.water_level - 0.05)
                
                # Natural nutrient loss
                tile.nutrient_level = max(0, tile.nutrient_level - 0.01)
                
                # Update crop if present
                if tile.crop:
                    # Apply weather effects if weather data is available
                    if weather_data:
                        tile.crop.process_weather_effects(
                            weather_data.get("temperature", 20),
                            weather_data.get("precipitation", 0),
                            weather_data.get("humidity", 50)
                        )
                    
                    # Grow the crop based on water and nutrients
                    water_factor = tile.water_level / tile.max_water
                    nutrient_factor = tile.nutrient_level / tile.max_nutrients
                    
                    tile.crop.grow(water_factor, nutrient_factor)
                    
        # Randomly spawn diseases and pests
        self._spawn_diseases_and_pests(current_date)
        
    def _spawn_diseases_and_pests(self, current_date):
        """Randomly spawn diseases and pests on crops - VERY RARE and selective."""
        import random
        
        # List of available diseases and pests
        diseases = ["blight", "rot", "wilt"]
        pests = ["aphids", "beetles", "caterpillars"]
        
        # EXTREMELY rare chance - only check every few days
        if current_date.day % 3 != 0:  # Only check every 3rd day
            return
        
        # Add a much longer cooldown period - no outbreaks if one happened recently
        outbreak_cooldown = 7  # At least 7 days between outbreaks (increased from 3)
        
        if not hasattr(self, 'last_outbreak_day'):
            self.last_outbreak_day = 0
        
        if hasattr(self, 'last_outbreak_day') and self.last_outbreak_day != 0:
            days_since_outbreak = abs((current_date - self.last_outbreak_day).days)
            
            if days_since_outbreak < outbreak_cooldown:
                return  # Skip outbreaks entirely during cooldown
        
        # Only allow 1 outbreak per week maximum
        # EXTREMELY low base chance
        base_outbreak_chance = 0.05  # 5% chance per check (which happens every 3 days)
        
        if random.random() > base_outbreak_chance:
            return  # Most of the time, no outbreak happens
        
        # If we get here, we'll have exactly ONE outbreak
        # Collect all healthy crops
        healthy_crops = []
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]
                if (tile.crop and 
                    not tile.crop.disease_status and 
                    not tile.crop.pest_status):
                    healthy_crops.append((x, y, tile.crop))
        
        if not healthy_crops:
            return  # No healthy crops to infect
        
        # Choose exactly ONE crop to infect
        x, y, crop = random.choice(healthy_crops)
        
        # 50/50 chance between disease and pest
        if random.random() < 0.5:
            disease = random.choice(diseases)
            crop.infect_with_disease(disease)
            print(f"⚠️ RARE {disease.capitalize()} outbreak at ({x}, {y})!")
        else:
            pest = random.choice(pests)
            crop.infest_with_pest(pest)
            print(f"🐛 RARE {pest.capitalize()} infestation at ({x}, {y})!")
        
        # Set cooldown
        self.last_outbreak_day = current_date
        print(f"Next outbreak possible in {outbreak_cooldown} days minimum.")
        
        # NO SPREADING - keep it to just this one crop
        # (Removed all spreading logic to keep outbreaks truly isolated)
                        
    def _spread_disease(self, origin_x, origin_y, disease_type):
        """Spread disease to nearby crops."""
        import random
        
        # Disease spreads to adjacent tiles with very low probability
        spread_chance = 0.05  # 5% chance to spread to each adjacent tile (reduced from 15%)
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the origin tile
                    
                new_x, new_y = origin_x + dx, origin_y + dy
                
                if (0 <= new_x < self.width and 0 <= new_y < self.height):
                    tile = self.grid[new_y][new_x]
                    if (tile.crop and not tile.crop.disease_status and 
                        random.random() < spread_chance):
                        tile.crop.infect_with_disease(disease_type)
                        print(f"  ↳ {disease_type.capitalize()} spread to ({new_x}, {new_y})")
                        
    def _spread_pest(self, origin_x, origin_y, pest_type):
        """Spread pests to nearby crops."""
        import random
        
        # Pests spread to adjacent tiles with very low probability
        spread_chance = 0.03  # 3% chance to spread to each adjacent tile (reduced from 12%)
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the origin tile
                    
                new_x, new_y = origin_x + dx, origin_y + dy
                
                if (0 <= new_x < self.width and 0 <= new_y < self.height):
                    tile = self.grid[new_y][new_x]
                    if (tile.crop and not tile.crop.pest_status and 
                        random.random() < spread_chance):
                        tile.crop.infest_with_pest(pest_type)
                        print(f"  ↳ {pest_type.capitalize()} spread to ({new_x}, {new_y})")

class FarmTile:
    """
    Represents a single tile in the farm grid.
    """
    
    def __init__(self):
        """Initialize a farm tile."""
        self.crop = None
        
        # Tile conditions
        self.water_level = 0.2  # 0.0 to 1.0 (fraction of max)
        self.max_water = 1.0
        
        self.nutrient_level = 0.2  # 0.0 to 1.0 (fraction of max)
        self.max_nutrients = 1.0
        
        # Tile quality factors
        self.soil_quality = 0.8  # 0.0 to 1.0
        self.pest_presence = 0.0  # 0.0 to 1.0 (higher is worse)
        
        # Visual effect properties
        self.showing_water_effect = False
        self.water_effect_start = 0
        self.water_effect_duration = 1000  # 1 second
        
        self.showing_harvest_effect = False
        self.harvest_effect_start = 0
        self.harvest_effect_duration = 1500  # 1.5 seconds
        self.harvested_crop_type = None
        self.harvest_yield = 0.0

class Crop:
    """
    Represents a crop that can be planted on a farm tile.
    """
    
    # Class-level crop types and their properties
    CROP_TYPES = {
        "corn": {
            "growth_rate": 0.1,
            "water_need": 0.6,
            "nutrient_need": 0.5,
            "days_to_mature": 80,
            "base_yield": 8.0,
            "min_temp": 10,    # Frost damage below this
            "max_temp": 35,    # Heat stress above this
            "drought_tolerance": 0.4,  # Lower = more sensitive to drought
            "flood_tolerance": 0.6     # Lower = more sensitive to flooding
        },
        "wheat": {
            "growth_rate": 0.12,
            "water_need": 0.4,
            "nutrient_need": 0.3,
            "days_to_mature": 70,
            "base_yield": 6.0,
            "min_temp": 5,     # More cold-tolerant
            "max_temp": 30,    # Less heat-tolerant
            "drought_tolerance": 0.7,  # More drought-tolerant
            "flood_tolerance": 0.3     # Less flood-tolerant
        },
        "tomato": {
            "growth_rate": 0.15,
            "water_need": 0.7,
            "nutrient_need": 0.6,
            "days_to_mature": 60,
            "base_yield": 10.0,
            "min_temp": 15,    # Very frost-sensitive
            "max_temp": 32,    # Moderate heat tolerance
            "drought_tolerance": 0.2,  # Very drought-sensitive
            "flood_tolerance": 0.4     # Moderate flood tolerance
        }
    }
    
    def __init__(self, crop_type="corn"):
        """
        Initialize a crop.
        
        Args:
            crop_type (str): Type of crop
        """
        self.type = crop_type
        self.growth_stage = 0.0  # 0.0 to 1.0 (0.0 is seed, 1.0 is mature)
        self.health = 1.0  # 0.0 to 1.0 (1.0 is perfect health)
        self.days_since_planted = 0
        
        # Disease and pest system
        self.disease_status = None  # None, "blight", "rot", "wilt"
        self.pest_status = None     # None, "aphids", "beetles", "caterpillars"
        self.disease_severity = 0.0  # 0.0 to 1.0
        self.pest_severity = 0.0     # 0.0 to 1.0
        self.days_infected = 0
        self.days_infested = 0
        self.treatment_applied = False
        
        # Weather stress system
        self.frost_damage = 0.0      # Accumulated frost damage
        self.drought_stress = 0.0    # Accumulated drought stress
        self.flood_damage = 0.0      # Damage from excessive water
        self.heat_stress = 0.0       # Damage from extreme heat
        self.weather_protection = False  # Whether protective measures are applied
        
        # Get crop properties from class dictionary
        if crop_type in self.CROP_TYPES:
            self.properties = self.CROP_TYPES[crop_type]
        else:
            # Default to corn if crop type is unknown
            self.properties = self.CROP_TYPES["corn"]
            
    def grow(self, water_factor, nutrient_factor):
        """
        Grow the crop based on available water and nutrients.
        
        Args:
            water_factor (float): Available water (0.0 to 1.0)
            nutrient_factor (float): Available nutrients (0.0 to 1.0)
        """
        # Calculate growth factor based on water and nutrients
        water_need = self.properties["water_need"]
        nutrient_need = self.properties["nutrient_need"]
        
        # Penalize for too little or too much water
        water_match = 1.0 - abs(water_factor - water_need)
        
        # Penalize for too little nutrients (but not too much)
        nutrient_match = min(1.0, nutrient_factor / nutrient_need)
        
        # Calculate overall growth factor
        growth_factor = self.properties["growth_rate"] * min(water_match, nutrient_match)
        
        # Update growth stage
        self.growth_stage = min(1.0, self.growth_stage + growth_factor)
        
        # Update health based on growth conditions (more lenient)
        health_factor = (water_match + nutrient_match) / 2.0
        # Less aggressive health decline - crops should stay healthier longer
        self.health = max(0.3, self.health * 0.95 + health_factor * 0.05)  # Changed from 0.9/0.1 to 0.95/0.05
        
        # Apply disease and pest damage to health (reduced damage)
        disease_damage = self.disease_severity * 0.01 if self.disease_status else 0  # Reduced from 0.02
        pest_damage = self.pest_severity * 0.008 if self.pest_status else 0          # Reduced from 0.015
        self.health = max(0.3, self.health - disease_damage - pest_damage)           # Higher minimum health
        
        # Increment days
        self.days_since_planted += 1
        
        # Progress diseases and pests
        self._update_disease_and_pests()
        
    def _update_disease_and_pests(self):
        """Update disease and pest progression."""
        # Progress existing diseases
        if self.disease_status:
            self.days_infected += 1
            # Disease gets worse over time if untreated
            if not self.treatment_applied:
                self.disease_severity = min(1.0, self.disease_severity + 0.05)
            else:
                # Treatment reduces disease severity
                self.disease_severity = max(0.0, self.disease_severity - 0.1)
                if self.disease_severity <= 0.1:
                    self.disease_status = None
                    self.days_infected = 0
                    self.treatment_applied = False
        
        # Progress existing pests
        if self.pest_status:
            self.days_infested += 1
            # Pests get worse over time if untreated
            if not self.treatment_applied:
                self.pest_severity = min(1.0, self.pest_severity + 0.03)
            else:
                # Treatment reduces pest severity
                self.pest_severity = max(0.0, self.pest_severity - 0.15)
                if self.pest_severity <= 0.1:
                    self.pest_status = None
                    self.days_infested = 0
                    self.treatment_applied = False
                    
    def infect_with_disease(self, disease_type):
        """Infect the crop with a disease."""
        if not self.disease_status:  # Only if not already diseased
            self.disease_status = disease_type
            self.disease_severity = 0.2  # Start with moderate infection
            self.days_infected = 0
            
    def infest_with_pest(self, pest_type):
        """Infest the crop with pests."""
        if not self.pest_status:  # Only if not already infested
            self.pest_status = pest_type
            self.pest_severity = 0.15  # Start with light infestation
            self.days_infested = 0
            
    def apply_treatment(self):
        """Apply treatment to cure diseases and remove pests."""
        treatment_success = False
        
        print(f"🏥 Applying treatment to crop:")
        print(f"   - Disease status: {self.disease_status}")
        print(f"   - Pest status: {self.pest_status}")
        
        # Cure diseases
        if self.disease_status:
            old_disease = self.disease_status
            self.disease_status = None
            self.disease_severity = 0.0
            self.days_infected = 0
            treatment_success = True
            print(f"✅ Disease '{old_disease}' cured!")
        
        # Remove pests
        if self.pest_status:
            old_pest = self.pest_status
            self.pest_status = None
            self.pest_severity = 0.0
            self.days_infested = 0
            treatment_success = True
            print(f"✅ Pests '{old_pest}' removed!")
        
        # Slightly boost health after successful treatment
        if treatment_success:
            old_health = self.health
            self.health = min(1.0, self.health + 0.2)  # Bigger health boost
            print(f"💊 Health improved from {old_health:.2f} to {self.health:.2f}")
        else:
            print(f"💊 No treatment needed - crop is healthy!")
        
        self.treatment_applied = True
        return treatment_success
        
    def apply_weather_protection(self):
        """Apply weather protection measures (greenhouse, frost protection, etc.)."""
        print(f"🛡️ Applying weather protection to crop:")
        print(f"   - Current protection: {self.weather_protection}")
        print(f"   - Frost damage: {self.frost_damage:.2f}")
        print(f"   - Heat stress: {self.heat_stress:.2f}")
        print(f"   - Drought stress: {self.drought_stress:.2f}")
        print(f"   - Flood damage: {self.flood_damage:.2f}")
        
        if not self.weather_protection:
            self.weather_protection = True
            # Reduce existing weather stress by 75% when protection is applied
            old_frost = self.frost_damage
            old_heat = self.heat_stress
            old_drought = self.drought_stress
            old_flood = self.flood_damage
            
            self.frost_damage *= 0.25
            self.heat_stress *= 0.25
            self.drought_stress *= 0.25
            self.flood_damage *= 0.25
            
            print(f"🛡️ Weather protection applied!")
            print(f"   - Frost damage reduced: {old_frost:.2f} → {self.frost_damage:.2f}")
            print(f"   - Heat stress reduced: {old_heat:.2f} → {self.heat_stress:.2f}")
            print(f"   - Drought stress reduced: {old_drought:.2f} → {self.drought_stress:.2f}")
            print(f"   - Flood damage reduced: {old_flood:.2f} → {self.flood_damage:.2f}")
            return True
        else:
            print(f"🛡️ Weather protection already active!")
            return False
        
    def process_weather_effects(self, temperature, precipitation, humidity):
        """
        Process weather effects on the crop.
        
        Args:
            temperature (float): Current temperature in Celsius
            precipitation (float): Current precipitation in mm
            humidity (float): Current humidity percentage
        """
        # Weather stress naturally decays over time (recovery)
        self.frost_damage = max(0, self.frost_damage - 0.02)
        self.heat_stress = max(0, self.heat_stress - 0.02)
        self.drought_stress = max(0, self.drought_stress - 0.02)
        self.flood_damage = max(0, self.flood_damage - 0.02)
        
        # Temperature stress
        min_temp = self.properties["min_temp"]
        max_temp = self.properties["max_temp"]
        
        # Frost damage (only on extreme cold)
        if temperature < min_temp - 5 and not self.weather_protection:  # Only severe frost
            frost_intensity = (min_temp - temperature) / 15.0  # Reduced severity
            self.frost_damage = min(0.5, self.frost_damage + frost_intensity * 0.03)  # Cap at 0.5
            
        # Heat stress (only on extreme heat)
        if temperature > max_temp + 5 and not self.weather_protection:  # Only severe heat
            heat_intensity = (temperature - max_temp) / 15.0  # Reduced severity
            self.heat_stress = min(0.5, self.heat_stress + heat_intensity * 0.03)  # Cap at 0.5
            
        # Drought stress (only severe drought)
        drought_tolerance = self.properties["drought_tolerance"]
        if precipitation < 1.0 and humidity < 30:  # More severe conditions needed
            drought_factor = (30 - humidity) / 30.0 * (1.0 - precipitation) / 1.0
            drought_resistance = drought_tolerance
            if drought_factor > drought_resistance:
                self.drought_stress = min(0.4, self.drought_stress + (drought_factor - drought_resistance) * 0.02)
                
        # Flood damage (only severe flooding)
        flood_tolerance = self.properties["flood_tolerance"]
        if precipitation > 40.0:  # Much higher threshold
            flood_intensity = (precipitation - 40.0) / 60.0  # Reduced severity
            if flood_intensity > flood_tolerance:
                self.flood_damage = min(0.4, self.flood_damage + (flood_intensity - flood_tolerance) * 0.04)
                
        # Apply very mild weather damage to health
        total_weather_damage = self.frost_damage + self.heat_stress + self.drought_stress + self.flood_damage
        weather_health_loss = min(total_weather_damage * 0.005, 0.05)  # Much reduced impact
        self.health = max(0.5, self.health - weather_health_loss)     # Higher minimum health (50%)
        
        # Weather protection lasts for 7 days, then degrades
        if self.weather_protection:
            if not hasattr(self, 'protection_days_left'):
                self.protection_days_left = 7  # Initialize protection duration
            else:
                self.protection_days_left -= 1
                if self.protection_days_left <= 0:
                    self.weather_protection = False
                    print(f"🛡️ Weather protection expired for {self.type}!")
                    delattr(self, 'protection_days_left')
        
    def get_weather_stress_level(self):
        """Get the overall weather stress level (0.0 to 1.0)."""
        return min(1.0, self.frost_damage + self.heat_stress + self.drought_stress + self.flood_damage)
        
    def get_dominant_weather_stress(self):
        """Get the type of weather stress affecting this crop most."""
        stresses = {
            "frost": self.frost_damage,
            "heat": self.heat_stress,
            "drought": self.drought_stress,
            "flood": self.flood_damage
        }
        if max(stresses.values()) > 0.1:
            return max(stresses, key=stresses.get)
        return None
        
    def is_severely_damaged(self):
        """Check if crop is too damaged to continue growing."""
        return self.health < 0.2 or self.disease_severity > 0.8 or self.pest_severity > 0.8
        
    def is_mature(self):
        """Check if the crop is mature and ready for harvest."""
        return self.growth_stage >= 0.95 or self.days_since_planted >= self.properties["days_to_mature"]
        
    def get_yield(self, water_factor, nutrient_factor):
        """
        Calculate the yield of the crop when harvested.
        
        Args:
            water_factor (float): Available water (0.0 to 1.0)
            nutrient_factor (float): Available nutrients (0.0 to 1.0)
            
        Returns:
            float: Yield of the crop
        """
        if not self.is_mature():
            return 0.0
            
        # Base yield from crop properties
        base_yield = self.properties["base_yield"]
        
        # Modify based on growth stage
        stage_factor = self.growth_stage
        
        # Modify based on crop health
        health_factor = self.health
        
        # Calculate final yield
        return base_yield * stage_factor * health_factor