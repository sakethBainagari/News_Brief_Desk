import json
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from db.connection import get_db_cursor
from auth.password import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_db")

# Demo users with safe deterministic passwords for local development
DEMO_USERS = [
    ("Saketh", "saketh@example.com", "REPORTER", "Reporter#123"),
    ("Rahul", "rahul@example.com", "EDITOR", "Editor#123"),
    ("Priya", "priya@example.com", "DESK_HEAD", "DeskHead#123")
]


def seed_database(reset: bool = False):
    root_dir = backend_dir.parent
    schema_file = root_dir / "database" / "schema.sql"
    items_file = root_dir / "data" / "synthetic_raw_items.json"

    if not schema_file.exists():
        logger.error(f"Schema file not found at {schema_file}")
        sys.exit(1)

    if not items_file.exists():
        logger.error(f"Synthetic dataset file not found at {items_file}. Run generate_dataset.py first.")
        sys.exit(1)

    logger.info("Initializing database schema...")
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db_cursor(commit=True) as cur:
        if reset:
            logger.info("Reset requested: Truncating tables...")
            cur.execute("""
                TRUNCATE TABLE audit_logs, story_merges, briefs, story_sources, story_clusters, raw_items, users CASCADE;
            """)
        cur.execute(schema_sql)

    logger.info("Seeding default demo users with password hashes...")
    with get_db_cursor(commit=True) as cur:
        for name, email, role, plain_password in DEMO_USERS:
            pw_hash = hash_password(plain_password)
            cur.execute("""
                INSERT INTO users (name, email, role, password_hash)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                    name = EXCLUDED.name,
                    role = EXCLUDED.role,
                    password_hash = EXCLUDED.password_hash;
            """, (name, email, role, pw_hash))

    logger.info("Seeding synthetic raw wire items...")
    with open(items_file, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    inserted_count = 0
    with get_db_cursor(commit=True) as cur:
        for item in raw_items:
            cur.execute("""
                INSERT INTO raw_items (id, source_name, headline, body, category, source_published_at, ingested_at, embedding_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (
                item["id"],
                item["source_name"],
                item["headline"],
                item["body"],
                item["category"],
                item["source_published_at"],
                item["ingested_at"],
                item.get("embedding_status", "PENDING")
            ))
            if cur.rowcount > 0:
                inserted_count += 1

    logger.info(f"[SUCCESS] Database seeding complete! Demo users & {inserted_count} raw items initialized.")


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    try:
        seed_database(reset=reset_flag)
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        sys.exit(1)
