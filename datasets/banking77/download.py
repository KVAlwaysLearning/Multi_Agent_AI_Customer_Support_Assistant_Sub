"""
Banking77 - intent classification dataset (77 banking-related intents).
Used to validate/benchmark the Intent Detection Agent.

Requires: pip install datasets
Run from project root: python datasets/banking77/download.py

NOTE: this script needs real internet access to huggingface.co, which
is not reachable from this build sandbox - it's written to run on your
own machine (or wherever the backend will actually be developed/deployed).
"""
from datasets import load_dataset
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("Downloading Banking77 dataset from Hugging Face...")
    dataset = load_dataset("banking77")
    for split in dataset:
        out_path = os.path.join(OUT_DIR, f"{split}.csv")
        dataset[split].to_csv(out_path)
        print(f"Saved {split} split ({len(dataset[split])} rows) -> {out_path}")
    print("Done. Use this to benchmark agents/intent_detection.py accuracy.")


if __name__ == "__main__":
    main()
