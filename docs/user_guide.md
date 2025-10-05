# NASA Farm Navigator - User Guide

## Introduction

NASA Farm Navigator is an educational game that demonstrates how NASA satellite imagery and climate data can be applied to agricultural practices. This simulation allows players to experiment with different farming strategies while learning about sustainable agricultural practices based on real-world data.

## Getting Started

### System Requirements

- Python 3.13 or higher
- Required libraries: pygame, pandas, numpy, matplotlib, requests, netCDF4, earthdata

### Installation

1. Ensure Python 3.13+ is installed on your system
2. Clone or download the NASA Farm Navigator repository
3. Navigate to the game directory in a terminal
4. Install required packages:
   ```
   pip install -r requirements.txt
   ```
5. Launch the game:
   ```
   python src/main.py
   ```

## Game Interface

The game interface consists of:

1. **Farm Grid**: The main play area showing your farm plots
2. **Tool Selection**: Buttons for selecting your current tool
3. **Crop Selection**: Buttons for selecting crop types
4. **Information Display**: Shows current date and game status
5. **Instructions Panel**: Shows controls and game hints

## Controls

### Keyboard Controls

- **ESC**: Exit the game
- **P**: Pause/Unpause the simulation
- **SPACE**: Manually advance one day

### Tool Selection

Tools can be selected either by clicking the buttons or using keyboard shortcuts:

- **1** or click **P** button: Select Plant tool
- **2** or click **W** button: Select Water tool
- **3** or click **F** button: Select Fertilize tool
- **4** or click **H** button: Select Harvest tool

### Crop Selection

Crops can be selected either by clicking the buttons or using keyboard shortcuts:

- **C** or click **C** button: Select Corn
- **W** or click **W** button: Select Wheat
- **T** or click **T** button: Select Tomato

## Gameplay

### Basic Farming Cycle

1. **Prepare**: Select a crop type to plant
2. **Plant**: Use the Plant tool to place crops on soil tiles
3. **Maintain**: Use the Water and Fertilize tools to help crops grow
4. **Monitor**: Watch how environmental conditions affect crop growth
5. **Harvest**: Use the Harvest tool when crops reach maturity

### Understanding Crop Growth

Each crop displays:
- A **growth bar** above the plant showing progress to maturity
- Different **visual stages** as the plant develops
- **Health indicators** based on water and nutrient levels

### Weather and Environmental Factors

The game simulates:
- **Seasonal changes** that affect temperature and precipitation
- **Water evaporation** requiring regular irrigation
- **Nutrient depletion** requiring fertilization

## NASA Data Integration

NASA Farm Navigator integrates several NASA data sources:

### Climate Data (NASA POWER API)

The game uses NASA's Prediction of Worldwide Energy Resources (POWER) data to simulate:
- Temperature fluctuations (daily and seasonal)
- Precipitation patterns
- Solar radiation
- Wind conditions

These factors influence:
- How quickly water evaporates from soil
- Optimal growing conditions for different crops
- Risk of drought or oversaturation

### Satellite Imagery

Satellite data influences:
- Vegetation health assessments (NDVI)
- Soil moisture measurements
- Detection of environmental stressors

### Educational Value

The game demonstrates:
1. How NASA Earth science data can inform agricultural decisions
2. The relationship between climate patterns and crop yields
3. Principles of sustainable farming based on data-driven decisions

## Advanced Features

### Seasonal Forecasting

The game includes a simplified seasonal forecast based on NASA climate models, helping players plan their planting strategy.

### Soil Quality Analysis

Soil quality is modeled based on:
- Water retention capabilities
- Nutrient content
- pH levels

## Tips for Success

- Different crops have different water and nutrient requirements
- Check weather forecasts to time your planting optimally
- Monitor soil moisture regularly
- Harvest crops when they reach maturity for maximum yield
- Experiment with different strategies to find optimal patterns

## Troubleshooting

If you encounter any issues:

- Ensure all required Python packages are installed
- Verify your Python version is 3.13 or higher
- Check the console for error messages
- Restart the game if it becomes unresponsive

## Further Development

This game is a simplified model. Real agricultural applications of NASA data include:
- More complex climate models
- Advanced crop growth simulations
- Integration with multiple satellite data sources
- Machine learning predictions of crop yields