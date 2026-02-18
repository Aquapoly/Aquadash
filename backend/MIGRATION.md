# Migrations guide

The system uses SQLAlchemy for the database, therefore we use Alembic for migrations.

## Commands

| Action              | Command                                                                    |
|---------------------|----------------------------------------------------------------------------|
| Create migration    | docker compose run --rm app alembic revision --autogenerate -m "[message]" |
| Apply migration     | docker compose run --rm app alembic upgrade head                           |
| Downgrade migration | docker compose run --rm app alembic downgrade -1                           |
| Check status        | docker compose run --rm app alembic current                                |

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

To apply a migration, the DB container must be running. However the backend container must be stopped because it locks the database.

### Stopping the backend container

- Option 1 (Docker Desktop):

    Manually stop the backend/app container and ensure the db container is running.

- Option 2:

    1. `docker ps`

    2. `docker stop [container name/id]` with the backend/app container

### Upgrading/downgrading

Run this command to execute the migration in a new backend container that deletes itself after the command.

    cd backend

1. Upgrading

        docker compose run --rm app alembic upgrade head

2. Downgrading

        docker compose run --rm app alembic downgrade -1
