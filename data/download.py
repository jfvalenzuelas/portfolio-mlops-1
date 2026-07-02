import tarfile
from pathlib import Path

import requests
from tqdm import tqdm

URL = "https://www.cs.jhu.edu/~mdredze/datasets/sentiment/unprocessed.tar.gz"
RAW_DIR = Path(__file__).parent / "raw"
ARCHIVE = RAW_DIR / "unprocessed.tar.gz"


def download() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    destination = RAW_DIR / Path(URL).name

    if destination.is_file():
        return destination

    with requests.get(URL, stream=True) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))

        with (
            destination.open("wb") as file,
            tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=destination.name,
            ) as progress,
        ):
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                progress.update(len(chunk))

    return destination


def extract() -> Path:
    if not ARCHIVE.is_file():
        raise FileNotFoundError(f"Archive not found: {ARCHIVE}")

    with tarfile.open(ARCHIVE, "r:gz") as archive:
        archive.extractall(RAW_DIR)

    return RAW_DIR


if __name__ == "__main__":
    path = download()
    print(f"Downloaded to {path}")
