
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
