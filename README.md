# CSC512C-Gamboa-Garcia-Simulation-Project

Cache simulation project implementing direct-mapped and set-associative cache architectures with visualization and animation capabilities.

## Authors
- **Kimberly Klaire H. Gamboa** - kimberly_gamboa@dlsu.edu.ph
- **Andre Emmanuel S. Garcia** - andre_emmanuel_garcia@dlsu.edu.ph

---

## Features
- **Direct-Mapped Cache**: Simulate direct-mapped cache with configurable parameters
- **8-Way Set Associative Cache**: Simulate 8-way set associative cache with LRU replacement
- **Configurable Timing**: Set cache access time and memory access time in nanoseconds
- **Test Patterns**: Sequential, mid-repeat, random, and custom access patterns
- **Step-by-Step Animation**: Interactive visualization of cache operations with playback controls
- **Performance Metrics**: Hit rate, miss rate, average access time, and total access time
- **Export Results**: Download trace logs as text files
- **Modern Web Interface**: Built with NiceGUI and Tailwind CSS
- **Persistent Storage**: Browser localStorage for per-user simulation history

---

## Tech Stack
- **Backend**: Python 3.14+
- **Web Framework**: NiceGUI (FastAPI-based)
- **Dependency Management**: Poetry
- **UI Components**: Tailwind CSS (via NiceGUI)
- **Storage**: Browser localStorage (client-side)
- **Deployment**: Docker, Render

---

## Quick Start

### Prerequisites
- **Python 3.8 or higher**
- **Poetry** (Python dependency management tool)

### Installation

**1. Clone the Repository**
```bash
git clone https://github.com/Episki2001/SimulationProject.git
cd SimulationProject
```

**2. Install Poetry** (if not already installed)

Windows (PowerShell):
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

macOS/Linux:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

After installation, restart your terminal or add Poetry to your PATH.

**3. Install Dependencies**
```bash
poetry install
```

**4. Run the Application**
```bash
poetry run python main.py
```

**5. Access the Application**

Open your browser and navigate to: **http://localhost:8080**

---

## Usage

### Creating a Simulation

1. Navigate to the **Simulations** page
2. Fill in the simulation parameters:
   - **Simulation Name**: Descriptive name for your simulation (auto-generated if empty)
   - **Simulation Type**: Direct Mapped or 8-Way Set Associative + LRU
   - **Cache Blocks**: Number of cache blocks (power of 2, minimum 4)
   - **Block Size**: Block size in words (power of 2, minimum 2)
   - **Cache Access Time**: Time per cache access in nanoseconds (1-1000 ns)
   - **Memory Access Time**: Time per word fetch from memory in nanoseconds (1-1000 ns)
   - **Test Pattern**: Choose from:
     - `sequential` - Sequential access pattern (4 × cache_blocks accesses)
     - `mid_repeat` - Mid-repeat pattern
     - `random` - Random access pattern (configurable length)
     - `custom` - Custom comma-separated block numbers (0-1023)
3. Click **Create Simulation**

### Viewing Results

After creating a simulation, you can:
- **Performance Metrics**: View hits, misses, hit rate, and miss rate
- **Timing Information**: Miss penalty, average access time, total access time
- **Trace Log**: Step-by-step text log of cache operations (downloadable)
- **Cache Animation**: Interactive playback with speed controls (0.25x to 2x)
- **Final Cache State**: Inspect the final cache memory contents

---

## Project Structure

```
SimulationProject/
├── main.py                    # Application entry point
├── pyproject.toml            # Poetry dependencies
├── Dockerfile                # Docker configuration
├── render.yaml               # Render deployment config
├── README.md                 # Documentation
├── backend/
│   ├── data.py              # Data models & localStorage
│   └── simulation.py        # Cache simulation engine
├── components/
│   ├── navbar.py            # Navigation bar
│   ├── footer.py            # Footer
│   ├── author_card.py       # Author information
│   ├── simulation_card.py   # Simulation display & animation
│   ├── simulation_form.py   # Simulation creation form
│   └── stats_card.py        # Statistics display
└── pages/
    ├── home.py              # Landing page
    ├── about.py             # About page
    └── simulations.py       # Simulations page
```

---

## Configuration

### Application Settings

- **Storage**: Browser localStorage (per-user, persistent)
- **Memory Space**: 1024 blocks (0-1023) - Fixed per CSC512C spec
- **Read Policy**: Non load-through (fixed)
- **Port**: 8080 (configurable via environment variable)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8080` | Server port |
| `RELOAD` | `false` | Hot reload (set `true` for development) |
| `STORAGE_SECRET` | (auto) | Secret key for session storage |
| `ANIMATION_MAX_SPEED` | `2` | Maximum animation speed (2, 4, 8, 16) |

---

## Development

### Running in Development Mode

```bash
poetry run python main.py
```

The application runs with hot-reload enabled by default in local mode.

### Clearing Browser Storage

To reset all simulation data:
1. Open browser Developer Tools (F12)
2. Navigate to **Application** → **Local Storage**
3. Find `cache_simulations` key and delete it

---

## Deployment

### Docker Deployment

**Build and Run Locally:**
```bash
docker build -t simulation-project .
docker run -p 8080:8080 simulation-project
```

**With Custom Configuration:**
```bash
docker run -p 8080:8080 -e ANIMATION_MAX_SPEED=4 simulation-project
```

**Stop Container:**
```bash
docker stop simulation-app
docker rm simulation-app
```

### Render Deployment

#### Option 1: Docker (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push
   ```

2. **In Render Dashboard:**
   - Click **"New +"** → **"Web Service"**
   - Connect repository: `Episki2001/SimulationProject`
   - **Environment**: Docker
   - **Region**: Choose your preferred region
   - Click **"Create Web Service"**

#### Option 2: Native Python

1. **Push to GitHub** (same as above)

2. **In Render Dashboard:**
   - Click **"New +"** → **"Blueprint"**
   - Connect your repository
   - Render will detect `render.yaml` automatically

#### Configure Environment Variables (Optional)

In Render dashboard, add any of these variables:
- `STORAGE_SECRET` - Custom secret key
- `ANIMATION_MAX_SPEED` - Max playback speed (2, 4, 8, 16)
- `PORT`, `HOST`, `RELOAD` - Server configuration

---

## Troubleshooting

### Port Already in Use

Change the port in `main.py`:
```python
ui.run(
    title="CSC512C Simulation Project",
    favicon="🔬",
    port=8081,  # Change this
    reload=True,
)
```

Or set via environment variable:
```bash
PORT=8081 poetry run python main.py
```

### Dependencies Not Installing

```bash
poetry self update
poetry env remove python
poetry install
```

### Animation Performance Issues

Lower the maximum speed by setting `ANIMATION_MAX_SPEED=2` in your environment.

---

## License

This project is developed for academic purposes as part of CSC512C coursework at De La Salle University.

---

## Support

For issues or questions, please contact:
- **Kimberly Klaire H. Gamboa**: kimberly_gamboa@dlsu.edu.ph
- **Andre Emmanuel S. Garcia**: andre_emmanuel_garcia@dlsu.edu.ph
