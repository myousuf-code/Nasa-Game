# NASA Farm Navigator - User Guide

## Introduction

NASA Farm Navigator is an educational game that demonstrates how NASA satellite imagery and climate data can be applied to agricultural practices. This simulation allows players to experiment with different farming strategies while learning about sustainable agricultural practices based on real-world data.

This enhanced version includes economic management, disease systems, professional UI improvements, and robust NASA data integration to provide a comprehensive farming simulation experience.

## Getting Started

### System Requirements

- Python 3.13 or higher
- Required libraries: pygame, pandas, numpy, matplotlib, requests, netCDF4, earthdata
- Internet connection for NASA API integration
- Minimum 512MB RAM for smooth gameplay

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

The game interface consists of several standardized panels:

1. **Farm Grid**: The main play area showing your farm plots with scrolling capability
2. **Tool Selection Panel**: Buttons for selecting your current farming tool
3. **Crop Selection Panel**: Buttons for selecting crop types to plant
4. **Information Display Panel**: Shows current date, weather, and economic status
5. **Status Panel**: Displays money, protection duration, and game state
6. **Weather Alert Panel**: Compact notifications for extreme weather conditions

### Windowed Mode & Display Options

- **Default Mode**: Game starts in windowed mode for easy screenshots and multitasking
- **Fullscreen Toggle**: Press **F11** to switch between windowed and fullscreen
- **Resizable Window**: Drag window edges to adjust size in windowed mode
- **Professional Layout**: Standardized 320px panel widths for clean appearance

### Scrolling System

- **Large Farm Navigation**: Use mouse wheel or arrow keys to scroll vertically
- **Visual Scroll Bar**: Shows current position and available scroll range
- **Smooth Movement**: Responsive scrolling for farms of any size

## Controls

### Navigation & View Controls

- **Mouse Wheel**: Scroll up/down to navigate large farms
- **Arrow Keys**: Alternative scrolling method (Up/Down)
- **F11**: Toggle fullscreen/windowed mode
- **Window Resize**: Drag window edges (windowed mode only)

### Game Management

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

- **C** or click **C** button: Select Corn (90-day growth, $15 value)
- **W** or click **W** button: Select Wheat (75-day growth, $12 value)
- **T** or click **T** button: Select Tomato (60-day growth, $8 value)
## Gameplay

### Economic Management System

#### Starting Resources
- **Initial Money**: $1000 to begin your farming operation
- **Real-Time Tracking**: Money display updates immediately with transactions
- **Profit Visualization**: Watch earnings grow with successful harvests

#### Crop Economics
- **Corn**: 90-day growth cycle, $15 harvest value (highest profit, longest wait)
- **Wheat**: 75-day growth cycle, $12 harvest value (balanced option)
- **Tomato**: 60-day growth cycle, $8 harvest value (quick returns, lower profit)

#### Costs & Expenses
- **Fertilizer Application**: $2 per use (boosts growth and provides disease protection)
- **Disease Protection**: $5 per treatment (7-day immunity duration)
- **Strategic Planning**: Balance immediate costs with long-term profits

### Basic Farming Cycle

1. **Prepare**: Select a crop type to plant based on economic strategy
2. **Plant**: Use the Plant tool to place crops on soil tiles
3. **Maintain**: Use the Water and Fertilize tools to optimize growth
4. **Monitor**: Watch environmental conditions and disease threats
5. **Protect**: Apply treatments to prevent disease spread
6. **Harvest**: Collect mature crops for maximum profit

### Disease & Pest Management System

#### Disease Mechanics
- **Natural Occurrence**: Diseases appear randomly with carefully balanced frequency
- **Visual Indicators**: Infected crops appear red/withered and stop growing
- **Growth Impact**: Diseased plants cannot progress until treated
- **Spread Risk**: Untreated diseases may affect nearby crops

#### Protection System
- **Treatment Method**: Use Fertilize tool on diseased crops to apply protection
- **Duration**: Protection lasts exactly 7 game days
- **Status Display**: Protection countdown shown in information panel
- **Cost**: $5 per protection treatment
- **Prevention**: Healthy crops can be pre-treated for immunity

#### Disease Management Strategy
- **Early Detection**: Monitor crops regularly for disease symptoms
- **Quick Response**: Treat infections immediately to prevent spread
- **Preventive Care**: Consider protecting valuable crops before disease strikes
- **Economic Balance**: Weigh protection costs against potential crop losses

### Understanding Crop Growth

Each crop displays:
- A **growth bar** above the plant showing progress to maturity
- Different **visual stages** as the plant develops
- **Health indicators** based on water, nutrient levels, and disease status
- **Economic value** potential based on crop type and growth stage

### Weather and Environmental Factors

#### Real NASA Climate Integration
- **Temperature Effects**: Extreme heat or cold slows crop growth
- **Precipitation Impact**: Affects soil moisture and watering requirements
- **Seasonal Patterns**: Experience realistic weather cycles based on NASA data
- **Growth Stress**: Environmental conditions directly impact crop development

#### Weather Alert System
- **Compact Notifications**: Non-overlapping alerts for extreme conditions
- **Temperature Warnings**: Heat waves and cold snap notifications
- **Precipitation Alerts**: Heavy rain and drought condition warnings
- **Strategic Planning**: Use weather forecasts to optimize farming decisions

## NASA Data Integration

NASA Farm Navigator integrates several NASA data sources for realistic agricultural simulation:

### Climate Data (NASA POWER API)

#### Real-Time Integration
- **NASA POWER Database**: Global climate and energy resource data
- **Historical Data Mapping**: Uses 2023 historical data mapped to game dates
- **Smart Caching**: Efficient data storage with automatic retry logic
- **Rate Limiting**: Respectful API usage with proper request timing

