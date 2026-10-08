
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ValidationError

from app.agent_audit import RefundProposal, propose_refund

router = APIRouter(
    prefix="/lab/agent",
    tags=["Local AI Agent"]
)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "llama3.2:3b"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


REFUND_TOOL = {
    "type": "function",
    "function": {
        "name": "propose_refund",
        "description": (
            "Propose a simulated refund for review. "
            "This never processes a payment."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount_cents": {"type": "integer"}
            },
            "required": ["order_id", "amount_cents"]
        }
    }
}


@router.post("/chat")
def chat_with_agent(request: ChatRequest):
    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a customer support assistant "
                    "in a simulated e-commerce security lab. "
                    "You may propose refunds for review, "
                    "but never claim a refund was processed."
                )
            },
            {
                "role": "user",
                "content": request.message
            }
        ],
        "tools": [REFUND_TOOL]
    }

    try:
        response = httpx.post(
            OLLAMA_URL,
            json=payload,
            timeout=120.0
        )
        response.raise_for_status()
        result = response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Local Ollama service unavailable"
        )

    except (httpx.HTTPStatusError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Ollama returned an invalid response"
        )

    message = result.get("message", {})
    proposals = []
    rejected = 0

    for call in message.get("tool_calls", []):
        function = call.get("function", {})

        if function.get("name") != "propose_refund":
            continue

        try:
            proposal = RefundProposal.model_validate(
                function.get("arguments", {})
            )
        except (ValidationError, ValueError, TypeError):
            rejected += 1
            continue

        # Audit only: never execute a refund.
        event = propose_refund(proposal)
        proposals.append(event)

    return {
        "assistant_message": message.get("content", ""),
        "refund_proposals": proposals,
        "rejected_proposals": rejected,
        "executed": False
    }

