# Math Genealogy Scraper

A project for scraping student/advisor relationships from the [Math Genealogy](https://mathgenealogy.org/) website.


# Local Setup

## Install Python
1. Install a recent version of Python. These instructions were verified for Python 3.7.7. Your mileage may vary with other versions. You can check the currently installed version with `python --version`
1. Create a virtual environment in the root directory of the project:
    ```bash
    python -m venv venv
    ```
1. Activate the virtual environment with `source venv/bin/activate`
1. Upgrade pip: `pip install --upgrade pip`
1. Install the project as an editable package by running the following from the project root:
    ```bash
    pip install -e .
    ```
1. Install additional dependencies
    ```bash
    pip install -r requirements.development.txt
    ```

## Install Docker and Docker Compose
1. Follow the [official installation instructions](https://docs.docker.com/install/) if you do not already have Docker installed.

## Source local environment variables
1. In the project root directory, create a file called .env with the following contents:
    ```
    export ENVIRONMENT="dev"
    export POSTGRES_CONNECTION_DEV="postgresql://postgres:postgres@localhost:5432/postgres"
    ```

## Database Setup
1. Run a PostgreSQL database server in a docker container by running the following command in the project root directory:
    ```bash
    docker compose up --build -d
    ```
1. Check that docker compose ran correctly with `docker ps`. You should see two containers running: `math-genealogy-scraper-pgadmin-1` and `math-genealogy-scraper-postgres-1`.
1. In a new terminal, check that you can connect to the database by running the following command in the project root directory:
    ```bash
    docker compose exec postgres psql -U postgres
    ```
1. Check that the database is in a clean state with no extra tables with:
    ```
    \l
    \c postgres
    \dt
    ```
You should not see any tables with "student" or "advisor" in the name.
1. Keep the psql terminal running. You will need it in a minute. When you are done, you can exit the psql prompt with `\q`.

## Run Alembic Migrations
1. `cd` into the `math_genealogy/backend` directory and run the following command:
    ```bash
    alembic upgrade head
    ```
1. In your psql cli, check that several new tables were created with `\dt`.


## Run the Scraper
1. `cd` into `math_genealogy/scrapers` and run the following command:
    ```bash
    scrapy crawl math_genealogy
    ```
