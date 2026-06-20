from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from ..database import get_db
from .. import models
from ..utils.distance import haversine_distance

router = APIRouter(prefix="/api/delivery", tags=["送货指引"])

WAREHOUSE_LAT = 39.9042
WAREHOUSE_LNG = 116.4074


@router.get("/route")
def get_delivery_route(
    delivery_date: date,
    warehouse_lat: Optional[float] = None,
    warehouse_lng: Optional[float] = None,
    db: Session = Depends(get_db)
):
    wh_lat = warehouse_lat or WAREHOUSE_LAT
    wh_lng = warehouse_lng or WAREHOUSE_LNG

    packing_slips = (
        db.query(models.PackingSlip)
        .filter(models.PackingSlip.delivery_date == delivery_date)
        .all()
    )

    route_points = []
    for slip in packing_slips:
        point = slip.pickup_point
        dist = haversine_distance(wh_lat, wh_lng, point.latitude, point.longitude)

        total_items = sum(item.total_quantity for item in slip.items)
        order_count = len(slip.order_links)

        route_points.append({
            "pickup_point": {
                "id": point.id,
                "name": point.name,
                "address": point.address,
                "community": point.community,
                "latitude": point.latitude,
                "longitude": point.longitude,
                "leader_id": point.leader_id,
                "leader": {
                    "id": point.leader.id,
                    "name": point.leader.name,
                    "phone": point.leader.phone,
                    "wechat": point.leader.wechat,
                    "created_at": point.leader.created_at
                } if point.leader else None,
                "created_at": point.created_at
            },
            "distance_km": round(dist, 2),
            "order_count": order_count,
            "total_items": round(total_items, 1),
            "packing_slip_id": slip.id,
            "slip_no": slip.slip_no,
            "status": slip.status
        })

    route_points.sort(key=lambda x: x["distance_km"])

    for i, point in enumerate(route_points):
        point["sequence"] = i + 1

    total_distance = sum(p["distance_km"] for p in route_points)

    return {
        "warehouse_lat": wh_lat,
        "warehouse_lng": wh_lng,
        "delivery_date": delivery_date.isoformat(),
        "total_points": len(route_points),
        "total_distance_km": round(total_distance, 2),
        "route": route_points
    }


@router.get("/route-without-packing")
def get_route_without_packing(
    delivery_date: date,
    warehouse_lat: Optional[float] = None,
    warehouse_lng: Optional[float] = None,
    db: Session = Depends(get_db)
):
    wh_lat = warehouse_lat or WAREHOUSE_LAT
    wh_lng = warehouse_lng or WAREHOUSE_LNG

    pending_orders = (
        db.query(models.Order)
        .filter(models.Order.delivery_date == delivery_date)
        .all()
    )

    point_map = {}
    for order in pending_orders:
        pid = order.pickup_point_id
        if pid not in point_map:
            point_map[pid] = {
                "order_count": 0,
                "total_items": 0
            }
        point_map[pid]["order_count"] += 1
        point_map[pid]["total_items"] += sum(it.quantity for it in order.order_items)

    route_points = []
    for pid, stats in point_map.items():
        point = db.query(models.PickupPoint).filter(models.PickupPoint.id == pid).first()
        if not point:
            continue
        dist = haversine_distance(wh_lat, wh_lng, point.latitude, point.longitude)

        slip = (
            db.query(models.PackingSlip)
            .filter(
                models.PackingSlip.pickup_point_id == pid,
                models.PackingSlip.delivery_date == delivery_date
            )
            .first()
        )

        route_points.append({
            "pickup_point": {
                "id": point.id,
                "name": point.name,
                "address": point.address,
                "community": point.community,
                "latitude": point.latitude,
                "longitude": point.longitude,
                "leader_id": point.leader_id,
                "leader": {
                    "id": point.leader.id,
                    "name": point.leader.name,
                    "phone": point.leader.phone,
                    "wechat": point.leader.wechat,
                    "created_at": point.leader.created_at
                } if point.leader else None,
                "created_at": point.created_at
            },
            "distance_km": round(dist, 2),
            "order_count": stats["order_count"],
            "total_items": round(stats["total_items"], 1),
            "packing_slip_id": slip.id if slip else None,
            "slip_no": slip.slip_no if slip else None,
            "status": slip.status if slip else None
        })

    route_points.sort(key=lambda x: x["distance_km"])

    for i, point in enumerate(route_points):
        point["sequence"] = i + 1

    total_distance = sum(p["distance_km"] for p in route_points)

    return {
        "warehouse_lat": wh_lat,
        "warehouse_lng": wh_lng,
        "delivery_date": delivery_date.isoformat(),
        "total_points": len(route_points),
        "total_distance_km": round(total_distance, 2),
        "route": route_points
    }
