import json
import logging
from typing import Optional, Dict, Any, List
from db.connection import get_db_cursor

logger = logging.getLogger(__name__)


def log_audit_event(actor_id: Optional[str], action: str, entity_type: str, entity_id: Optional[str], metadata: Optional[Dict[str, Any]] = None):
    """Inserts a structured operational audit log entry."""
    query = """
        INSERT INTO audit_logs (actor_id, action, entity_type, entity_id, metadata)
        VALUES (%s, %s, %s, %s, %s);
    """
    try:
        with get_db_cursor(commit=True) as cur:
            cur.execute(query, (actor_id, action, entity_type, entity_id, json.dumps(metadata) if metadata else None))
    except Exception as e:
        logger.warning(f"Could not log audit event: {e}")


def get_brief_by_id(brief_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single brief by UUID."""
    query = """
        SELECT id, story_id, reporter_id, editor_id, headline, summary, status, created_at, submitted_at, published_at
        FROM briefs
        WHERE id = %s;
    """
    with get_db_cursor() as cur:
        cur.execute(query, [brief_id])
        brief = cur.fetchone()

    if not brief:
        return None

    brief["id"] = str(brief["id"])
    brief["story_id"] = str(brief["story_id"])
    if brief.get("reporter_id"):
        brief["reporter_id"] = str(brief["reporter_id"])
    if brief.get("editor_id"):
        brief["editor_id"] = str(brief["editor_id"])
    if brief.get("created_at"):
        brief["created_at"] = brief["created_at"].isoformat()
    if brief.get("submitted_at"):
        brief["submitted_at"] = brief["submitted_at"].isoformat()
    if brief.get("published_at"):
        brief["published_at"] = brief["published_at"].isoformat()

    return brief


def edit_brief(brief_id: str, headline: str, summary: str, user_id: str) -> Dict[str, Any]:
    """Edits a brief draft. Fails if brief is already published."""
    brief = get_brief_by_id(brief_id)
    if not brief:
        raise ValueError(f"Brief '{brief_id}' not found.")

    if brief["status"] == "PUBLISHED":
        raise ValueError("Cannot edit a published brief. Once published, the brief is locked.")

    query = """
        UPDATE briefs
        SET headline = %s, summary = %s, reporter_id = %s
        WHERE id = %s AND status != 'PUBLISHED';
    """
    with get_db_cursor(commit=True) as cur:
        cur.execute(query, (headline, summary, user_id, brief_id))

    log_audit_event(user_id, "EDIT_BRIEF", "BRIEF", brief_id, {"headline": headline})
    return get_brief_by_id(brief_id)


def submit_brief(brief_id: str, user_id: str) -> Dict[str, Any]:
    """Submits a brief draft for editor review."""
    brief = get_brief_by_id(brief_id)
    if not brief:
        raise ValueError(f"Brief '{brief_id}' not found.")

    if brief["status"] == "PUBLISHED":
        raise ValueError("Cannot submit an already published brief.")

    update_brief_sql = """
        UPDATE briefs
        SET status = 'EDITOR_REVIEW', submitted_at = NOW(), reporter_id = %s
        WHERE id = %s;
    """
    update_story_sql = """
        UPDATE story_clusters
        SET status = 'EDITOR_REVIEW', updated_at = NOW()
        WHERE id = %s;
    """
    with get_db_cursor(commit=True) as cur:
        cur.execute(update_brief_sql, (user_id, brief_id))
        cur.execute(update_story_sql, [brief["story_id"]])

    log_audit_event(user_id, "SUBMIT_BRIEF_FOR_REVIEW", "BRIEF", brief_id, {"story_id": brief["story_id"]})
    return get_brief_by_id(brief_id)


def publish_brief(brief_id: str, editor_id: str) -> Dict[str, Any]:
    """
    Publishes a brief draft.
    Allowed ONLY for Editors. Sets status = 'PUBLISHED', records published_at timestamp.
    """
    brief = get_brief_by_id(brief_id)
    if not brief:
        raise ValueError(f"Brief '{brief_id}' not found.")

    if brief["status"] == "PUBLISHED":
        raise ValueError("Brief is already published. Duplicate publication is not permitted.")

    update_brief_sql = """
        UPDATE briefs
        SET status = 'PUBLISHED', published_at = NOW(), editor_id = %s
        WHERE id = %s;
    """
    update_story_sql = """
        UPDATE story_clusters
        SET status = 'PUBLISHED', updated_at = NOW()
        WHERE id = %s;
    """
    with get_db_cursor(commit=True) as cur:
        cur.execute(update_brief_sql, (editor_id, brief_id))
        cur.execute(update_story_sql, [brief["story_id"]])

    log_audit_event(editor_id, "PUBLISH_STORY_BRIEF", "BRIEF", brief_id, {"story_id": brief["story_id"]})
    return get_brief_by_id(brief_id)


def merge_story_clusters(source_story_id: str, target_story_id: str, editor_id: str, reason: str) -> Dict[str, Any]:
    """
    Merges source_story_id into target_story_id.
    Allowed ONLY for Editors. Reassigns story_sources, marks source story as MERGED, logs audit.
    """
    if source_story_id == target_story_id:
        raise ValueError("Source and target stories cannot be the same.")

    # Reassign sources
    reassign_sql = """
        UPDATE story_sources
        SET story_id = %s
        WHERE story_id = %s;
    """
    mark_merged_sql = """
        UPDATE story_clusters
        SET status = 'MERGED', updated_at = NOW()
        WHERE id = %s;
    """
    insert_merge_sql = """
        INSERT INTO story_merges (source_story_id, target_story_id, merged_by, reason)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """

    with get_db_cursor(commit=True) as cur:
        cur.execute(reassign_sql, (target_story_id, source_story_id))
        cur.execute(mark_merged_sql, [source_story_id])
        cur.execute(insert_merge_sql, (source_story_id, target_story_id, editor_id, reason))
        merge_res = cur.fetchone()

    merge_id = str(merge_res["id"])
    log_audit_event(
        editor_id,
        "MERGE_STORY_CLUSTERS",
        "STORY_CLUSTER",
        target_story_id,
        {"source_story_id": source_story_id, "reason": reason, "merge_record_id": merge_id}
    )

    return {
        "merge_id": merge_id,
        "source_story_id": source_story_id,
        "target_story_id": target_story_id,
        "merged_by": editor_id,
        "reason": reason
    }


def reset_demo_data_in_db(actor_id: str) -> Dict[str, Any]:
    """
    Resets generated demo workflow state (story_merges, briefs, story_sources, story_clusters, audit_logs).
    Leaves raw_items (81) and users (3) intact.
    Logs a single 'DEMO_RESET' audit event.
    """
    truncate_queries = [
        "TRUNCATE TABLE story_merges CASCADE;",
        "TRUNCATE TABLE briefs CASCADE;",
        "TRUNCATE TABLE story_sources CASCADE;",
        "TRUNCATE TABLE story_clusters CASCADE;",
        "TRUNCATE TABLE audit_logs CASCADE;",
        "UPDATE raw_items SET embedding_status = 'PENDING';"
    ]

    with get_db_cursor(commit=True) as cur:
        for q in truncate_queries:
            cur.execute(q)

    log_audit_event(
        actor_id=actor_id,
        action="DEMO_RESET",
        entity_type="SYSTEM",
        entity_id=None,
        metadata={"description": "Reset demo data to initial seeded state (81 raw items preserved)"}
    )

    return {
        "status": "success",
        "message": "Demo data reset successfully. The newsroom is ready for a fresh AI run.",
        "raw_items_count": 81,
        "story_clusters_count": 0,
        "briefs_count": 0,
        "story_sources_count": 0,
        "story_merges_count": 0
    }
