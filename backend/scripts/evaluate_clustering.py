import json
import logging
import sys
from pathlib import Path

# Force UTF-8 output encoding for Windows terminal compatibility
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.story_clustering import StoryClusteringEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("evaluate_clustering")


def evaluate_clustering():
    data_dir = backend_dir.parent / "data"
    items_file = data_dir / "synthetic_raw_items.json"
    ground_truth_file = data_dir / "ground_truth_events.json"

    if not items_file.exists() or not ground_truth_file.exists():
        logger.error("Missing dataset files in data/ directory. Run generate_dataset.py first.")
        sys.exit(1)

    with open(items_file, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    with open(ground_truth_file, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    logger.info("Executing AI Event Grouping pipeline for evaluation...")
    engine = StoryClusteringEngine()
    clustering_res = engine.process_and_cluster(raw_items=raw_items, save_to_db=False)

    predicted_clusters = clustering_res["clusters"]

    # 1. Build Item ID -> Ground Truth Event ID map
    item_to_gt_event = {}
    event_pairs_map = {}

    for evt in ground_truth:
        evt_id = evt["event_id"]
        if evt.get("false_match_pair_event_id"):
            event_pairs_map[evt_id] = evt["false_match_pair_event_id"]

        for item_id in evt["raw_item_ids"]:
            item_to_gt_event[item_id] = evt_id

    # 2. Build Item ID -> Predicted Cluster Index map
    item_to_pred_cluster = {}
    for cluster_idx, cluster in enumerate(predicted_clusters):
        for item_id in cluster["raw_item_ids"]:
            item_to_pred_cluster[item_id] = cluster_idx

    # 3. Pairwise Evaluation Metrics
    item_ids = [item["id"] for item in raw_items]
    n = len(item_ids)

    tp = 0  # True Merges (GT=Same, Pred=Same)
    fp = 0  # False Merges (GT=Diff, Pred=Same)
    fn = 0  # Missed Merges (GT=Same, Pred=Diff)
    tn = 0  # Correct Separations (GT=Diff, Pred=Diff)

    for i in range(n):
        for j in range(i + 1, n):
            id_a, id_b = item_ids[i], item_ids[j]

            gt_same = (item_to_gt_event.get(id_a) == item_to_gt_event.get(id_b))
            pred_same = (item_to_pred_cluster.get(id_a) == item_to_pred_cluster.get(id_b))

            if gt_same and pred_same:
                tp += 1
            elif not gt_same and pred_same:
                fp += 1
            elif gt_same and not pred_same:
                fn += 1
            else:
                tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # 4. Check False Match Event Pairs Specifically
    false_match_eval = []
    false_merge_occurred = False

    for evt in ground_truth:
        evt1_id = evt["event_id"]
        evt2_id = evt.get("false_match_pair_event_id")

        if evt2_id and evt1_id < evt2_id:
            items1 = evt["raw_item_ids"]
            evt2 = next((e for e in ground_truth if e["event_id"] == evt2_id), None)
            items2 = evt2["raw_item_ids"] if evt2 else []

            merged = False
            for id1 in items1:
                for id2 in items2:
                    if item_to_pred_cluster.get(id1) == item_to_pred_cluster.get(id2):
                        merged = True
                        break

            status = "SEPARATED (CORRECT)" if not merged else "FALSE MERGE (FAILED)"
            if merged:
                false_merge_occurred = True

            false_match_eval.append({
                "pair": f"{evt1_id} vs {evt2_id}",
                "title1": evt["title"],
                "title2": evt2["title"] if evt2 else "",
                "result": status
            })

    print("\n==================================================")
    print("      AI EVENT GROUPING EVALUATION REPORT         ")
    print("==================================================")
    print(f"Total Raw Items Processed : {n}")
    print(f"Ground Truth Events       : {len(ground_truth)}")
    print(f"Predicted Clusters        : {len(predicted_clusters)}")
    print(f"Evaluated Candidate Pairs : {clustering_res['candidate_pairs_evaluated']}")
    print(f"Verified SAME_EVENT Pairs : {clustering_res['same_event_matches']}")
    print("--------------------------------------------------")
    print(f"True Merges (TP)  : {tp}")
    print(f"False Merges (FP) : {fp}")
    print(f"Missed Merges (FN): {fn}")
    print(f"True Separations (TN): {tn}")
    print("--------------------------------------------------")
    print(f"Pairwise Precision : {precision * 100:.2f}%")
    print(f"Pairwise Recall    : {recall * 100:.2f}%")
    print(f"Pairwise F1 Score  : {f1 * 100:.2f}%")
    print("==================================================")
    print("\n--- FALSE MATCH TEST PAIRS AUDIT ---")
    for res in false_match_eval:
        print(f"[{res['result']}] {res['pair']}\n  Event A: {res['title1']}\n  Event B: {res['title2']}\n")

    if false_merge_occurred or fp > 0:
        print("[WARNING] Some false merges occurred during clustering evaluation.")
    else:
        print("[SUCCESS] All false-match test pairs were correctly kept SEPARATE!")


if __name__ == "__main__":
    evaluate_clustering()
