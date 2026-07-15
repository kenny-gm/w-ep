import os


def pytest_sessionstart(session):
    """Never let tests run against the mounted production SQLite database."""
    database_url = os.environ.get("DATABASE_URL", "sqlite:////app/db/wb_erp.db")
    allow_prod = os.environ.get("WB_ERP_ALLOW_PROD_PYTEST") == "true"
    if not allow_prod and database_url.startswith("sqlite:////app/db/wb_erp.db"):
        raise RuntimeError(
            "Refusing to run pytest against production DB /app/db/wb_erp.db. "
            "Set DATABASE_URL to a test database."
        )
