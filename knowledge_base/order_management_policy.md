# Order Management Policy — TechGadgets Inc

## Orders awaiting shipment

- An order with the status **processing — not yet shipped** is being prepared for dispatch.
- Tracking is sent by email within 24 hours after shipment. Until the order is shipped, there is no carrier tracking number.
- Support must state the verified order status and must not promise a shipment date that is not in the order record.

## Cancellation before shipment

- Customers may request cancellation while an order is **processing — not yet shipped**.
- A cancellation request is not a completed cancellation. Athena must not claim to have cancelled an order, changed an order, or issued money back.
- Athena should explain that the request must be submitted to the order-management team for confirmation. If the order ships before the request is processed, the customer can use the normal return process instead.
- Once an order is shipped, it cannot be cancelled; customers should use the return policy after delivery.

## Returns and refund status

- A return must be received and inspected before a standard refund can be completed.
- After the return is received, refunds are processed to the original payment method within **5–7 business days**.
- An order status of **return received — refund processing** means the return has been received and the refund is in the processing window. Athena must not promise an exact posting date.
- If more than 7 business days have passed after receipt, the customer should be referred to a human support specialist for review.

## Guardrails

- Order lookup is read-only. Athena can verify and explain a status but cannot cancel an order, create a return, or issue a refund.
- Do not invent a tracking number, a cancellation confirmation, or a refund confirmation.
