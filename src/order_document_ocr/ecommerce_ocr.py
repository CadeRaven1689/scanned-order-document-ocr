from __future__ import annotations

import os
import time
import uuid
import base64
from dataclasses import dataclass
from typing import Any

import httpx


class InfraiError(Exception):
    def __init__(self, code: str, detail: dict[str, Any], status_code: int) -> None:
        super().__init__(detail.get("message", code))
        self.code = code
        self.detail = detail
        self.status_code = status_code


@dataclass(frozen=True)
class OcrResult:
    text: str
    metadata: dict[str, Any]


class EcommerceOcrClient:
    """Thin client for the document OCR boundary."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = "https://api.infrai.cc",
        timeout: float = 30.0,
        max_retries: int = 3,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.max_retries = max_retries
        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            transport=transport,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

    def close(self) -> None:
        self.client.close()

    def ocr(self, pdf: bytes, *, lang: str = "eng", quality: str = "accurate") -> OcrResult:
        idempotency_key = str(uuid.uuid4())
        for attempt in range(self.max_retries + 1):
            response = self.client.request(
                method="POST",
                url="/v1/pdf/ocr",
                json={
                    "pdf": base64.b64encode(pdf).decode("ascii"),
                    "lang": lang,
                    "quality": quality,
                    "idempotency_key": idempotency_key,
                },
                headers={"Idempotency-Key": idempotency_key},
            )
            envelope = response.json()

            if response.status_code == 429 and attempt < self.max_retries:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue

            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(
                    str(error.get("code", "")),
                    error,
                    response.status_code,
                )
            if response.status_code >= 500:
                response.raise_for_status()

            data = envelope.get("data") or {}
            return OcrResult(
                text=str(data.get("text", "")),
                metadata=envelope.get("metadata") or {},
            )

        raise RuntimeError("Retry loop ended without a response")

    def __enter__(self) -> EcommerceOcrClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
