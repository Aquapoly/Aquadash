# Migrations guide

The system uses SQLAlchemy for the database, therefore we use Alembic for migrations.

Alembic manages the whole schema, starting from the initial migration that creates the tables. The app does not create tables itself.

Migrations are applied automatically before the app starts: `./run app` starts the `migrate` service, which runs `alembic upgrade head`, and the `app` service only starts once it succeeds. `./run app --native` runs `alembic upgrade head` before uvicorn.

## Commands

| Action              | Command                                                |
|---------------------|--------------------------------------------------------|
| Create migration    | ./run alembic revision --autogenerate -m "[message]"   |
| Apply migration     | ./run alembic upgrade head                             |
| Downgrade migration | ./run alembic downgrade -1                             |
| Check status        | ./run alembic current                                  |
| Mark as up to date  | ./run alembic stamp head                               |

Creating a migration requires `DEV=1` in `.env`, so that the container can write to your local `alembic/versions`.

With `DEV=0`, Alembic uses the migrations baked into the image. Add `--build` to include newer ones: `./run alembic --build upgrade head`.

## Creating a migration file

After modifying the models, you can follow these steps:

### 1. Generate the migration file

- Option 1 (Docker Desktop):

    1. Open the terminal of the 'app' container.

    2. run: ```alembic revision --autogenerate -m "[your changes]"```

- Option 2 (Directly in the console):

    1. run: `docker ps` and find the name (or id) of the backend/app container.

        If it is not running, start the container with `docker-compose up` in the `backend` directory.

    2. run: `docker exec [container name/id] alembic revision --autogenerate -m "[your changes]"` (detects changes in the schemas to generate the migration file).

- Option 3 (`./run`, with `DEV=1` in `.env`):

    1. run: `./run alembic revision --autogenerate -m "[your changes]"`

### 2. Verify the migration file

In the directory `backend/alembic/versions`, you should see your new migration file.

You must verify that the `upgrade` and `downgrade` functions match your changes. If you want to be able to downgrade, constraints must have a name.

Example:

                                         name                    table            check
    op.create_check_constraint("check_id_prototype_positive", "prototypes", "prototype_id >= 0")

    op.drop_constraint("check_id_prototype_positive", "prototypes", type_="check")
    
The first line (upgrade) adds a check constraint named "*check_id_prototype_positive*" that makes sure the id of the prototype is positive. 

The second line is used in a downgrade, it requires a name.

## Applying a migration

Restart the app. The `migrate` service applies any pending migration before the app starts:

    cd backend
    ./run app

With `DEV=0`, add `--build` so the image includes the new migration files: `./run app --build`.

If a migration fails, the app does not start. See the error with:

    docker compose logs migrate

### Upgrading/downgrading manually

These commands run in a new backend container that deletes itself after the command. Stop the app first, since its open connections can block schema changes.

1. Upgrading

        ./run alembic upgrade head

2. Downgrading

        ./run alembic downgrade -1

## Common errors

### Alembic not installed

If you are trying to run the provided commands and there is an error saying Alembic isn't installed, then your container is probably outdated. To fix this, you must rebuild your container:

    cd backend
    docker compose build

### Permission denied when creating a migration

This means the container is using the code baked into the image, which it cannot write to. Set `DEV=1` in `.env` and use `./run alembic`, because a plain `docker compose run` ignores `DEV`.

### Database is not up to date

This just means there was a migration you have not applied yet. You can simply run the upgrading command.

### Constraint or table already exists

    psycopg.errors.DuplicateObject: constraint "check_id_prototype_positive" for relation "prototypes" already exists

The database was created by an older version of the app, which created the tables directly instead of through Alembic, so it has no `alembic_version`. Alembic then tries to run every migration from the start. If the schema is otherwise up to date, mark it as being at the latest migration, once:

    ./run alembic stamp head
