from enum import Enum


class DocumentKind(str, Enum):
    CHECKOUT = "checkout"
    FULFILLMENT = "fulfillment"
    RECEIPT = "receipt"
    CUSTOMER_UPDATE = "customer_order_update"
    REVIEW = "manual_review"


class NextAction(str, Enum):
    CONFIRM_PAYMENT = "confirm_payment"
    TRACK_SHIPMENT = "track_shipment"
    ARCHIVE_RECEIPT = "archive_receipt"
    NOTIFY_CUSTOMER = "notify_customer"
    REVIEW_DOCUMENT = "review_document"


def decide_order_action(text: str) -> tuple[DocumentKind, NextAction]:
    normalized = " ".join(text.lower().split())
    rules = (
        (("receipt", "total", "paid"), DocumentKind.RECEIPT, NextAction.ARCHIVE_RECEIPT),
        (("shipped", "tracking", "carrier"), DocumentKind.FULFILLMENT, NextAction.TRACK_SHIPMENT),
        (("checkout", "payment", "cart"), DocumentKind.CHECKOUT, NextAction.CONFIRM_PAYMENT),
        (("order update", "delayed", "delivery date"), DocumentKind.CUSTOMER_UPDATE, NextAction.NOTIFY_CUSTOMER),
    )
    for terms, kind, action in rules:
        if any(term in normalized for term in terms):
            return kind, action
    return DocumentKind.REVIEW, NextAction.REVIEW_DOCUMENT

