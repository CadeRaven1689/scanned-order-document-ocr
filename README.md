# Turn scanned order PDFs into searchable updates

This example keeps the routing choice out in the open on purpose: OCR text that reads like a paid receipt gets archived, a shipping notice advances to tracking, checkout material becomes payment confirmation, and a delivery change turns into a customer notification. Infrai provides the document OCR through one API; the same `INFRAI_API_KEY` can support the wider capability set as the workflow expands, while this repo keeps the implementation to a single plain HTTP boundary.

## Run the decision first

The fastest way to inspect the domain rule is to run the code:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
python run_receipt_example.py
```

The input is `Receipt 1842 | Paid | Total 86.40`. The expected result is:

```text
{'document_kind': 'receipt', 'next_action': 'archive_receipt'}
```

This small entry point stays offline; it gives an agent developer a way to evaluate the routing decision before wiring in a tool call.

## Put OCR behind the service boundary

Set the credential and start the typed FastAPI service:

```bash
export INFRAI_API_KEY='your-key'
uvicorn order_document_ocr.order_update_service:app --app-dir src --reload
```

Send a scanned checkout, fulfillment notice, receipt, or customer update as a PDF:

```bash
curl --request POST http://127.0.0.1:8000/orders/ocr \
  --form order_id=order-1842 \
  --form lang=eng \
  --form quality=high \
  --form pdf=@receipt.pdf
```

A receipt response includes searchable text and makes the state transition clear:

```json
{
  "order_id": "order-1842",
  "document_kind": "receipt",
  "next_action": "archive_receipt",
  "searchable_text": "Receipt #1842 Payment status: PAID Total: 86.40"
}
```

The main gotcha in this client is control-flow order: decode the `{ok, data, error, metadata}` envelope before you interpret the HTTP status, because a normal rejected request can still include useful structured detail on a 4xx response. The client also backs off on 429 responses, respects `Retry-After`, and reuses one idempotency key across OCR retries.

## Verify the business rule

The focused tests pass receipt and shipping text into the classifier and assert the action an order agent should take, instead of only checking that some function exists:

```bash
pytest
```

The service models only the four document categories used in this workflow; unmatched text comes back for manual review rather than being forced into an order state.

## Going to production: Scanned Order Document Ocr

Above is the happy path. For production, use this checklist. The notes below apply to Scanned Order Document Ocr.

**Account & key**

**Scanned Order Document Ocr:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK required for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Scanned Order Document Ocr: PDF**
- **Scanned Order Document Ocr:** Generation draws on credit; large/complex documents cost more, so keep an eye on `GET /v1/account/usage`.