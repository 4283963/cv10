from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/orders", tags=["订单管理"])


def generate_order_no() -> str:
    return f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{id(datetime.now()) % 1000:03d}"


@router.get("", response_model=List[schemas.OrderWithPickupPoint])
def list_orders(
    delivery_date: Optional[date] = None,
    pickup_point_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.Order)
    if delivery_date:
        q = q.filter(models.Order.delivery_date == delivery_date)
    if pickup_point_id:
        q = q.filter(models.Order.pickup_point_id == pickup_point_id)
    if status:
        q = q.filter(models.Order.status == status)
    return q.order_by(models.Order.id.desc()).all()


@router.get("/{order_id}", response_model=schemas.OrderWithPickupPoint)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.post("", response_model=schemas.Order)
def create_order(data: schemas.OrderCreate, db: Session = Depends(get_db)):
    order = models.Order(
        order_no=generate_order_no(),
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        pickup_point_id=data.pickup_point_id,
        delivery_date=data.delivery_date,
        remark=data.remark,
        status="pending"
    )
    for item in data.order_items:
        db_item = models.OrderItem(**item.model_dump())
        order.order_items.append(db_item)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if status not in ["pending", "packed", "delivered"]:
        raise HTTPException(status_code=400, detail="状态不合法")
    order.status = status
    db.commit()
    return {"success": True, "status": status}
