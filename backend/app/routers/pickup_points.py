from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/pickup-points", tags=["自提点管理"])


@router.get("", response_model=List[schemas.PickupPoint])
def list_pickup_points(db: Session = Depends(get_db)):
    points = db.query(models.PickupPoint).order_by(models.PickupPoint.id).all()
    return points


@router.get("/{point_id}", response_model=schemas.PickupPoint)
def get_pickup_point(point_id: int, db: Session = Depends(get_db)):
    point = db.query(models.PickupPoint).filter(models.PickupPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="自提点不存在")
    return point


@router.post("", response_model=schemas.PickupPoint)
def create_pickup_point(data: schemas.PickupPointCreate, db: Session = Depends(get_db)):
    point = models.PickupPoint(**data.model_dump())
    db.add(point)
    db.commit()
    db.refresh(point)
    return point
