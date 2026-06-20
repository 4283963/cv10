# 生鲜配货管理系统

一个面向仓库管理员的生鲜配送管理系统，包含分拣配货和送货指引两大核心功能。

## 技术栈

**前端**
- Vue 3 (Composition API)
- Element Plus (UI组件库)
- Vue Router (路由)
- Axios (HTTP请求)
- Vite (构建工具)

**后端**
- FastAPI (Web框架)
- SQLAlchemy 2.0 (ORM)
- PyMySQL (MySQL驱动)
- Pydantic v2 (数据校验)
- Uvicorn (ASGI服务器)

**数据库**
- MySQL 8.0+

## 项目目录结构

```
cv10/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── routers/         # API路由
│   │   │   ├── orders.py
│   │   │   ├── packing_slips.py
│   │   │   ├── pickup_points.py
│   │   │   ├── products.py
│   │   │   └── delivery.py
│   │   ├── utils/
│   │   │   └── distance.py  # Haversine距离算法
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI入口
│   │   ├── config.py        # 配置
│   │   ├── database.py      # 数据库连接
│   │   ├── models.py        # SQLAlchemy模型
│   │   └── schemas.py       # Pydantic Schema
│   ├── seed_data.py         # 测试数据初始化脚本
│   └── requirements.txt     # Python依赖
│
└── frontend/                # 前端项目
    ├── src/
    │   ├── api/             # API封装
    │   │   ├── index.js
    │   │   └── request.js
    │   ├── router/
    │   │   └── index.js     # 路由配置
    │   ├── views/           # 页面组件
    │   │   ├── Packing.vue  # 分拣配货页
    │   │   └── Delivery.vue # 送货指引页
    │   ├── App.vue          # 根组件
    │   ├── main.js          # 入口
    │   └── style.css        # 全局样式
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## 数据库设计

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| leaders | 团长 | name, phone, wechat |
| pickup_points | 自提点 | name, address, community, latitude, longitude, leader_id |
| products | 商品 | name, sku, unit, price, category |
| orders | 订单 | order_no, customer_name, customer_phone, pickup_point_id, delivery_date, status |
| order_items | 订单明细 | order_id, product_id, quantity |
| packing_slips | 配货单 | slip_no, pickup_point_id, delivery_date, total_orders, status |
| packing_slip_items | 配货单商品汇总 | slip_id, product_id, total_quantity |
| packing_slip_orders | 配货单订单关联 | slip_id, order_id |

## 快速启动

### 1. 准备 MySQL 数据库

```sql
CREATE DATABASE fresh_delivery
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

> 默认数据库连接配置（可通过 `backend/app/config.py` 或环境变量修改）：
> - 主机: `127.0.0.1`
> - 端口: `3306`
> - 用户: `root`
> - 密码: `root`
> - 数据库: `fresh_delivery`

### 2. 启动后端服务

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化测试数据（团长/自提点/商品/订单）
python seed_data.py

# 启动服务（端口 8000）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API 文档地址: http://127.0.0.1:8000/docs
- 健康检查: http://127.0.0.1:8000/api/health

### 3. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install
# 或使用 yarn / pnpm
# yarn install
# pnpm install

# 启动开发服务（端口 5173）
npm run dev
```

浏览器访问: http://localhost:5173

## 功能说明

### 分拣配货页面

- 按**配送日期**查询当日待处理订单
- 订单**按自提点自动分组**，显示每个自提点：
  - 团长信息与联系方式
  - 订单数与商品种类汇总
  - 商品分拣清单（含数量汇总）
  - 逐单客户明细
- 一键**生成配货单**：自动汇总所有订单商品、将订单状态标记为"已打包"
- 顶部统计卡片实时显示：待配货自提点、待处理订单、商品种类、已生成配货单数

### 送货指引页面

- 基于自提点**经纬度**，使用 Haversine 公式计算距离仓库的球面距离
- **按距离由近到远自动排序**送货顺序
- 左侧 SVG **路线图**：直观展示仓库到各自提点的送货顺序
- 右侧时间轴式**送货清单**：
  - 每站显示自提点地址、团长信息、配货单号
  - 显示订单数、商品件数
  - 支持"标记已装车"状态流转
- 支持切换"仅已打包"或"含未打包"视图
- 显示总里程、总送货点数、总订单数等统计信息

## 主要 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/orders` | 订单列表（按日期/自提点过滤） |
| POST | `/api/orders` | 创建订单 |
| GET | `/api/packing-slips/grouped/by-pickup-point` | 按自提点分组获取待配货订单 |
| POST | `/api/packing-slips` | 生成配货单 |
| GET | `/api/delivery/route` | 获取已配货送货路线 |
| GET | `/api/delivery/route-without-packing` | 获取完整送货路线（含未打包） |
| PATCH | `/api/packing-slips/{id}/status` | 更新配货单状态 |
