import argparse
import csv
from pathlib import Path


def generate(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "amount"])
        for index in range(rows):
            writer.writerow([f"{index:08d}", f"{index / 100:.2f}"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output/benchmark-100k.csv")
    parser.add_argument("--rows", type=int, default=100000)
    args = parser.parse_args()
    generate(args.output, args.rows)
