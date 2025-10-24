# Aquadash - Backend (FastAPI)

FastAPI backend for monitoring and controlling a hydroponics system.

Developer Documentation - Not for production use.

# 🚀 Quick Start

To get the backend to work on your pc, you will need to install some prerequisites:

- Python 3.8+
    
    ```jsx
    sudo apt update && sudo apt install python3
    ```
    
- Git
    
    ```jsx
    sudo apt install git
    ```
    

If you are on Windows, you might want to get these versions to make setting this up easier:

- Python:
- Git bash:

## 1. Setting Up a Virtual Environment

From the backend folder, on your terminal, enter:

```python
python -m venv .venv
```

Now, to activate it. From VS Code you can

On **Linux/MacOS**:

```python
source .venv/bin/activate
```

Or on **Windows**, you can either enter in VS Code:

 `Ctrl+Shift+P` → `Python: Select Interpreter` → Enter path to `.venv/Scripts/python.exe`
> 

Or in the terminal:

```python
.\.venv\Scripts\activate
```

## 2. Installing the Dependencies

```bash
pip install -r requirements.txt
```

# 🗄 Database Configuration

The database is runs on postgresql 12+. You can either install it directly or, if you want a simpler way, use docker 

## 🐘 Option A - PostgreSQL

### On Linux : 

```bash
# 1. Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 2. Start service
sudo systemctl start postgresql

# 3. Set password (aquapoly)
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'aquapoly';"

# 4. Create database
sudo -u postgres createdb aquapoly

# 5. Start Backend
uvicorn app.main:app --reload

⚡ # Backend should now be running
```

### Or on Windows :

Install pg4dmin from the official site: [https://www.pgadmin.org/download/pgadmin-4-windows/](https://www.pgadmin.org/download/pgadmin-4-windows/)

```cpp
#includeTO_CHANGE_SECTION
String officialy = true;
```

## **🐋** Option B - Docker

### On Linux : 

```bash
# 1. Install docker
sudo apt install docker

# 2. Activate camera control
export ENABLE_CAMERA=true # or false to disable

# 3. Build App Container(First use or update only)
docker-compose build

# 4. Start Container 
docker-compose up

⚡ # Backend should now be running
```

### On windows : 

1. Install dockerDesktop from the official site:
    
    [https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)
    
2. 

```cpp
#includeTO_CHANGE_SECTION
String officialy = true;
```

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