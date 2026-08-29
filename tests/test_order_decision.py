from order_document_ocr.order_decision import (
    DocumentKind,
    NextAction,
    decide_order_action,
)


def test_paid_total_is_archived_as_a_receipt() -> None:
    text = "RECEIPT #1842\nPayment status: PAID\nTotal: 86.40"

    kind, action = decide_order_action(text)

    assert kind is DocumentKind.RECEIPT
    assert action is NextAction.ARCHIVE_RECEIPT


def test_shipping_notice_moves_to_tracking() -> None:
    text = "Your order shipped. Carrier: North Parcel. Tracking: NP-2048"

    kind, action = decide_order_action(text)

    assert kind is DocumentKind.FULFILLMENT
    assert action is NextAction.TRACK_SHIPMENT
