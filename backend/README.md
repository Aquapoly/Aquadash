# Aquadash - Backend (FastAPI)

FastAPI backend for monitoring and controlling a hydroponics system.  
**Developer Documentation** - Not for production use.

---

## 🚀 Quick Start

### Prerequisites

#### 1. Software

**🐧 Linux:**

```bash
sudo apt update && sudo apt install python3 git
```

**🪟 Windows:**

- [Python 3.8+](https://apps.microsoft.com/detail/9PNRBTZXMB4Z?hl=en-us&gl=CA&ocid=pdpshare)
- [Git Bash](https://git-scm.com/install/windows)

**Docker (optional):**

- **Linux:** `sudo apt install docker.io docker-compose-plugin`
- **Windows:** [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) with WSL2

It is recommended that you use Docker mode for development and production. It is also recommended that you restart your computer after having installed docker.

_Note: You may need to [add your user to the `docker` group](https://docs.docker.com/engine/install/linux-postinstall/) to run docker commands without sudo._

#### 2. Python dependencies

The `run.py` script needs the `python-dotenv` package to load environment variables from the `.env` file. Install it globally for your user on the host system:

```bash
pip install python-dotenv
```

---

## 📷 Step 1: Device Services

### Camera Daemon

Whether you want camera functionality or not, install the camera daemon on the **host system** first. It is required for Docker mode, and will be used for native mode if you want to use the camera. It is an intermediary between the camera and the backend for secure access to your devices or lackthereof.

#### Installation

```bash
cd deployment/devices/camera
sudo ./install.sh
```

#### Start the service

```bash
sudo systemctl start camera-daemon.service
```

#### Create a camera

Replace `camera0` with whatever camera name suits you.

```bash
sudo camera-ctl create camera0 /dev/video0
sudo camera-ctl list  # Verify
```

#### Documentation

See [`deployment/devices/camera/README.md`](deployment/devices/camera/README.md) for more information on the camera daemon and camera-ctl.

---

## 🛠 Step 2: Setup

### Configuration

1. **Copy environment template:**

```bash
cp .env.example .env
```

2. **Edit `.env` to configure:**
   - `DOCKER=1` for Docker mode, `DOCKER=0` for native Python
   - `CAMERA_NAME=camera0` (or any other name you want to use, such as `front` or `back`, etc.)
   - `HOST_ENV_GID=...`

To obtain the correct value of `HOST_ENV_GID`, execute this command, after having started the camera daemon:

```bash
sudo camera-ctl gid  # Will print the required value for HOST_ENV_GID to stdout
```

### 🐘 Native PostgreSQL + Python Setup

**Only if `DOCKER=0` in `.env`**

Your only manual steps are installing PostgreSQL and creating the database. The rest is handled by the script.

**🐧 Linux:**

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'aquapoly';"
sudo -u postgres createdb aquapoly
```

**🪟 Windows:**

- Install [pgAdmin 4](https://www.pgadmin.org/download/pgadmin-4-windows/)
- Set `postgres` user password to `aquapoly`
- Create `aquapoly` database

### Docker Setup

**Only if `DOCKER=1` in `.env`**

Only building the containers is required. Everything else is handled by the `run.py` script.

**Build containers:**

```bash
docker compose build
```

---

## ▶️ Step 3: Run

The `run.py` script is cross-platform and will acquire your mode from your previously-configured `.env` file to run the appropriate backend.

You can run it directly with:

```bash
./run
./run -d        # Docker: detached mode
./run --reload  # Native: auto-reload on changes
```

The script automatically:

- Loads configuration from `.env`
- Detects Docker vs Native mode
- Creates virtual environment and installs dependencies (Native mode, first run)
- Gets host-dev GID for camera access (Docker mode)
- Starts the appropriate backend

In docker mode, additional arguments get passed to `docker compose up`.

In native mode, additional arguments get passed to `uvicorn`.

_Note: You can also invoke python explicitly as `python run <args>`._

---

## 🔗 Access

- **API Documentation:** http://localhost:8000/docs
- **Camera Endpoint:** http://localhost:8000/picture

---

## 🧪 Testing

### Run Tests in Docker

```bash
docker compose up -d
docker exec -it <container_name> /bin/sh
cd /usr/src/app
pytest                          # All tests
pytest tests/test_example.py    # Specific test
pytest --cov-report=html        # Coverage report
```

### Run Tests Natively

```bash
source .venv/bin/activate
pytest
```

---

## 📚 Developer Resources

| Technology | Documentation                       |
| ---------- | ----------------------------------- |
| FastAPI    | https://fastapi.tiangolo.com        |
| SQLAlchemy | https://www.sqlalchemy.org          |
| Pydantic   | https://pydantic-docs.helpmanual.io |
| PostgreSQL | https://www.postgresql.org/docs     |
| Docker     | https://www.docker.com/             |
| Pytest     | https://docs.pytest.org/en/stable/  |

---

## 💡 Troubleshooting

**PostgreSQL connection errors:**

- Verify password is `aquapoly`
- Check service is running: `sudo systemctl status postgresql`

**Docker port already in use:**

- PostgreSQL may be running natively
- Or a detached container is already running: `docker ps`

**Camera not available:**

- Ensure camera daemon is running: `sudo systemctl status camera-daemon.service`
- Verify camera exists: `sudo camera-ctl list`
- Check CAMERA_NAME in `.env` matches camera name

**Windows PowerShell issues:**

- Use Git Bash for shell commands

---

© 2025 Aquadash — Released under the GNU License
