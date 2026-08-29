from order_document_ocr.order_decision import decide_order_action


def main() -> None:
    scanned_text = "Receipt 1842 | Paid | Total 86.40"
    document_kind, next_action = decide_order_action(scanned_text)
    print({"document_kind": document_kind.value, "next_action": next_action.value})


if __name__ == "__main__":
    main()
