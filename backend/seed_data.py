import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app import models


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("开始插入测试数据...")

        leaders_data = [
            {"name": "张团长", "phone": "13800000001", "wechat": "zhangleader1"},
            {"name": "李团长", "phone": "13800000002", "wechat": "lileader2"},
            {"name": "王团长", "phone": "13800000003", "wechat": "wangleader3"},
            {"name": "赵团长", "phone": "13800000004", "wechat": "zhaoleader4"},
            {"name": "刘团长", "phone": "13800000005", "wechat": "liuleader5"},
        ]
        leaders = []
        for data in leaders_data:
            leader = models.Leader(**data)
            db.add(leader)
            leaders.append(leader)
        db.flush()

        pickup_points_data = [
            {
                "name": "阳光花园东门便利店",
                "address": "朝阳区望京街道阳光花园1号楼底商便利店",
                "community": "阳光花园",
                "latitude": 39.9971,
                "longitude": 116.4774,
                "leader_id": leaders[0].id
            },
            {
                "name": "翠湖小区南门驿站",
                "address": "海淀区西三旗翠湖小区南门菜鸟驿站",
                "community": "翠湖小区",
                "latitude": 40.0589,
                "longitude": 116.3535,
                "leader_id": leaders[1].id
            },
            {
                "name": "万科城市花园物业",
                "address": "丰台区花乡万科城市花园物业服务中心",
                "community": "万科城市花园",
                "latitude": 39.8236,
                "longitude": 116.3233,
                "leader_id": leaders[2].id
            },
            {
                "name": "龙湖天街北区快递点",
                "address": "大兴区亦庄龙湖天街北区B1快递代收点",
                "community": "龙湖天街",
                "latitude": 39.7912,
                "longitude": 116.5079,
                "leader_id": leaders[3].id
            },
            {
                "name": "金茂悦小区自提点",
                "address": "通州区梨园金茂悦小区东门岗亭",
                "community": "金茂悦小区",
                "latitude": 39.8945,
                "longitude": 116.6548,
                "leader_id": leaders[4].id
            },
        ]
        points = []
        for data in pickup_points_data:
            point = models.PickupPoint(**data)
            db.add(point)
            points.append(point)
        db.flush()

        products_data = [
            {"name": "有机西红柿", "sku": "VEG001", "unit": "斤", "price": 6.8, "category": "蔬菜"},
            {"name": "山东黄瓜", "sku": "VEG002", "unit": "斤", "price": 4.5, "category": "蔬菜"},
            {"name": "云南生菜", "sku": "VEG003", "unit": "斤", "price": 5.2, "category": "蔬菜"},
            {"name": "土豆", "sku": "VEG004", "unit": "斤", "price": 3.0, "category": "蔬菜"},
            {"name": "胡萝卜", "sku": "VEG005", "unit": "斤", "price": 3.8, "category": "蔬菜"},
            {"name": "烟台红富士苹果", "sku": "FRU001", "unit": "斤", "price": 8.9, "category": "水果"},
            {"name": "海南香蕉", "sku": "FRU002", "unit": "斤", "price": 5.5, "category": "水果"},
            {"name": "赣南脐橙", "sku": "FRU003", "unit": "斤", "price": 7.2, "category": "水果"},
            {"name": "阳光玫瑰葡萄", "sku": "FRU004", "unit": "斤", "price": 15.8, "category": "水果"},
            {"name": "土鸡蛋", "sku": "EGG001", "unit": "份", "price": 25.0, "category": "肉蛋"},
            {"name": "散养柴鸡蛋", "sku": "EGG002", "unit": "份", "price": 32.0, "category": "肉蛋"},
            {"name": "鲜牛奶", "sku": "DAI001", "unit": "份", "price": 12.0, "category": "乳品"},
            {"name": "原味酸奶", "sku": "DAI002", "unit": "份", "price": 18.0, "category": "乳品"},
        ]
        products = []
        for data in products_data:
            product = models.Product(**data)
            db.add(product)
            products.append(product)
        db.flush()

        today = date.today()

        orders_data = [
            {
                "customer_name": "陈女士",
                "customer_phone": "13911110001",
                "pickup_point_idx": 0,
                "items": [(0, 2.5), (1, 1.8), (9, 1)],
                "remark": "西红柿要熟一点的"
            },
            {
                "customer_name": "周先生",
                "customer_phone": "13911110002",
                "pickup_point_idx": 0,
                "items": [(2, 1.2), (3, 3.0), (5, 2.0), (11, 2)],
                "remark": ""
            },
            {
                "customer_name": "吴阿姨",
                "customer_phone": "13911110003",
                "pickup_point_idx": 0,
                "items": [(4, 1.5), (6, 2.0), (9, 1)],
                "remark": "下午3点后取"
            },
            {
                "customer_name": "郑先生",
                "customer_phone": "13911110004",
                "pickup_point_idx": 1,
                "items": [(0, 3.0), (1, 2.0), (5, 3.0), (7, 2.5)],
                "remark": ""
            },
            {
                "customer_name": "孙女士",
                "customer_phone": "13911110005",
                "pickup_point_idx": 1,
                "items": [(3, 2.0), (8, 1.0), (10, 1), (12, 1)],
                "remark": "葡萄要新鲜的"
            },
            {
                "customer_name": "马先生",
                "customer_phone": "13911110006",
                "pickup_point_idx": 1,
                "items": [(2, 2.0), (4, 1.0), (6, 3.0)],
                "remark": ""
            },
            {
                "customer_name": "朱阿姨",
                "customer_phone": "13911110007",
                "pickup_point_idx": 2,
                "items": [(0, 2.0), (2, 1.5), (9, 2)],
                "remark": "多给几个袋子"
            },
            {
                "customer_name": "胡先生",
                "customer_phone": "13911110008",
                "pickup_point_idx": 2,
                "items": [(1, 2.5), (3, 2.5), (5, 2.0), (11, 1)],
                "remark": ""
            },
            {
                "customer_name": "林女士",
                "customer_phone": "13911110009",
                "pickup_point_idx": 3,
                "items": [(7, 3.0), (8, 1.5), (12, 2)],
                "remark": "帮我放冷藏柜"
            },
            {
                "customer_name": "何先生",
                "customer_phone": "13911110010",
                "pickup_point_idx": 3,
                "items": [(0, 1.5), (1, 1.5), (2, 1.5), (3, 1.5), (4, 1.0)],
                "remark": ""
            },
            {
                "customer_name": "郭女士",
                "customer_phone": "13911110011",
                "pickup_point_idx": 3,
                "items": [(5, 4.0), (6, 2.0), (9, 1), (10, 1)],
                "remark": ""
            },
            {
                "customer_name": "罗先生",
                "customer_phone": "13911110012",
                "pickup_point_idx": 3,
                "items": [(8, 2.0), (11, 1), (12, 1)],
                "remark": "尽快送达"
            },
            {
                "customer_name": "高阿姨",
                "customer_phone": "13911110013",
                "pickup_point_idx": 4,
                "items": [(0, 2.0), (5, 2.5), (7, 2.0)],
                "remark": ""
            },
            {
                "customer_name": "梁先生",
                "customer_phone": "13911110014",
                "pickup_point_idx": 4,
                "items": [(1, 2.0), (2, 1.0), (3, 3.0), (4, 2.0), (11, 2)],
                "remark": ""
            },
            {
                "customer_name": "宋女士",
                "customer_phone": "13911110015",
                "pickup_point_idx": 4,
                "items": [(6, 3.0), (8, 1.0), (9, 1), (12, 2)],
                "remark": "牛奶要最近日期"
            },
        ]

        import time
        for i, data in enumerate(orders_data):
            order_no = f"ORD{today.strftime('%Y%m%d')}{i+1:05d}"
            order = models.Order(
                order_no=order_no,
                customer_name=data["customer_name"],
                customer_phone=data["customer_phone"],
                pickup_point_id=points[data["pickup_point_idx"]].id,
                delivery_date=today,
                remark=data["remark"],
                status="pending"
            )
            for p_idx, qty in data["items"]:
                order.order_items.append(models.OrderItem(
                    product_id=products[p_idx].id,
                    quantity=qty
                ))
            db.add(order)
            time.sleep(0.001)

        db.commit()
        print(f"数据插入完成！")
        print(f"  团长: {len(leaders)} 个")
        print(f"  自提点: {len(points)} 个")
        print(f"  商品: {len(products)} 个")
        print(f"  订单: {len(orders_data)} 个")
        print(f"配送日期: {today.isoformat()}")

    except Exception as e:
        db.rollback()
        print(f"插入数据出错: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
