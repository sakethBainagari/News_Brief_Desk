import json
import unittest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from scripts.validate_dataset import validate_dataset


class DatasetTestCase(unittest.TestCase):
    def test_synthetic_dataset_properties(self):
        data_dir = backend_dir.parent / "data"
        items_file = data_dir / "synthetic_raw_items.json"
        ground_truth_file = data_dir / "ground_truth_events.json"

        self.assertTrue(items_file.exists(), "synthetic_raw_items.json must exist")
        self.assertTrue(ground_truth_file.exists(), "ground_truth_events.json must exist")

        with open(items_file, "r", encoding="utf-8") as f:
            items = json.load(f)

        with open(ground_truth_file, "r", encoding="utf-8") as f:
            events = json.load(f)

        # 1. Total items count [80, 100]
        self.assertGreaterEqual(len(items), 80)
        self.assertLessEqual(len(items), 100)

        # 2. Total underlying events [20, 25]
        self.assertGreaterEqual(len(events), 20)
        self.assertLessEqual(len(events), 25)

        # 3. Verify false match pairs exist
        false_match_events = [e for e in events if e.get("false_match_pair_event_id")]
        self.assertGreater(len(false_match_events), 0)

        # 4. Verify single source events exist
        single_source_events = [e for e in events if e["source_count"] == 1]
        self.assertGreater(len(single_source_events), 0)

        # 5. Verify multi-source events exist
        multi_source_events = [e for e in events if e["source_count"] >= 3]
        self.assertGreater(len(multi_source_events), 0)


if __name__ == "__main__":
    unittest.main()
