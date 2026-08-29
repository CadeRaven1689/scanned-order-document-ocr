from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .ecommerce_ocr import EcommerceOcrClient, InfraiError
from .order_decision import DocumentKind, NextAction, decide_order_action


class OcrOrderRequest(BaseModel):
    order_id: str = Field(min_length=1)
    lang: str = Field(default="eng", min_length=2)
    quality: str = Field(default="accurate", min_length=1)


class OrderDocumentResult(BaseModel):
    order_id: str
    document_kind: DocumentKind
    next_action: NextAction
    searchable_text: str


app = FastAPI(title="Scanned order document OCR")


@app.post("/orders/ocr", response_model=OrderDocumentResult)
def ocr_order_document(
    pdf: UploadFile = File(...),
    order_id: str = Form(...),
    lang: str = Form("eng"),
    quality: str = Form("accurate"),
) -> OrderDocumentResult:
    request = OcrOrderRequest(order_id=order_id, lang=lang, quality=quality)
    contents = pdf.file.read()
    try:
        with EcommerceOcrClient() as client:
            result = client.ocr(contents, lang=request.lang, quality=request.quality)
    except InfraiError as exc:
        client_status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(
            status_code=client_status,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc

    kind, action = decide_order_action(result.text)
    return OrderDocumentResult(
        order_id=request.order_id,
        document_kind=kind,
        next_action=action,
        searchable_text=result.text,
    )
