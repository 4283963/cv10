from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/products", tags=["商品管理"])


@router.get("", response_model=List[schemas.Product])
def list_products(category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Product)
    if category:
        q = q.filter(models.Product.category == category)
    return q.order_by(models.Product.id).all()


@router.post("", response_model=schemas.Product)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.sku == data.sku).first()
    if p:
        raise HTTPException(status_code=400, detail="SKU已存在")
    product = models.Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
