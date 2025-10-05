# NASA Farm Navigator

🌾 **An Educational Agricultural Simulation Using Real NASA Data** 🌾

NASA Farm Navigator is a comprehensive farming simulation game that integrates real NASA POWER API climate data to demonstrate the practical application of Earth science data in agriculture. Experience the challenges of modern farming while learning about sustainable agricultural practices based on actual satellite and climate data.

## 🚀 What's New in This Version

### Enhanced Gameplay Mechanics
- **Disease & Pest System**: Realistic crop diseases and pests with 7-day protection duration after treatment
- **Economic Management**: Track profits with visual money display and economic decision-making
- **Weather Stress Effects**: Crops respond dynamically to temperature extremes and precipitation
- **Balanced Challenge**: Carefully tuned difficulty with proper disease frequency and recovery mechanics

### Professional UI & User Experience
- **Windowed Mode**: Resizable window with F11 fullscreen toggle - perfect for screenshots and presentations
- **Scrolling System**: Navigate large farms with mouse wheel and arrow keys, complete with visual scroll bars
- **Standardized Panels**: Clean, consistent 320px panel widths for professional appearance
- **Compact Weather Alerts**: Non-overlapping weather notifications with proper positioning
- **Visual Feedback**: Comprehensive displays for protection duration, profit tracking, and game state

### Robust NASA Data Integration
- **Real-Time Climate Data**: NASA POWER API integration with historical data mapping
- **Smart Caching**: Efficient data caching with retry logic and rate limiting
- **Error Handling**: Robust fallback systems for API failures
- **Realistic Weather**: Temperature, precipitation, and environmental factors affect crop growth

## 🎮 Key Features

### Core Gameplay
- **Interactive Farm Management**: Plant, water, fertilize, and harvest crops with intuitive tools
- **Multiple Crop Types**: Corn, wheat, and tomatoes with unique growth characteristics
- **Seasonal Farming**: Experience realistic seasonal changes affecting crop growth
- **Resource Management**: Balance water, fertilizer, and economic resources

### Educational Value
- **Real NASA Data**: Learn how satellite data informs agricultural decisions
- **Climate Impact**: Understand how weather patterns affect farming success
- **Sustainable Practices**: Discover data-driven farming techniques
- **Earth Science Applications**: See practical uses of space-based Earth observation

### Technical Features
- **NASA POWER API**: Real climate data from NASA's global energy resource database
- **Advanced Simulation**: Sophisticated crop growth models based on environmental factors
- **Cross-Platform**: Runs on Windows, macOS, and Linux
- **Professional Graphics**: Polished Pygame-based interface with smooth animations

## 🛠️ Installation

### System Requirements
- **Python**: 3.13 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for NASA data integration
- **Memory**: Minimum 512MB RAM
- **Storage**: 50MB free space

### Quick Setup
1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd "Nasa Game"
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Game**
   ```bash
   python src/main.py
   ```

### Dependencies
- `pygame` - Game engine and graphics
- `requests` - NASA API communication
- `numpy` - Numerical computations
- `pandas` - Data processing
- `matplotlib` - Data visualization (future features)

## 🎯 Quick Start

### Basic Controls
- **Mouse**: Click to interact with farm plots and UI elements
- **Scroll Wheel**: Navigate large farms vertically
- **Arrow Keys**: Alternative scrolling method
- **F11**: Toggle fullscreen/windowed mode
- **ESC**: Exit game
- **P**: Pause/unpause simulation
- **SPACE**: Advance one day manually

### First Steps
1. **Select a Tool**: Choose Plant (1), Water (2), Fertilize (3), or Harvest (4)
2. **Choose a Crop**: Select Corn (C), Wheat (W), or Tomato (T)
3. **Plant Seeds**: Click on empty soil plots to plant
4. **Monitor Growth**: Watch progress bars and environmental conditions
5. **Maintain Crops**: Water and fertilize as needed
6. **Harvest**: Collect mature crops for profit

## 📚 Documentation

- **[Quick Start Guide](docs/quick_start.md)**: Get playing immediately
- **[User Guide](docs/user_guide.md)**: Comprehensive gameplay instructions
- **[NASA Data Integration](docs/nasa_data_integration.md)**: Technical details about data sources

## 🌍 Educational Applications

### For Students
- **Earth Science**: Learn about satellite data and climate monitoring
- **Agriculture**: Understand modern farming challenges and solutions
- **Data Science**: See real-world applications of data analysis
- **Environmental Science**: Explore climate impact on food production

### For Educators
- **Interactive Learning**: Engaging way to teach Earth science concepts
- **Real Data**: Demonstrate practical NASA applications
- **STEM Integration**: Combine science, technology, and agriculture
- **Customizable**: Adapt scenarios for different learning levels

## 🔬 NASA Data Sources

- **NASA POWER API**: Global climate and energy data
- **Temperature Data**: Daily min/max temperatures
- **Precipitation**: Rainfall and weather patterns
- **Solar Radiation**: Energy availability for plant growth
- **Historical Climate**: Multi-year datasets for realistic simulation

## 🚀 Future Enhancements

- **Multiplayer Support**: Collaborative farming experiences
- **Advanced Crops**: Additional plant varieties and breeding
- **Market Simulation**: Dynamic pricing and trade systems
- **3D Visualization**: Enhanced graphics and perspective views
- **Mobile Version**: Tablet and smartphone compatibility

## 🤝 Contributing

We welcome contributions! This project demonstrates the intersection of space technology and agriculture, perfect for:
- Earth science students
- Agricultural researchers
- Game developers interested in educational applications
- NASA data enthusiasts

## 📄 License

This project is developed for educational purposes, demonstrating practical applications of NASA Earth science data in agricultural decision-making.

---

**Experience farming like never before with real NASA data!** 🛰️🌱