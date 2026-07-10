"""
CFPB Consumer Complaint Database - real customer complaint narratives,
issue categories, and company responses. Used as inspiration for
realistic Complaint Agent test queries and KB phrasing.

The CFPB provides a direct CSV export endpoint. This pulls a date-bounded
slice rather than the full multi-GB dataset (full dataset is huge - slice
it further with the date params below if you need less).

Run from project root: python datasets/cfpb/download.py
"""
import os
import urllib.request

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(OUT_DIR, "cfpb_complaints_sample.csv")

# CFPB Socrata API - CSV export, limited to 5000 rows for a manageable sample.
# Full database / query builder: https://www.consumerfinance.gov/data-research/consumer-complaints/
URL = (
    "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
    "?format=csv&size=5000"
)


def main():
    print(f"Downloading CFPB complaint sample to {OUT_PATH} ...")
    urllib.request.urlretrieve(URL, OUT_PATH)
    print("Done.")


if __name__ == "__main__":
    main()
