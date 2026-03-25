# CSC512C-Gamboa-Garcia-Simulation-Project
Repository for CSC512C Simulation Project

## Authors
- **Kimberly Klaire H. Gamboa**
- **Andre Emmanuel S. Garcia**

## Description
Cache simulation project implementing direct-mapped and set-associative cache architectures with visualization and animation capabilities.

## Tech Stack
- **Backend**: Python 3.8+
- **Web Framework**: NiceGUI (FastAPI-based)
- **Dependency Management**: Poetry
- **UI Components**: Tailwind CSS (via NiceGUI)
- **Storage**: Browser localStorage (client-side persistence)
- **Architecture**: Component-based page routing

## Features
- **Direct-Mapped Cache**: Simulate direct-mapped cache with configurable parameters
- **8-Way Set Associative Cache**: Simulate 8-way set associative cache with LRU replacement
- **Configurable Timing**: Set cache access time and memory access time in nanoseconds
- **Test Patterns**: Sequential, mid-repeat, random, and custom access patterns
- **Animation**: Step-by-step visualization of cache operations
- **Performance Metrics**: Hit rate, miss rate, average access time, and total access time
- **Web Interface**: Modern, interactive UI built with NiceGUI

## Prerequisites
- **Python 3.8 or higher**
- **Poetry** (Python dependency management tool)

### Installing Poetry
If you don't have Poetry installed, run:

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -
```

## Local Setup & Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/Episki2001/SimulationProject.git
cd SimulationProject
```

### Step 2: Install Poetry (if not already installed)
Poetry is required for dependency management. Install it using one of the following methods:

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**macOS/Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

After installation, restart your terminal or add Poetry to your PATH.

### Step 3: Install Project Dependencies
Poetry will automatically create a virtual environment and install all required dependencies:

```bash
poetry install
```

This will:
- Create a virtual environment for the project
- Install NiceGUI and all required packages
- Set up the development environment

### Step 4: Run the Application
Start the local development server:

```bash
poetry run python main.py
```

You should see output similar to:
```
NiceGUI ready to go on http://localhost:8080
```

### Step 5: Access the Application
Open your web browser and navigate to:
```
http://localhost:8080
```

The application will be running with hot-reload enabled, so any code changes will automatically refresh the browser.

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
SimulationProject/
├── main.py                    # Application entry point
├── pyproject.toml            # Poetry configuration and dependencies
├── README.md                 # This file
├── backend/
│   ├── __init__.py
│   ├── data.py              # Data models and localStorage persistence
│   └── simulation.py        # Cache simulation engine (direct-mapped & set-associative)
├── components/
│   ├── __init__.py
│   ├── navbar.py            # Navigation bar component
│   ├── footer.py            # Footer component
│   ├── links.py             # Links section component
│   ├── author_card.py       # Author information card
│   ├── simulation_card.py   # Simulation display card
│   ├── simulation_form.py   # Simulation creation form
│   └── stats_card.py        # Statistics card component
└── pages/
    ├── __init__.py
    ├── home.py              # Home/landing page
    ├── about.py             # About page with project info
    └── simulations.py       # Simulations page (create & view)
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

## Deployment

### Docker Deployment

The project includes a Dockerfile for easy containerization and deployment.

#### Build Docker Image
```bash
docker build -t simulation-project .
```

#### Run Docker Container
```bash
# Run in foreground
docker run -p 8080:8080 simulation-project

# Run in detached mode
docker run -d -p 8080:8080 --name simulation-app simulation-project
```

Access the application at `http://localhost:8080`

#### Stop Docker Container
```bash
docker stop simulation-app
docker rm simulation-app
```

### Render Deployment

This application can be deployed to [Render](https://render.com) using either Docker or native Python.

#### Option 1: Deploy with Docker (Recommended)

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push
   ```

2. **In Render Dashboard:**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository: `Episki2001/SimulationProject`
   - Configure the service:
     - **Environment**: Docker
     - **Region**: Choose your preferred region
     - **Plan**: Free or paid tier
   - Click **"Create Web Service"**

Render will automatically use your Dockerfile to build and deploy the application.

#### Option 2: Deploy with Native Python

The project includes a `render.yaml` configuration file for blueprint deployment.

1. **Push your code to GitHub** (same as above)

2. **In Render Dashboard:**
   - Click **"New +"** → **"Blueprint"**
   - Connect your repository
   - Render will detect `render.yaml` and configure automatically

#### Environment Variables (Optional)

You can add these environment variables in Render dashboard for customization:
- `STORAGE_SECRET`: Custom secret key for session storage
- `PORT`: Port number (default: 8080)
- `HOST`: Host address (default: 0.0.0.0)
- `RELOAD`: Enable hot reload (default: false for production)

#### Testing Before Deployment

Test the Docker setup locally before deploying:
```bash
docker build -t simulation-project .
docker run -p 8080:8080 simulation-project
```

Visit `http://localhost:8080` to verify it works correctly.

## License
This project is developed for academic purposes as part of CSC512C coursework.

## Support
For issues or questions, please contact:
- Kimberly Klaire H. Gamboa: kimberly_gamboa@dlsu.edu.ph
- Andre Emmanuel S. Garcia: andre_emmanuel_garcia@dlsu.edu.ph
