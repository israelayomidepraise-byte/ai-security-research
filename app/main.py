
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="AI Agent Security Testing Lab",
    description="A simulated e-commerce refund API for security research",
    version="0.1.0"
)

# Fake orders for our local testing environment
orders = {
    "ORD-1001": {
        "customer_id": "CUST-001",
        "total_cents": 12000,
        "eligible": True,
        "refunded": False
    },
    "ORD-1002": {
        "customer_id": "CUST-002",
        "total_cents": 8000,
        "eligible": False,
        "refunded": False
    }
}


class RefundRequest(BaseModel):
    order_id: str
    customer_id: str
    amount_cents: int = Field(gt=0)


@app.get("/")
def home():
    return {"message": "AI Security Testing Lab is running"}


@app.get("/orders")
def get_orders():
    return orders


@app.post("/refunds")
def process_refund(request: RefundRequest):
    order = orders.get(request.order_id)

    if order is None:
        raise HTTPException(404, "Order not found")

    if order["customer_id"] != request.customer_id:
        raise HTTPException(403, "Customer does not match order")

    if not order["eligible"]:
        raise HTTPException(403, "Order is not eligible for refund")

    if order["refunded"]:
        raise HTTPException(409, "Order already refunded")

    if request.amount_cents != order["total_cents"]:
        raise HTTPException(400, "Refund must match the order total")

    order["refunded"] = True

    return {
        "status": "simulated_refund_approved",
        "order_id": request.order_id,
        "amount_cents": request.amount_cents
    }



# Protected refund workflow (local security lab)
import os
from secrets import compare_digest
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer(auto_error=False)


class ProtectedRefundRequest(BaseModel):
    order_id: str
    amount_cents: int = Field(gt=0)


def get_authenticated_customer(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
):
    token = credentials.credentials if credentials else None

    # Test credentials come from environment variables.
    # Never commit real API tokens to GitHub.
    customer_tokens = {
        "CUST-001": os.getenv("LAB_TOKEN_CUST_001"),
        "CUST-002": os.getenv("LAB_TOKEN_CUST_002"),
    }

    if token:
        for customer_id, expected_token in customer_tokens.items():
            if expected_token and compare_digest(token, expected_token):
                return customer_id

    raise HTTPException(
        status_code=401,
        detail="Valid authentication token required"
    )


@app.post("/protected/refunds")
def protected_refund(
    request: ProtectedRefundRequest,
    customer_id: str = Depends(get_authenticated_customer)
):
    order = orders.get(request.order_id)

    if order is None:
        raise HTTPException(404, "Order not found")

    if order["customer_id"] != customer_id:
        raise HTTPException(403, "You do not own this order")

    if not order["eligible"]:
        raise HTTPException(403, "Order is not eligible")

    if order["refunded"]:
        raise HTTPException(409, "Order already refunded")

    if request.amount_cents != order["total_cents"]:
        raise HTTPException(400, "Refund amount is incorrect")

    order["refunded"] = True

    return {
        "status": "simulated_refund_approved",
        "order_id": request.order_id,
        "customer_id": customer_id,
        "amount_cents": request.amount_cents
    }
