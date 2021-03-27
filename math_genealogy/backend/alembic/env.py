import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


ENVIRONMENT = "ENVIRONMENT"


POSTGRES_CONNECTION_DEV = "POSTGRES_CONNECTION_DEV"


POSTGRES_CONNECTION_PROD = "POSTGRES_CONNECTION_PROD"


def get_url(environment):
    if environment.lower().startswith("dev"):
        key = POSTGRES_CONNECTION_DEV
    elif environment.lower().startswith("prod"):
        key = POSTGRES_CONNECTION_PROD
    else:
        raise ValueError(f"Invalid environment key {environment}")
    return os.environ[key]


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


# interpolate string variables in alembic.ini
config.set_section_option(
    config.config_ini_section,
    "DB_CONNECTION",
    get_url(os.environ[ENVIRONMENT]),
)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from math_genealogy.backend.models import Base
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url(os.environ[ENVIRONMENT])
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
