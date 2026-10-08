
from fastapi import APIRouter, Depends

from app.agent_audit import (
    RefundProposal,
    record_policy_decision
)
from app.refund_policy import evaluate_refund_policy


def build_secure_dispatch_router(
    order_store,
    authenticate_customer
):
    router = APIRouter(
        prefix="/lab/secure-agent",
        tags=["Secure AI Agent Dispatcher"]
    )

    @router.post("/evaluate-tool-call")
    def evaluate_tool_call(
        proposal: RefundProposal,
        customer_id: str = Depends(
            authenticate_customer
        )
    ):
        # The customer identity comes from authentication,
        # never from the model's proposed tool arguments.
        policy = evaluate_refund_policy(
            orders=order_store,
            authenticated_customer_id=customer_id,
            order_id=proposal.order_id,
            amount_cents=proposal.amount_cents
        )

        event = record_policy_decision(
            proposal=proposal,
            customer_id=customer_id,
            policy=policy
        )

        # This dispatcher never modifies refund state.
        return {
            "decision": policy["decision"],
            "reason": policy["reason"],
            "executed": False,
            "audit_event_id": event["event_id"]
        }

    return router
