from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))

from app.forecasting.preprocessing import PROCESSED_DATASET_PATH, prepare_forecasting_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=PROCESSED_DATASET_PATH)
    args = parser.parse_args()
    print(json.dumps(prepare_forecasting_dataset(args.source), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
