from contextlib import contextmanager
import logging
import psycopg
from psycopg.rows import dict_row
from config import Config

logger = logging.getLogger(__name__)

_pool = None


def get_db_connection():
    """Returns a direct psycopg v3 database connection."""
    try:
        conn = psycopg.connect(
            Config.DATABASE_URL,
            row_factory=dict_row,
            autocommit=False,
            connect_timeout=3
        )
        return conn
    except Exception as e:
        logger.warning(f"Failed to connect to PostgreSQL database: {e}")
        raise


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager yielding a dictionary-row cursor.
    Auto-commits if commit=True and no exception occurs.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            yield cur
            if commit:
                conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error during execution: {e}")
        raise
    finally:
        if conn:
            conn.close()


def check_db_health() -> bool:
    """Utility to test database connectivity."""
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT 1 AS health;")
            res = cur.fetchone()
            return res is not None and res.get("health") == 1
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False
