from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routers import pickup_points, products, orders, packing_slips, delivery


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("[INFO] 数据库表初始化完成")
    except Exception as e:
        print(f"[WARN] 数据库初始化失败（请确认MySQL是否就绪）: {e}")
    yield


app = FastAPI(
    title="生鲜配货管理系统",
    description="仓库管理员分拣配货与送货指引系统",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pickup_points.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(packing_slips.router)
app.include_router(delivery.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "生鲜配货管理系统运行中"}
