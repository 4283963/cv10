from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class LeaderBase(BaseModel):
    name: str
    phone: str
    wechat: Optional[str] = None


class LeaderCreate(LeaderBase):
    pass


class Leader(LeaderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PickupPointBase(BaseModel):
    name: str
    address: str
    community: str
    latitude: float
    longitude: float
    leader_id: int


class PickupPointCreate(PickupPointBase):
    pass


class PickupPoint(PickupPointBase):
    id: int
    created_at: datetime
    leader: Optional[Leader] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    sku: str
    unit: str
    price: float
    category: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItemBase(BaseModel):
    product_id: int
    quantity: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    product: Product

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_name: str
    customer_phone: str
    pickup_point_id: int
    delivery_date: date
    remark: Optional[str] = None


class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]


class Order(OrderBase):
    id: int
    order_no: str
    status: str
    created_at: datetime
    order_items: List[OrderItem] = []

    class Config:
        from_attributes = True


class OrderWithPickupPoint(Order):
    pickup_point: PickupPoint


class PackingSlipItemBase(BaseModel):
    product_id: int
    total_quantity: float


class PackingSlipItem(PackingSlipItemBase):
    id: int
    product: Product

    class Config:
        from_attributes = True


class PackingSlipOrderLink(BaseModel):
    id: int
    order: Order

    class Config:
        from_attributes = True


class PackingSlipBase(BaseModel):
    pickup_point_id: int
    delivery_date: date


class PackingSlipCreate(PackingSlipBase):
    order_ids: List[int]


class PackingSlip(PackingSlipBase):
    id: int
    slip_no: str
    total_orders: int
    status: str
    created_at: datetime
    pickup_point: PickupPoint
    items: List[PackingSlipItem] = []
    order_links: List[PackingSlipOrderLink] = []

    class Config:
        from_attributes = True


class PickupPointWithDistance(PickupPoint):
    distance_km: float
    order_count: int


class DeliveryRoutePoint(BaseModel):
    sequence: int
    pickup_point: PickupPoint
    distance_km: float
    order_count: int
    total_items: int
    packing_slip_id: Optional[int] = None
    slip_no: Optional[str] = None
    status: Optional[str] = None


class DeliveryRoute(BaseModel):
    warehouse_lat: float
    warehouse_lng: float
    delivery_date: date
    total_points: int
    total_distance_km: float
    route: List[DeliveryRoutePoint]
