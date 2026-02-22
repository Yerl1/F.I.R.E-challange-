from __future__ import annotations

import os
import tempfile
from typing import Any


class PaddleOcrClient:
    def __init__(self, lang: str = "ru") -> None:
        self._lang = lang
        self._engine: Any | None = None
        self._init_error = False

    def _get_engine(self) -> Any | None:
        if self._engine is not None:
            return self._engine
        if self._init_error:
            return None

        try:
            from paddleocr import PaddleOCR

            self._engine = PaddleOCR(use_angle_cls=True, lang=self._lang)
            return self._engine
        except Exception:
            self._init_error = True
            return None

    def _parse_result(self, result: Any) -> str:
        lines: list[str] = []
        if not result:
            return ""

        pages = result if isinstance(result, list) else [result]
        for page in pages:
            if not isinstance(page, list):
                continue
            for item in page:
                if not isinstance(item, list) or len(item) < 2:
                    continue
                text_block = item[1]
                if not isinstance(text_block, (list, tuple)) or not text_block:
                    continue
                text = str(text_block[0]).strip()
                if text:
                    lines.append(text)
        return "\n".join(lines).strip()

    def _preprocess_variants(self, image_path: str) -> list[str]:
        paths: list[str] = []
        try:
            import cv2

            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return paths

            upscaled = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
            otsu = cv2.threshold(upscaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            adaptive = cv2.adaptiveThreshold(
                upscaled,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                11,
            )
            inverted = cv2.bitwise_not(otsu)

            variants = [upscaled, otsu, adaptive, inverted]
            for variant in variants:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = tmp.name
                if cv2.imwrite(tmp_path, variant):
                    paths.append(tmp_path)
                elif os.path.exists(tmp_path):
                    os.remove(tmp_path)

            rotated = cv2.rotate(upscaled, cv2.ROTATE_90_CLOCKWISE)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                rotated_path = tmp.name
            if cv2.imwrite(rotated_path, rotated):
                paths.append(rotated_path)
            elif os.path.exists(rotated_path):
                os.remove(rotated_path)

            return paths
        except Exception:
            return paths

    def _ocr_text(self, engine: Any, image_path: str) -> str:
        try:
            raw_result = engine.ocr(image_path, cls=True)
            return self._parse_result(raw_result)
        except Exception:
            return ""

    def extract_text(self, image_path: str) -> str:
        try:
            from PIL import Image

            with Image.open(image_path) as img:
                img.verify()
        except Exception:
            return ""

        engine = self._get_engine()
        if engine is None:
            return ""

        best_text = self._ocr_text(engine, image_path)

        variant_paths = self._preprocess_variants(image_path)
        try:
            for path in variant_paths:
                candidate = self._ocr_text(engine, path)
                if len(candidate) > len(best_text):
                    best_text = candidate
        finally:
            for path in variant_paths:
                if os.path.exists(path):
                    os.remove(path)

        return best_text
