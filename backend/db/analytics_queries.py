from typing import Dict, Any, List
from db.connection import get_db_cursor


def format_seconds_duration(seconds: float) -> str:
    """Formats duration seconds into readable human string (e.g., '2h 15m' or '45m')."""
    if seconds is None or seconds < 0:
        return "N/A"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def get_desk_head_analytics() -> Dict[str, Any]:
    """Calculates Desk Head publication metrics and publication history from PostgreSQL."""
    today_sql = "SELECT COUNT(*) AS total FROM briefs WHERE status = 'PUBLISHED' AND published_at >= CURRENT_DATE;"
    yesterday_sql = """
        SELECT COUNT(*) AS total FROM briefs
        WHERE status = 'PUBLISHED'
          AND published_at >= CURRENT_DATE - INTERVAL '1 day'
          AND published_at < CURRENT_DATE;
    """
    total_sql = "SELECT COUNT(*) AS total FROM briefs WHERE status = 'PUBLISHED';"

    avg_time_sql = """
        SELECT AVG(EXTRACT(EPOCH FROM (b.published_at - COALESCE(sc.first_incoming_at, b.created_at)))) AS avg_seconds
        FROM briefs b
        JOIN story_clusters sc ON b.story_id = sc.id
        WHERE b.status = 'PUBLISHED' AND b.published_at IS NOT NULL;
    """

    categories_sql = """
        SELECT sc.category, COUNT(b.id) AS count
        FROM briefs b
        JOIN story_clusters sc ON b.story_id = sc.id
        WHERE b.status = 'PUBLISHED'
        GROUP BY sc.category
        ORDER BY count DESC;
    """

    history_sql = """
        SELECT
            b.id AS brief_id,
            b.story_id,
            b.headline AS brief_headline,
            b.summary AS brief_summary,
            sc.category,
            sc.first_incoming_at,
            b.created_at,
            b.published_at,
            u.name AS publisher_name,
            COUNT(ss.raw_item_id) AS source_count,
            EXTRACT(EPOCH FROM (b.published_at - COALESCE(sc.first_incoming_at, b.created_at))) AS duration_seconds
        FROM briefs b
        JOIN story_clusters sc ON b.story_id = sc.id
        LEFT JOIN users u ON b.editor_id = u.id
        LEFT JOIN story_sources ss ON sc.id = ss.story_id
        WHERE b.status = 'PUBLISHED'
        GROUP BY b.id, sc.id, u.name
        ORDER BY b.published_at DESC;
    """

    with get_db_cursor() as cur:
        cur.execute(today_sql)
        published_today = cur.fetchone()["total"]

        cur.execute(yesterday_sql)
        published_yesterday = cur.fetchone()["total"]

        cur.execute(total_sql)
        total_published = cur.fetchone()["total"]

        cur.execute(avg_time_sql)
        avg_res = cur.fetchone()
        avg_seconds = float(avg_res["avg_seconds"]) if avg_res and avg_res.get("avg_seconds") is not None else 0.0

        cur.execute(categories_sql)
        categories = cur.fetchall()

        cur.execute(history_sql)
        history = cur.fetchall()

    for item in history:
        item["brief_id"] = str(item["brief_id"])
        item["story_id"] = str(item["story_id"])
        item["source_count"] = int(item.get("source_count", 0))
        item["duration_seconds"] = float(item["duration_seconds"]) if item.get("duration_seconds") is not None else 0.0
        item["duration_formatted"] = format_seconds_duration(item["duration_seconds"])

        if item.get("first_incoming_at"):
            item["first_incoming_at"] = item["first_incoming_at"].isoformat()
        if item.get("created_at"):
            item["created_at"] = item["created_at"].isoformat()
        if item.get("published_at"):
            item["published_at"] = item["published_at"].isoformat()

    return {
        "published_today": published_today,
        "published_yesterday": published_yesterday,
        "total_published": total_published,
        "average_time_to_publication_seconds": avg_seconds,
        "average_time_to_publication_formatted": format_seconds_duration(avg_seconds),
        "categories": {c["category"] or "General": c["count"] for c in categories},
        "publication_history": history
    }


def get_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves operational audit logs."""
    query = """
        SELECT a.id, a.actor_id, u.name AS actor_name, u.role AS actor_role, a.action, a.entity_type, a.entity_id, a.metadata, a.created_at
        FROM audit_logs a
        LEFT JOIN users u ON a.actor_id = u.id
        ORDER BY a.created_at DESC
        LIMIT %s;
    """
    with get_db_cursor() as cur:
        cur.execute(query, [limit])
        logs = cur.fetchall()

    for log in logs:
        log["id"] = str(log["id"])
        if log.get("actor_id"):
            log["actor_id"] = str(log["actor_id"])
        if log.get("entity_id"):
            log["entity_id"] = str(log["entity_id"])
        if log.get("created_at"):
            log["created_at"] = log["created_at"].isoformat()

    return logs
