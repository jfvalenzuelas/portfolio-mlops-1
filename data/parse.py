import io
from pathlib import Path

import pandas as pd
from lxml import etree

RAW_DIR = Path(__file__).parent / "raw"
PROCESSED_DIR = Path(__file__).parent / "processed"
SORTED_DATA_DIR = RAW_DIR / "sorted_data"


def _parse_review_file(path: Path, category: str, label: str) -> list[dict[str, str]]:
    text = path.read_text(encoding="latin-1")
    wrapped = f"<reviews>{text}</reviews>".encode("latin-1")

    rows: list[dict[str, str]] = []
    for _event, review in etree.iterparse(
        io.BytesIO(wrapped),
        events=("end",),
        tag="review",
        recover=True,
    ):
        row: dict[str, str] = {"category": category, "label": label}
        for child in review:
            value = (child.text or "").strip()
            tag = child.tag
            if tag == "review":
                continue
            if tag == "unique_id":
                if value.isdigit():
                    row["unique_id"] = value
                else:
                    row.setdefault("unique_id_slug", value)
            elif tag == "product_type":
                row.setdefault("product_type", value)
            else:
                row[tag] = value
        rows.append(row)
        review.clear()

    return rows


def _load_reviews() -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for category_dir in sorted(SORTED_DATA_DIR.iterdir()):
        if not category_dir.is_dir():
            continue

        category = category_dir.name
        for label in ("positive", "negative"):
            path = category_dir / f"{label}.review"
            if path.is_file():
                rows.extend(_parse_review_file(path, category, label))

    return pd.DataFrame(rows)


def transform() -> None:
    df = _load_reviews()
    print(df.head())
    print(df.columns)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output = PROCESSED_DIR / "reviews.parquet"
    df.to_parquet(output, index=False)
    print(f"Saved {len(df):,} rows to {output}")


if __name__ == "__main__":
    transform()
