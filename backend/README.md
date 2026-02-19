# Aquadash - Backend (FastAPI)

FastAPI backend for monitoring and controlling a hydroponics system.  
**Developer Documentation** - Not for production use.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git (Recommended: Git Bash for Windows users)

---

## 🛠 Development Setup

### 1. Virtual Environment

```bash
# Create
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.\.venv\Scripts\activate
```

*VS Code Tip*:  
`Ctrl+Shift+P` → `Python: Select Interpreter` → Enter path to `.venv/Scripts/python.exe`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🗄 Database Configuration

### Linux
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql

# Set password (aquapoly)
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'aquapoly';"

# Create database
sudo -u postgres createdb aquapoly
```

### Windows
1. Download [PostgreSQL](https://www.postgresql.org/download/windows/)
2. Use pgAdmin4 to:
   - Set password for `postgres` user (aquapoly)
   - Create `aquapoly` database

---

## ⚡ Running the Server

```bash
uvicorn src.main:app --reload
```

Access API docs:  
🔗 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐋 Docker Setup (Optional)

```bash
# Camera control
export ENABLE_CAMERA=true  # or false to disable

# Make script executable (Linux)
chmod +x backend-launcher.sh

# Start container
./backend-launcher.sh
```

---

## Running Backend Test Cases

The backend tests use `pytest`.

### Running Tests in Docker

1. **Start your backend container**:
   ```bash
   docker-compose up -d backend
   ```

2. **Access the container**:
   - **Docker Desktop**: Click on your container → "Open in Terminal"
   - **Command Line**:
     ```bash
     docker exec -it backend_container_name /bin/bash
     ```

3. **Navigate to the app directory**:
   ```bash
   cd /usr/src/app
   ```

4. **Run tests**:
   - Run all tests:
     ```bash
     pytest
     ```
   - Run specific test file:
     ```bash
     pytest app/tests/test_example.py
     ```
---

## 📚 Developer Resources

| Technology | Documentation |
|------------|---------------|
| FastAPI | https://fastapi.tiangolo.com |
| SQLAlchemy | https://www.sqlalchemy.org |
| Pydantic | https://pydantic-docs.helpmanual.io |
| PostgreSQL | https://www.postgresql.org/docs |
| Docker | https://www.docker.com/ |
| Pytest | https://docs.pytest.org/en/stable/ |

---

## 💡 Troubleshooting

- **Windows PS Issues**: Use Git Bash for all commands
- **PostgreSQL Connection**: Verify password is set to 'aquapoly'
- **Camera Errors**: Check `ENABLE_CAMERA` environment variable
```