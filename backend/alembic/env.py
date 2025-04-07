"""
Alembic environment configuration.
Handles database migrations and model imports.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

# Add python-dotenv import
from dotenv import load_dotenv

from alembic import context

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import Base class
from app.db.base_class import Base

# Import all models here to make them visible to Alembic
from app.models.user import User, UserSession, UserStatus
# Comment out duplicates to avoid import errors
# from app.models.role import Role, Permission
# from app.models.policy import Policy, PolicyVersion, PolicyAssignment
# from app.models.attribute import AttributeDefinition, AttributeValue
# from app.models.audit import (
#     AuditLog, AuditLogArchive, SecurityAlert, 
#     SystemMetric, HealthCheck, AuditEventType, AuditEventSeverity
# )

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    """Get database URL from environment variables."""
    # Define the path to the root .env file relative to this script
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    
    # Check if the .env file exists and load it
    if os.path.exists(dotenv_path):
        print(f"Loading environment variables from: {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path)
    else:
        print(f"Warning: .env file not found at {dotenv_path}")

    # Get DATABASE_URL from environment, raise error if not found
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set or .env file not loaded correctly.")
    
    # Ensure the URL uses the correct dialect for psycopg2 if needed by Alembic
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        
    print(f"Using database URL: {db_url[:db_url.find(':') + 1]}...hidden...@{db_url.split('@')[-1]}") # Hide credentials in output
    return db_url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
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