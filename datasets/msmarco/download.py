"""
MS MARCO - large-scale QA dataset for semantic retrieval evaluation.
Useful as a stress-test for the embeddings + FAISS retrieval pipeline
once you've moved past the small company knowledge base.

Requires: pip install datasets
Run from project root: python datasets/msmarco/download.py
"""
from datasets import load_dataset
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("Downloading MS MARCO (v1.1, passage ranking subset) from Hugging Face...")
    dataset = load_dataset("ms_marco", "v1.1")
    for split in dataset:
        out_path = os.path.join(OUT_DIR, f"{split}.json")
        dataset[split].to_json(out_path)
        print(f"Saved {split} split ({len(dataset[split])} rows) -> {out_path}")
    print("Done.")


if __name__ == "__main__":
    main()
