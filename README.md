Application to monitor and control the hydroponics system.

## Setup

### Python

Create a virtual environment :
```bash
python3 -m venv .venv
```
or in vscode : \
Ctrl+Shift+P -> Python: Select Interpreter -> Enter interpreter path -> Enter path to venv/bin/python3

Activate the virtual environment (Linux):
```bash
source ./.venv/bin/activate
```

Activate the virtual environment (Windows):
```
./.venv/Scripts/activate
```

Install dependencies (in the virtual environment):
```bash
pip install -r requirements.txt
```

### Database (Linux)
Install PostgreSQL :
```
sudo apt-get install postgresql postgresql-contrib
```
Start service 
```
sudo systemctl start postgresql.service
```
Set a password for the postgres user (pwd: aquapoly) :
```
sudo -u postgres psql postgres
```
```sql
\password postgres
```

Create a database :
```
sudo -u postgres createdb aquapoly
```

### Database (Windows)
Install PostgreSQL : [Download](https://www.postgresql.org/download/windows/)

Open pgAdmin4 and set a password for the postgres user (pwd: aquapoly) \
Create a database named aquapoly

## Usage

Start the server (at the root of the project):
```
uvicorn app.main:app --reload
```

To start the server with HTTPS:
```
uvicorn app.main:app --ssl-keyfile /etc/ssl/private/table2.aquapoly.ca.key --ssl-certfile /etc/ssl/private/table2.aquapoly.ca.crt --host=0.0.0.0
```

Open the docs in a browser :
http://localhost:8000/docs

## Resources

[Fast API documentation](https://fastapi.tiangolo.com/) \
[Fastapi sql db tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/) \
[SQLAlchemy](https://www.sqlalchemy.org/) \
[Pydantic](https://pydantic-docs.helpmanual.io/)