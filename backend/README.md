# Aquadash - Backend (FastAPI)

FastAPI backend for monitoring and controlling a hydroponics system.  
**Developer Documentation** - Not for production use.

---

## 🚀 Quick Start

### To get the backend running on your computer, install Python 3.8+ and Git (optionnal) :

### 🐧 On Linux

  ```bash
  # Install python3:
  sudo apt update && sudo apt install python3
 
  # Install git
  sudo apt install git
  ```
### 🪟 On Windows:  
  **These versions** are recomended: :  
 - [Python](https://apps.microsoft.com/detail/9PNRBTZXMB4Z?hl=en-us&gl=CA&ocid=pdpshare)  
 - [Git Bash](https://git-scm.com/install/windows) 

---

## 🛠 Development Setup

### 1. Virtual Environment

From the `Aquadash/backend` folder, open a terminal and run:

```bash
python -m venv .venv
```

### Activate The Environment

**🐧 On Linux/ 🍎 On MacOS:**

```bash
source .venv/bin/activate
```
🪟 **On Windows:**

 In **VS Code** :  
  - `Ctrl + Shift + P` → `Python: Select Interpreter` → enter path to `backend/.venv/Scripts/python.exe`

  Or in the **Terminal** :
```powershell
.\.venv\Scripts\activate
```
---

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🗄 Database Configuration

The backend uses **PostgreSQL 12+**.  
You can install it directly or use **[Docker](#docker-option-en)** for a simpler setup.

## 🐘 Option A — Native PostgreSQL Installation


- ### 🐧 On Linux

   ```bash
   # 1. Install PostgreSQL
   sudo apt install postgresql postgresql-contrib

   # 2. Start service
   sudo systemctl start postgresql

   # 3. Set password (aquapoly)
   sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'aquapoly';"

   # 4. Create database
   sudo -u postgres createdb aquapoly

   # 5. Start the backend
  uvicorn app.main:app --reload

   ```
   ⚡ Backend should now be running

- ### 🪟 On Windows
   1. Install **[pgAdmin 4](https://www.pgadmin.org/download/pgadmin-4-windows/)** from the official site
   2. Use pgAdmin4 to :
      - Set password for `postgres` user (aquapoly)
      - Create `aquapoly` database
   3. Start backend on a terminal (from backend folder) :
         ```powershell
         uvicorn app.main:app --reload
         ```
      ⚡ Backend should now be running
---

Link to Access API docs:  
🔗 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐋 Option B — Using Docker <a id="docker-option-en"></a>

- ### 🐧 On Linux

   ```bash
   # 1. Install Docker 
   sudo apt install docker.io docker-compose

   # 2. Camera control
   export ENABLE_CAMERA=true  # or false to disable

   # 3. Restart your computer (recommended)

   # 4. Build the app container (first time or after updates)
  docker-compose build

   # 5 Start Containers
  docker-compose up # Or running in background: docker-compose up -d
   ```
   ⚡ Backend should now be running

- ### 🪟 On Windows

  1. Get **[Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)** from the official site  and lauch the installer
  2. Check **Use Wsl2** 
  3. Restat your computer once the install is finished
  4. Build and lauch the container (from backend folder):
      ```bash
      # Build Container
      docker-compose build

      # Start Containers
      docker-compose up # Or running in background: docker-compose up -d
      ```
   ⚡ Backend should now be running

---
Link to Access API docs:  
🔗 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Running Backend Test Cases

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

- **Windows PowerShell issues:** Use Git Bash for commands if PowerShell blocks execution.  
- **PostgreSQL connection errors:** Verify that the `postgres` password is set to `aquapoly` and that the DB service is running.  
- **Docker port already in use** PostgreSQL is probably running **or** A detached container is running.
- **Camera errors:** Ensure the `ENABLE_CAMERA` environment variable is correctly set before starting containers.
---
<br><br>
© 2025 Aquadash — Released under the GNU License
