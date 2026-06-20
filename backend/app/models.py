from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Leader(Base):
    __tablename__ = "leaders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="团长姓名")
    phone = Column(String(20), nullable=False, comment="团长电话")
    wechat = Column(String(100), nullable=True, comment="微信号")
    created_at = Column(DateTime, server_default=func.now())

    pickup_points = relationship("PickupPoint", back_populates="leader")


class PickupPoint(Base):
    __tablename__ = "pickup_points"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="自提点名称")
    address = Column(String(255), nullable=False, comment="自提点详细地址")
    community = Column(String(100), nullable=False, comment="所属小区")
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    leader_id = Column(Integer, ForeignKey("leaders.id"), nullable=False, comment="团长ID")
    created_at = Column(DateTime, server_default=func.now())

    leader = relationship("Leader", back_populates="pickup_points")
    orders = relationship("Order", back_populates="pickup_point")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="商品名称")
    sku = Column(String(50), nullable=False, unique=True, comment="商品编码")
    unit = Column(String(20), nullable=False, comment="单位(斤/份/个)")
    price = Column(Float, nullable=False, comment="单价")
    category = Column(String(50), nullable=True, comment="分类(蔬菜/水果/肉蛋...)")
    created_at = Column(DateTime, server_default=func.now())

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(String(50), nullable=False, unique=True, comment="订单号")
    customer_name = Column(String(50), nullable=False, comment="客户姓名")
    customer_phone = Column(String(20), nullable=False, comment="客户电话")
    pickup_point_id = Column(Integer, ForeignKey("pickup_points.id"), nullable=False, comment="自提点ID")
    delivery_date = Column(Date, nullable=False, comment="配送日期")
    remark = Column(Text, nullable=True, comment="备注")
    status = Column(String(20), nullable=False, default="pending", comment="状态:pending待配货/packed已打包/delivered已送达")
    created_at = Column(DateTime, server_default=func.now())

    pickup_point = relationship("PickupPoint", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="订单ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="商品ID")
    quantity = Column(Float, nullable=False, comment="数量")
    created_at = Column(DateTime, server_default=func.now())

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


class PackingSlip(Base):
    __tablename__ = "packing_slips"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slip_no = Column(String(50), nullable=False, unique=True, comment="配货单号")
    pickup_point_id = Column(Integer, ForeignKey("pickup_points.id"), nullable=False, comment="自提点ID")
    delivery_date = Column(Date, nullable=False, comment="配送日期")
    total_orders = Column(Integer, nullable=False, default=0, comment="订单总数")
    status = Column(String(20), nullable=False, default="created", comment="状态:created已创建/printed已打印/loaded已装车")
    created_at = Column(DateTime, server_default=func.now())

    pickup_point = relationship("PickupPoint")
    items = relationship("PackingSlipItem", back_populates="slip", cascade="all, delete-orphan")
    order_links = relationship("PackingSlipOrder", back_populates="slip", cascade="all, delete-orphan")


class PackingSlipItem(Base):
    __tablename__ = "packing_slip_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slip_id = Column(Integer, ForeignKey("packing_slips.id"), nullable=False, comment="配货单ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="商品ID")
    total_quantity = Column(Float, nullable=False, comment="总数量")
    created_at = Column(DateTime, server_default=func.now())

    slip = relationship("PackingSlip", back_populates="items")
    product = relationship("Product")


class PackingSlipOrder(Base):
    __tablename__ = "packing_slip_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slip_id = Column(Integer, ForeignKey("packing_slips.id"), nullable=False, comment="配货单ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="订单ID")
    created_at = Column(DateTime, server_default=func.now())

    slip = relationship("PackingSlip", back_populates="order_links")
    order = relationship("Order")
