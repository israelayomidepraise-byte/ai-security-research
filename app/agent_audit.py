
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(
    prefix="/lab/agent",
    tags=["AI Agent Security Lab"]
)

# Temporary in-memory audit storage
_audit_events = []
_audit_lock = Lock()


class RefundProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(
        pattern=r"^ORD-\d{4}$"
    )
    amount_cents: int = Field(gt=0)


def get_audit_events():
    with _audit_lock:
        return [event.copy() for event in _audit_events]


def clear_audit_events():
    with _audit_lock:
        _audit_events.clear()


@router.post("/propose-refund")
def propose_refund(proposal: RefundProposal):
    """
    Record an AI refund proposal.

    This endpoint never executes a refund.
    """

    event = {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "action": "refund",
        "order_id": proposal.order_id,
        "amount_cents": proposal.amount_cents,
        "decision": "proposal_only",
        "executed": False
    }

    with _audit_lock:
        _audit_events.append(event)

        # Prevent unlimited memory growth
        if len(_audit_events) > 1000:
            _audit_events.pop(0)

    return event

def record_policy_decision(
    proposal: RefundProposal,
    customer_id: str,
    policy: dict
):
    """Record a policy decision without executing a refund."""

    event = {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": "authenticated_tool_dispatch",
        "action": "refund",
        "customer_id": customer_id,
        "order_id": proposal.order_id,
        "amount_cents": proposal.amount_cents,
        "decision": policy["decision"],
        "reason": policy["reason"],
        "executed": False
    }

    with _audit_lock:
        _audit_events.append(event)

        if len(_audit_events) > 1000:
            _audit_events.pop(0)

    return event
