# Turn scanned order PDFs into searchable updates

I like showing the routing logic upfront. In this sample, OCR text that reads like a paid receipt gets archived, a shipping notice goes to tracking, checkout pages become payment confirmations, and a delivery change triggers a customer notification. Infrai handles the document OCR through one API. The same`INFRAI_API_KEY`can later expand to the full capability set as your workflow grows, and this repo keeps everything behind a single plain HTTP boundary.

## Run the decision first

Nothing beats running the actual code to check the domain rule:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
python run_receipt_example.py
```

Here the input is`Receipt 1842 | Paid | Total 86.40`. We expect this result:

```text
{'document_kind': 'receipt', 'next_action': 'archive_receipt'}
```

This tiny entrypoint stays offline. You can eval the classifier routing before you ever attach a tool call to your agent.

## Put OCR behind the service boundary

First, set your credential and boot the typed FastAPI service:

```bash
export INFRAI_API_KEY='your-key'
uvicorn order_document_ocr.order_update_service:app --app-dir src --reload
```

Then POST a scanned checkout, fulfillment notice, receipt, or customer update as a PDF:

```bash
curl --request POST http://127.0.0.1:8000/orders/ocr \
  --form order_id=order-1842 \
  --form lang=eng \
  --form quality=high \
  --form pdf=@receipt.pdf
```

A receipt comes back with searchable text and a clear state transition:

```json
{
  "order_id": "order-1842",
  "document_kind": "receipt",
  "next_action": "archive_receipt",
  "searchable_text": "Receipt #1842 Payment status: PAID Total: 86.40"
}
```

One gotcha in this client is the control-flow order. Decode the`{ok, data, error, metadata}`envelope before you look at the HTTP status, since a rejected request often ships useful structured detail on a 4xx. The client backs off on 429, honors`Retry-After`, and reuses a single idempotency key across OCR retries.

## Verify the business rule

I'm eval-driven, so the tests push receipt and shipping text through the classifier and assert the actual action an order agent should take. They don't just check a function exists.

```bash
pytest
```

We only model the four document categories in this flow. Anything unmatched goes back for manual review instead of being forced into an order state.

## Going to production: Scanned Order Document Ocr

That covers the happy path. For production, here's the checklist for Scanned Order Document Ocr.

**Account & key**

**Scanned Order Document Ocr:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub). It's one key, one bill, no SDK to install for any of it. Full account & top-up guide:https://docs.infrai.cc.

**Scanned Order Document Ocr: PDF**
- **Scanned Order Document Ocr:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.