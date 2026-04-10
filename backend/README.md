# Aquadash - Backend (FastAPI)

FastAPI backend for monitoring and controlling a hydroponics system.  
**Developer Documentation** - Not for production use.

---

## 🚀 Quick Start

### Prerequisites

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

_Note: It is possible you may need to [add your user to the Docker group](https://docs.docker.com/engine/install/linux-postinstall/) to run Docker commands without sudo._

---

## 🛠 Step 1: Setup

### Configuration

1. **Copy environment template:**

```bash
cp .env.example .env
```

2. **Configure `.env`:**

Minimally, you must set:

- `DOCKER=1` for Docker mode, `DOCKER=0` for native Python

If you want to use the camera, you will also have to set these:

- `CAMERA_NAME=camera0` (any name you like, such as `front` or `top`, etc.)
- `CAMERA_DEVICE=/dev/video0` (usually)

### 🐘 Native PostgreSQL + Python Setup

**Only if `DOCKER=0` in `.env`**

Your only manual steps are installing PostgreSQL and creating the database. The rest is handled by the `run` script.

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

The first time you use `run` ([step 3](#️-step-3-run)), pass it the `--build` option.

---

## 📷 Step 2: Camera Daemon (Optional)

A camera daemon is necessary on the host if you want to wire a camera into the system. You must install it on the host.

### Installation

```bash
sudo ./devices/camera/scripts/install.sh
```

### Documentation

For a quickstart, you do not have to interact further with the camera daemon.

However, it is possible to have finer control over the daemon and to issue commands to it. You can consult [`devices/camera/README.md`](devices/camera/README.md) for more information on the camera daemon and camera-ctl utilities.

---

## ▶️ Step 3: Run

You can run a single instance of the Aquadash backend via the `run` script:

```bash
./run app [--build] [--native] # Spin up the app only
./run cam [--build] [--native] # Spin up the camera block
./run [--build]     [--native] # Spin up the app & camera block
```

If you pass the `--build` flag, all involved containers will be rebuilt.

Pass the `--native` flag if you are not launching the containerized app.

The script automatically:

- Loads configuration from `.env`
- Starts the appropriate backend containers

### Hot Reload (DEV mode)

If you set `DEV=1` in `.env`, `./run` will include `docker-compose.dev.yml` and the backend will run with hot reload.

For the camera, it also:

- Determnines host-dev GID for camera access
- Launches the host daemon and creates a logical camera

Note that for the `cam` command, you will be required to enter credentials in order for the script to be able to use `systemctl` and `camera-ctl`.

### Advanced

If you want finer control or if you want to run multiple instances of Aquadash at once, you will need to [launch and control the camera daemon](devices/camera/README.md), and you will need to provide the relevant environment variables to `docker compose` yourself.

---

## 🛑 Step 4: Stop

You can use the `kill` script to take down your instance of the Aquadash backend:

```bash
./kill app # Kill the app
./kill cam # Kill the camera block
./kill     # Kill the app & camera block
```

Again, for the `cam` command, your credentials will be asked, this time in order to user `system-ctl` only.

### Advanced

If you want to finer control over multiple instances of Aquadash, or if you do not want to kill the camera daemon, for example, you would do well to `docker compose down` manually or with a different custom script, and to [control the camera daemon yourself](devices/camera/README.md).

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
| systemd    | https://systemd.io/                 |

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
- Check `CAMERA_NAME` in `.env` matches camera name
- Check `CAMERA_DEVICE` in `.env` matches camera device path
- (Windows) Make sure your camera is exposed to WSL via usbipd

**Windows PowerShell issues:**

- Use Git Bash for shell commands

---

© 2025 Aquadash — Released under the GNU License
