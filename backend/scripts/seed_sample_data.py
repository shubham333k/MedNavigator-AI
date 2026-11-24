"""Ingest the checked-in sample files into the local Chroma database."""

from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.pipeline import get_ingestion_pipeline  # noqa: E402


def main() -> None:
    pipeline = get_ingestion_pipeline()
    sample_dir = BACKEND_ROOT / "sample_data"
    files = [
        (sample_dir / "hypertension.txt", "text"),
        (sample_dir / "sample_guideline.pdf", "pdf"),
    ]

    for path, document_type in files:
        result = pipeline.ingest_document(
            file_content=path.read_bytes(),
            document_type=document_type,
            title=path.stem.replace("_", " ").title(),
            source_url="",
        )
        print(f"{path.name}: {result}")


if __name__ == "__main__":
    main()
