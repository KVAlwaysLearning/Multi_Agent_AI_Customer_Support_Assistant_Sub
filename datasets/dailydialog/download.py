"""
DailyDialog - multi-turn conversational dataset. Useful for evaluating
multi-turn coherence (does the AI remember earlier turns correctly).

Requires: pip install datasets
Run from project root: python datasets/dailydialog/download.py
"""
from datasets import load_dataset
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("Downloading DailyDialog dataset from Hugging Face...")
    dataset = load_dataset("daily_dialog")
    for split in dataset:
        out_path = os.path.join(OUT_DIR, f"{split}.json")
        dataset[split].to_json(out_path)
        print(f"Saved {split} split ({len(dataset[split])} rows) -> {out_path}")
    print("Done.")


if __name__ == "__main__":
    main()
