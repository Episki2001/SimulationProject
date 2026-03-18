# CSC512C-Gamboa-Garcia-Simulation-Project
Repository for CSC512C Simulation Project

## Authors
- **Kimberly Claire H. Gamboa**
- **Andre Emmanuel S. Garcia**

## Description
Cache simulation project implementing direct-mapped and set-associative cache architectures with visualization and animation capabilities.

## Features
- **Direct-Mapped Cache**: Simulate direct-mapped cache with configurable parameters
- **8-Way Set Associative Cache**: Simulate 8-way set associative cache with LRU replacement
- **Configurable Timing**: Set cache access time and memory access time in nanoseconds
- **Test Patterns**: Sequential, mid-repeat, random, and custom access patterns
- **Animation**: Step-by-step visualization of cache operations
- **Performance Metrics**: Hit rate, miss rate, average access time, and total access time
- **Web Interface**: Modern, interactive UI built with NiceGUI

## Prerequisites
- **Python 3.14 or higher**
- **Poetry** (Python dependency management tool)

### Installing Poetry
If you don't have Poetry installed, run:

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -
```

## Installation & Deployment

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/CSC512C-Gamboa-Garcia-Simulation-Project.git
cd CSC512C-Gamboa-Garcia-Simulation-Project
```

### 2. Install Dependencies
Poetry will automatically create a virtual environment and install all dependencies:

```bash
poetry install
```

### 3. Run the Application
Start the web server:

```bash
poetry run python main.py
```

The application will start and be accessible at:
- **Local**: http://localhost:8080
- **Network**: The terminal will display the network URL

### 4. Access the Web Interface
Open your browser and navigate to:
```
http://localhost:8080
```

## Usage

### Creating a Simulation
1. Navigate to the **Simulations** page
2. Fill in the simulation parameters:
   - **Simulation Name**: Descriptive name for your simulation
   - **Simulation Type**: Direct Mapped or 8-Way Set Associative + LRU
   - **Cache Blocks**: Number of cache blocks (power of 2, min 4)
   - **Block Size**: Block size in words (power of 2, min 2)
   - **Cache Access Time**: Time per cache access in nanoseconds
   - **Memory Access Time**: Time per word fetch from memory in nanoseconds
   - **Test Pattern**: Choose from sequential, mid_repeat, random, or custom
3. Click **Create Simulation**

### Viewing Results
After creating a simulation, you can:
- View **performance metrics** (hits, misses, hit rate, miss rate)
- View **timing information** (miss penalty, average access time, total access time)
- Watch **cache animation** showing step-by-step cache operations
- Inspect **final cache memory** state

## Project Structure
```
CSC512C-Gamboa-Garcia-Simulation-Project/
├── main.py                    # Application entry point
├── pyproject.toml            # Poetry configuration and dependencies
├── README.md                 # This file
├── backend/
│   ├── data.py              # Data models and persistence
│   └── simulation.py        # Cache simulation engine
└── components/
    ├── navbar.py            # Navigation bar component
    ├── hero.py              # Hero section component
    ├── footer.py            # Footer component
    └── stats_card.py        # Statistics card component
```

## Configuration
The application uses the following default configurations:
- **Storage**: Browser localStorage (per-user, persistent)
- **Memory Space**: 1024 blocks (0-1023) - Fixed per CSC512C spec
- **Cache Access Time**: 1 ns/block (configurable)
- **Memory Access Time**: 10 ns/word (configurable)
- **Read Policy**: Non load-through (fixed)
- **Port**: 8080 (configurable in main.py)

### Data Storage
- Each user's simulations are stored in their **browser's localStorage**
- Data persists across browser sessions but is isolated per user/browser
- No server-side storage or shared data between users
- Initial state: **empty** (no seed data)

## Timing Formulas
- **Hit Time**: cache_access_time
- **Miss Penalty**: cache_access_time + (block_size × memory_access_time) + cache_access_time
- **Average Memory Access Time (AMAT)**: hit_time + miss_rate × miss_penalty
- **Total Access Time**: (hits × hit_time) + (misses × miss_penalty)

## Development

### Running in Development Mode
The application runs with hot-reload enabled by default:
```bash
poetry run python main.py
```

### Clearing Browser Storage
To reset all simulation data:
1. Open browser Developer Tools (F12)
2. Navigate to **Application** → **Local Storage**
3. Find `cache_simulations` key and delete it
4. Or clear all localStorage for the site

## Troubleshooting

### Port Already in Use
If port 8080 is already in use, you can:
1. Stop the conflicting process
2. Change the port in `main.py`:
```python
ui.run(
    title="CSC512C Simulation Project",
    favicon="🔬",
    port=8081,  # Change this
    reload=True,
)
```

### Dependencies Not Installing
Try updating Poetry and reinstalling:
```bash
poetry self update
poetry env remove python
poetry install
```

## License
This project is developed for academic purposes as part of CSC512C coursework.

## Support
For issues or questions, please contact:
- Kimberly Claire H. Gamboa: kimberly_gamboa@dlsu.edu.ph
- Andre Emmanuel S. Garcia: andre_emmanuel_garcia@dlsu.edu.ph
