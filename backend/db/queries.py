from typing import Optional, Dict, Any, List
import logging
from db.connection import get_db_cursor

logger = logging.getLogger(__name__)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetch a user record by email address (including password_hash for auth)."""
    query = """
        SELECT id, name, email, role, password_hash, created_at
        FROM users
        WHERE LOWER(email) = LOWER(%s);
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(query, [email.strip()])
            user = cur.fetchone()

        if not user:
            return None

        user["id"] = str(user["id"])
        if user.get("created_at"):
            user["created_at"] = user["created_at"].isoformat()

        return user
    except Exception as e:
        logger.warning(f"Unable to fetch user by email ({email}): {e}")
        return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a user profile by UUID (excluding password_hash)."""
    query = """
        SELECT id, name, email, role, created_at
        FROM users
        WHERE id = %s;
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(query, [user_id])
            user = cur.fetchone()

        if not user:
            return None

        user["id"] = str(user["id"])
        if user.get("created_at"):
            user["created_at"] = user["created_at"].isoformat()

        return user
    except Exception as e:
        logger.warning(f"Unable to fetch user by id ({user_id}): {e}")
        return None


def get_raw_items(
    page: int = 1,
    limit: int = 20,
    category: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch paginated raw news items with optional category, source, and headline/body search filters.
    """
    offset = (page - 1) * limit
    where_clauses = []
    params = []

    if category:
        where_clauses.append("category = %s")
        params.append(category)

    if source:
        where_clauses.append("source_name = %s")
        params.append(source)

    if search:
        where_clauses.append("(headline ILIKE %s OR body ILIKE %s)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern])

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    count_query = f"SELECT COUNT(*) AS total FROM raw_items {where_sql};"
    items_query = f"""
        SELECT id, source_name, headline, body, category, source_published_at, ingested_at, embedding_status
        FROM raw_items
        {where_sql}
        ORDER BY ingested_at DESC
        LIMIT %s OFFSET %s;
    """

    with get_db_cursor() as cur:
        cur.execute(count_query, params)
        total = cur.fetchone()["total"]

        cur.execute(items_query, params + [limit, offset])
        items = cur.fetchall()

    for item in items:
        item["id"] = str(item["id"])
        if item.get("source_published_at"):
            item["source_published_at"] = item["source_published_at"].isoformat()
        if item.get("ingested_at"):
            item["ingested_at"] = item["ingested_at"].isoformat()

    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


def get_raw_item_by_id(item_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single raw news item by its UUID."""
    query = """
        SELECT id, source_name, headline, body, category, source_published_at, ingested_at, embedding_status
        FROM raw_items
        WHERE id = %s;
    """
    with get_db_cursor() as cur:
        cur.execute(query, [item_id])
        item = cur.fetchone()

    if not item:
        return None

    item["id"] = str(item["id"])
    if item.get("source_published_at"):
        item["source_published_at"] = item["source_published_at"].isoformat()
    if item.get("ingested_at"):
        item["ingested_at"] = item["ingested_at"].isoformat()

    return item


def get_raw_items_stats() -> Dict[str, Any]:
    """Get category distribution, total counts, and date bounds for raw news items."""
    total_query = "SELECT COUNT(*) AS total FROM raw_items;"
    categories_query = """
        SELECT category, COUNT(*) AS count
        FROM raw_items
        GROUP BY category
        ORDER BY count DESC;
    """
    sources_query = """
        SELECT source_name, COUNT(*) AS count
        FROM raw_items
        GROUP BY source_name
        ORDER BY count DESC;
    """
    bounds_query = """
        SELECT MIN(ingested_at) AS earliest, MAX(ingested_at) AS latest
        FROM raw_items;
    """

    with get_db_cursor() as cur:
        cur.execute(total_query)
        total = cur.fetchone()["total"]

        cur.execute(categories_query)
        categories = cur.fetchall()

        cur.execute(sources_query)
        sources = cur.fetchall()

        cur.execute(bounds_query)
        bounds = cur.fetchone()

    return {
        "total_raw_items": total,
        "categories": {c["category"] or "Uncategorized": c["count"] for c in categories},
        "sources": {s["source_name"]: s["count"] for s in sources},
        "earliest_ingested_at": bounds["earliest"].isoformat() if bounds and bounds.get("earliest") else None,
        "latest_ingested_at": bounds["latest"].isoformat() if bounds and bounds.get("latest") else None
    }
