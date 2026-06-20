from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from collections import defaultdict
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/packing-slips", tags=["配货单管理"])


def generate_slip_no() -> str:
    return f"PS{datetime.now().strftime('%Y%m%d%H%M%S')}{id(datetime.now()) % 1000:03d}"


@router.get("", response_model=List[schemas.PackingSlip])
def list_packing_slips(
    delivery_date: Optional[date] = None,
    pickup_point_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.PackingSlip)
    if delivery_date:
        q = q.filter(models.PackingSlip.delivery_date == delivery_date)
    if pickup_point_id:
        q = q.filter(models.PackingSlip.pickup_point_id == pickup_point_id)
    return q.order_by(models.PackingSlip.id.desc()).all()


@router.get("/{slip_id}", response_model=schemas.PackingSlip)
def get_packing_slip(slip_id: int, db: Session = Depends(get_db)):
    slip = db.query(models.PackingSlip).filter(models.PackingSlip.id == slip_id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="配货单不存在")
    return slip


@router.get("/grouped/by-pickup-point")
def get_orders_grouped_by_pickup_point(
    delivery_date: date,
    db: Session = Depends(get_db)
):
    pending_orders = (
        db.query(models.Order)
        .filter(
            models.Order.delivery_date == delivery_date,
            models.Order.status == "pending"
        )
        .all()
    )

    grouped = defaultdict(list)
    for order in pending_orders:
        grouped[order.pickup_point_id].append(order)

    result = []
    for point_id, orders in grouped.items():
        point = db.query(models.PickupPoint).filter(models.PickupPoint.id == point_id).first()
        product_summary = defaultdict(float)
        for order in orders:
            for item in order.order_items:
                product_summary[item.product_id] += item.quantity

        summary_items = []
        for product_id, qty in product_summary.items():
            product = db.query(models.Product).filter(models.Product.id == product_id).first()
            summary_items.append({
                "product_id": product_id,
                "product_name": product.name if product else "",
                "sku": product.sku if product else "",
                "unit": product.unit if product else "",
                "total_quantity": qty
            })

        order_list = []
        for order in orders:
            order_list.append({
                "order_id": order.id,
                "order_no": order.order_no,
                "customer_name": order.customer_name,
                "customer_phone": order.customer_phone,
                "remark": order.remark,
                "items": [
                    {
                        "product_id": it.product_id,
                        "product_name": it.product.name,
                        "quantity": it.quantity,
                        "unit": it.product.unit
                    }
                    for it in order.order_items
                ]
            })

        result.append({
            "pickup_point_id": point_id,
            "pickup_point_name": point.name if point else "",
            "address": point.address if point else "",
            "community": point.community if point else "",
            "leader_name": point.leader.name if point and point.leader else "",
            "leader_phone": point.leader.phone if point and point.leader else "",
            "latitude": point.latitude if point else None,
            "longitude": point.longitude if point else None,
            "order_count": len(orders),
            "product_summary": sorted(summary_items, key=lambda x: x["product_name"]),
            "orders": sorted(order_list, key=lambda x: x["order_no"])
        })

    return sorted(result, key=lambda x: x["pickup_point_name"])


@router.post("", response_model=schemas.PackingSlip)
def create_packing_slip(data: schemas.PackingSlipCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.PackingSlip)
        .filter(
            models.PackingSlip.pickup_point_id == data.pickup_point_id,
            models.PackingSlip.delivery_date == data.delivery_date
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="该自提点当日配货单已存在")

    slip = models.PackingSlip(
        slip_no=generate_slip_no(),
        pickup_point_id=data.pickup_point_id,
        delivery_date=data.delivery_date,
        total_orders=len(data.order_ids),
        status="created"
    )

    product_totals = defaultdict(float)
    for oid in data.order_ids:
        order = db.query(models.Order).filter(models.Order.id == oid).first()
        if not order:
            raise HTTPException(status_code=404, detail=f"订单{oid}不存在")
        if order.pickup_point_id != data.pickup_point_id:
            raise HTTPException(status_code=400, detail=f"订单{oid}不属于该自提点")
        if order.delivery_date != data.delivery_date:
            raise HTTPException(status_code=400, detail=f"订单{oid}配送日期不匹配")
        if order.status != "pending":
            raise HTTPException(status_code=400, detail=f"订单{oid}已处理")

        for item in order.order_items:
            product_totals[item.product_id] += item.quantity

        slip.order_links.append(models.PackingSlipOrder(order_id=oid))
        order.status = "packed"

    for pid, qty in product_totals.items():
        slip.items.append(models.PackingSlipItem(product_id=pid, total_quantity=qty))

    db.add(slip)
    db.commit()
    db.refresh(slip)
    return slip


@router.patch("/{slip_id}/status")
def update_slip_status(slip_id: int, status: str, db: Session = Depends(get_db)):
    slip = db.query(models.PackingSlip).filter(models.PackingSlip.id == slip_id).first()
    if not slip:
        raise HTTPException(status_code=404, detail="配货单不存在")
    if status not in ["created", "printed", "loaded"]:
        raise HTTPException(status_code=400, detail="状态不合法")
    slip.status = status
    db.commit()
    return {"success": True, "status": status}
