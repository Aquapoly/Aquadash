# Aquadash - Backend (FastAPI)

FastAPI backend for monitoring and controlling a hydroponics system.  
**Developer Documentation — Not for production use.**

---

## 🚀 Quick Start

### To get the backend running on your computer, install the following prerequisites:

- **Python 3.8+**
- **Git**

### 🐧 On Linux

  ```bash
  # Install python3:
  sudo apt update && sudo apt install python3
 
  # Install git
  sudo apt install git
  ```

### 🪟 On Windows:  
  **Official desktop versions** are recommended:  
 - [Python](https://www.python.org/downloads/)  
 - [Git Bash](https://gitforwindows.org/)

---
## 🛠 Development Setup

## 1. Setting Up a Virtual Environment

From the `Aquadash/backend` folder, open a terminal and run:

```bash
python3 -m venv .venv
```

### Activate the Environment

**🐧 On Linux/ 🍎 On MacOS:**

```bash
source .venv/bin/activate
```

🪟 **On Windows:**

 In **VS Code**:  
  - `Ctrl + Shift + P` → `Python: Select Interpreter` → enter path to `backend/.venv/Scripts/python.exe`

 Or in the terminal:  
   ```bash
    .\.venv\Scripts\activate 
   ```

---

## 2. Installing Dependencies

```bash
pip install -r requirements.txt
```

---

# 🗄 Database Configuration

The backend uses **PostgreSQL 12+**.  
You can install it directly or use **Docker** for a simpler setup.

---

## 🐘 Option A — Native PostgreSQL Installation

- ### On Linux

  ```bash
  # 1. Install PostgreSQL
  sudo apt install -y postgresql postgresql-contrib

  # 2. Start the service
  sudo systemctl start postgresql

  # 3. Set password (aquapoly)
  sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'aquapoly';"

  # 4. Create the database
  sudo -u postgres createdb aquapoly

  # 5. Start the backend
  uvicorn app.main:app --reload

  # ⚡ Backend should now be running
  ```

- ### On Windows

  1. Install **[pgAdmin 4](https://www.pgadmin.org/download/pgadmin-4-windows/)** from the official site


Link to access API docs:  
🔗 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐋 Option B — Using Docker

- ### On Linux

  ```bash
  # 1. Install Docker 
  sudo apt install docker.io docker-compose

  # 2. (Optional) Enable camera support
  export ENABLE_CAMERA=true  # or false to disable

  # 3. Build the app container (first time or after updates)
  docker-compose build

  # 4. Start containers
  docker-compose up # Or running in background: docker-compose up -d

  # ⚡ Backend should now be running
  ```

- ### On Windows

  1. Install **[Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)** from the official site  



---

## 🧪 Running Backend Tests Cases

The backend tests use `pytest`.

### Running Tests in Docker

1. **Start the backend container:**
   ```bash
   docker-compose up -d backend
   ```

2. **Access the container:**
   - **Using Docker Desktop:** Click the container → "Open in Terminal"
   - **Using CLI:**
     ```bash
     docker exec -it backend_container_name /bin/bash
     ```

3. **Navigate to the app directory:**
   ```bash
   cd /usr/src/app
   ```

4. **Run tests:**
   - Run all tests:
     ```bash
     pytest
     ```
   - Run a specific test file:
     ```bash
     pytest app/tests/test_example.py
     ```

---

## 📚 Developer Resources

| Technology  | Documentation |
|-------------|---------------|
| FastAPI     | https://fastapi.tiangolo.com |
| SQLAlchemy  | https://www.sqlalchemy.org |
| Pydantic    | https://docs.pydantic.dev |
| PostgreSQL  | https://www.postgresql.org/docs |
| Docker      | https://www.docker.com |
| Pytest      | https://docs.pytest.org/en/stable |

---

## 💡 Troubleshooting

- **Windows PowerShell issues:** Use Git Bash for commands if PowerShell blocks execution.  
- **PostgreSQL connection errors:** Verify that the `postgres` password is set to `aquapoly` and that the DB service is running.  
- **Docker port already in use** PostgreSQL is probably running **or** A detached container is running.
- **Camera errors:** Ensure the `ENABLE_CAMERA` environment variable is correctly set before starting containers.

---
<br><br>
© 2025 Aquadash — Released under the MIT License