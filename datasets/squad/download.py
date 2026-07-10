"""
SQuAD 2.0 - question-answering dataset, useful for evaluating retrieval +
answer-generation quality (precision@k style checks on the RAG pipeline).

Direct JSON files, no auth needed.
Run from project root: python datasets/squad/download.py
"""
import os
import urllib.request

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "train-v2.0.json": "https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/train-v2.0.json",
    "dev-v2.0.json": "https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/dev-v2.0.json",
}


def main():
    for fname, url in FILES.items():
        out_path = os.path.join(OUT_DIR, fname)
        print(f"Downloading {fname} ...")
        urllib.request.urlretrieve(url, out_path)
        print(f"Saved -> {out_path}")
    print("Done.")


if __name__ == "__main__":
    main()
