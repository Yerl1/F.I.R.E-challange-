from __future__ import annotations

import sys
from pathlib import Path


def _ensure_pipeline_import_path() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    pipeline_src = repo_root / "pipeline-service" / "src"
    pipeline_src_str = str(pipeline_src)
    if pipeline_src_str not in sys.path:
        sys.path.insert(0, pipeline_src_str)


_ensure_pipeline_import_path()
