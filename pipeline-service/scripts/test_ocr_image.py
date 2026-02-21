from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline_service.application.nodes.extract_ocr_text import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Test OCR node directly on one image")
    parser.add_argument("--image", required=True, help="Absolute or relative path to image")
    parser.add_argument("--ticket-id", default="OCR-TEST-1")
    parser.add_argument("--raw-text", default="")
    args = parser.parse_args()

    image_path = Path(args.image)
    state = {
        "ticket_id": args.ticket_id,
        "attachments": str(image_path),
        "raw_text": args.raw_text,
        "errors": [],
    }

    result = run(state)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    text = result.get("extracted_text", "")
    print("\n--- OCR TEXT ---")
    print(text if text else "<empty>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
