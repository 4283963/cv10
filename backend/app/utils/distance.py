import math


def _validate_lat_lon(lat: float, lon: float, name: str = ""):
    """
    校验经纬度合法性。
    - 纬度 latitude  范围 [-90, 90]
    - 经度 longitude 范围 [-180, 180]
    在中国地区（东经73-135，北纬3-54）如果数值被写反会立刻被发现。
    """
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(
            f"{'(' + name + ')' if name else ''}纬度 latitude={lat} 不合法，"
            f"应在 [-90, 90] 范围内。若经纬度写反了，请检查参数顺序 (lat, lon)。"
        )
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(
            f"{'(' + name + ')' if name else ''}经度 longitude={lon} 不合法，"
            f"应在 [-180, 180] 范围内。若经纬度写反了，请检查参数顺序 (lat, lon)。"
        )


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    使用 Haversine 公式计算两个 GPS 坐标之间的球面距离（单位：公里）。
    参数顺序必须是 (纬度, 经度)，否则会抛错或结果荒谬。
    """
    _validate_lat_lon(lat1, lon1, name="起点")
    _validate_lat_lon(lat2, lon2, name="终点")

    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
