
# Independent refund policy evaluator
# All decisions are simulations.

REVIEW_THRESHOLD_CENTS = 25000  # Demo: $250


def evaluate_refund_policy(
    *,
    orders,
    authenticated_customer_id,
    order_id,
    amount_cents
):
    def result(decision, reason):
        return {
            "decision": decision,
            "reason": reason,
            "executed": False
        }

    # Validate the proposed amount.
    if (
        type(amount_cents) is not int
        or amount_cents <= 0
    ):
        return result("deny", "invalid_amount")

    order = orders.get(order_id)

    # Do not reveal whether another customer's
    # order actually exists.
    if (
        order is None
        or order["customer_id"]
        != authenticated_customer_id
    ):
        return result("deny", "order_not_accessible")

    if not order["eligible"]:
        return result("deny", "order_ineligible")

    if order["refunded"]:
        return result("deny", "already_refunded")

    if amount_cents != order["total_cents"]:
        return result("deny", "amount_mismatch")

    # Large refunds require manual approval.
    if amount_cents >= REVIEW_THRESHOLD_CENTS:
        return result(
            "human_review_required",
            "approval_threshold"
        )

    return result("would_allow", "checks_passed")
