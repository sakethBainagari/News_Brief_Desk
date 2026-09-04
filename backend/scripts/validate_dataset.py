import json
from pathlib import Path
import sys


def validate_dataset():
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    items_file = data_dir / "synthetic_raw_items.json"
    ground_truth_file = data_dir / "ground_truth_events.json"

    if not items_file.exists():
        print(f"[ERROR] Missing file: {items_file}")
        sys.exit(1)

    if not ground_truth_file.exists():
        print(f"[ERROR] Missing file: {ground_truth_file}")
        sys.exit(1)

    with open(items_file, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    with open(ground_truth_file, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    print("=== DATASET VALIDATION REPORT ===")
    errors = []

    # 1. Check raw items count (80-100)
    total_items = len(raw_items)
    print(f"Total Raw Items: {total_items}")
    if not (80 <= total_items <= 100):
        errors.append(f"Raw items count ({total_items}) is outside required range [80, 100].")

    # 2. Check events count (20-25)
    total_events = len(ground_truth)
    print(f"Total Events: {total_events}")
    if not (20 <= total_events <= 25):
        errors.append(f"Events count ({total_events}) is outside required range [20, 25].")

    # 3. Check multi-source events
    multi_source_events = [e for e in ground_truth if e["source_count"] >= 3]
    print(f"Multi-source Events (>=3 sources): {len(multi_source_events)}")
    if len(multi_source_events) == 0:
        errors.append("No multi-source events found.")

    # 4. Check single-source events
    single_source_events = [e for e in ground_truth if e["source_count"] == 1]
    print(f"Single-source Events: {len(single_source_events)}")
    if len(single_source_events) == 0:
        errors.append("No single-source events found.")

    # 5. Check false-match pairs
    false_match_pairs = [e for e in ground_truth if e.get("false_match_pair_event_id")]
    print(f"Events in False-Match Test Pairs: {len(false_match_pairs)}")
    if len(false_match_pairs) == 0:
        errors.append("No false-match test cases found.")

    # 6. Check for dummy names (e.g. test1, article1)
    forbidden_terms = ["test1", "test2", "article1", "source1"]
    for item in raw_items:
        text = (item["source_name"] + " " + item["headline"]).lower()
        for term in forbidden_terms:
            if term in text:
                errors.append(f"Found forbidden dummy term '{term}' in item ID {item['id']}")

    # Summary
    if errors:
        print("\n[FAILED] Dataset validation failed with the following errors:")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All Phase 1 dataset validation checks passed cleanly!")


if __name__ == "__main__":
    validate_dataset()