#### Climate Parameters
The game uses NASA's Prediction of Worldwide Energy Resources (POWER) data to simulate:
- **Temperature fluctuations** (daily min/max temperatures)
- **Precipitation patterns** (rainfall amounts and timing)
- **Solar radiation** (energy available for photosynthesis)
- **Wind conditions** (affecting evaporation rates)

#### Game Impact
These factors influence:
- **Evaporation rates**: How quickly water disappears from soil
- **Optimal growing conditions**: Temperature ranges for different crops
- **Stress factors**: Environmental conditions that slow growth
- **Seasonal patterns**: Realistic agricultural cycles

### Enhanced Data Processing

#### Robust Error Handling
- **Automatic Retry**: Exponential backoff for failed API requests
- **Fallback Systems**: Default weather patterns when API unavailable
- **Error Logging**: Comprehensive tracking for troubleshooting
- **Graceful Degradation**: Game continues with simulated data if needed

#### Performance Optimization
- **Response Caching**: Store frequently requested data locally
- **Efficient Requests**: Minimize API calls while maintaining accuracy
- **Background Processing**: Non-blocking data fetching for smooth gameplay

### Satellite Imagery Integration

Satellite data influences:
- **Vegetation health assessments** (NDVI calculations)
- **Soil moisture measurements** (affecting irrigation needs)
- **Detection of environmental stressors** (disease risk factors)

### Educational Value

The enhanced integration demonstrates:
1. **Practical NASA Applications**: How space-based data informs agricultural decisions
2. **Climate-Agriculture Relationship**: Direct connection between weather and crop success
3. **Data-Driven Farming**: Modern agricultural techniques using satellite information
4. **Environmental Monitoring**: Real-time assessment of growing conditions

## Advanced Features

### User Interface Enhancements

#### Professional Layout
- **Standardized Panels**: Consistent 320px width for all UI elements
- **Clean Design**: Non-overlapping components with proper spacing
- **Visual Hierarchy**: Clear organization of information and controls
- **Responsive Design**: Adapts to different window sizes

#### Accessibility Features
- **Windowed Mode**: Perfect for documentation and screenshots
- **Scrolling Support**: Navigate large farms with ease
- **Clear Visual Feedback**: Immediate response to user actions
- **Status Indicators**: Always-visible game state information

### Seasonal Forecasting

The game includes simplified seasonal forecasts based on NASA climate models, helping players:
- **Plan planting schedules** based on expected weather patterns
- **Anticipate climate challenges** before they occur
- **Optimize crop selection** for seasonal conditions
- **Develop long-term farming strategies**

### Soil Quality Analysis

Soil quality is modeled based on:
- **Water retention capabilities** (affecting irrigation frequency)
- **Nutrient content** (influencing fertilizer needs)
- **pH levels** (impacting crop health and growth rates)
- **Environmental factors** (temperature and precipitation effects)

## Tips for Success

### Economic Strategy
- **Crop Diversification**: Plant different crops to spread risk and optimize profits
- **Timing Optimization**: Use weather forecasts to plan planting and harvesting
- **Cost Management**: Balance fertilizer and protection costs with expected returns
- **Protection Planning**: Prevent diseases rather than treating them reactively

### Gameplay Optimization
- **Monitor Regularly**: Check crops daily for disease symptoms and growth progress
- **Weather Awareness**: Adjust farming practices based on NASA climate data
- **Resource Conservation**: Use water and fertilizer efficiently to maximize profits
- **Long-term Planning**: Consider seasonal patterns for optimal crop rotation

### Interface Mastery
- **Scrolling Efficiency**: Master mouse wheel and arrow key navigation
- **Window Management**: Use windowed mode for better multitasking
- **Status Monitoring**: Keep track of protection durations and economic status
- **Visual Feedback**: Pay attention to all growth indicators and alerts

## Troubleshooting

### Performance Issues
- **Windowed Mode**: Use for better performance on slower systems
- **Pause Feature**: Use P key to pause simulation when planning strategy
- **Memory Management**: Restart game if it becomes unresponsive
- **API Connectivity**: Check internet connection for NASA data integration

### Display Problems
- **Fullscreen Issues**: Try F11 if fullscreen display looks incorrect
- **UI Overlap**: Resize window if interface elements seem cramped
- **Scrolling Problems**: Use arrow keys if mouse wheel scrolling fails
- **Package Verification**: Ensure all required Python packages are installed

### Gameplay Issues
- **Disease Management**: Remember that protection lasts exactly 7 days
- **Economic Tracking**: Monitor money display for accurate profit calculations
- **Weather Alerts**: Pay attention to compact weather notifications
- **NASA Data**: Game continues with simulated data if API is unavailable

## Further Development

This enhanced version demonstrates advanced agricultural applications of NASA data:

### Current Capabilities
- **Realistic climate modeling** using actual NASA data
- **Economic simulation** with profit/loss tracking
- **Disease management** systems reflecting real agricultural challenges
- **Professional interface** suitable for educational demonstrations

### Future Enhancements
- **Machine learning predictions** of crop yields based on historical data
- **Advanced crop varieties** with specific climate requirements
- **Market simulation** with dynamic pricing based on supply and demand
- **Multiplayer functionality** for collaborative farming experiences
- **3D visualization** for immersive agricultural education
- **Mobile platform** support for wider accessibility

### Research Applications
This simulation framework could be extended for:
- **Agricultural research** into climate change impacts
- **Educational curriculum** development for Earth science programs
- **NASA outreach** programs demonstrating practical space applications
- **Sustainability studies** exploring data-driven farming practices