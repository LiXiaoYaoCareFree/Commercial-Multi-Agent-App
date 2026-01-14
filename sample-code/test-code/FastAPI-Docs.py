from typing import List

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

# ---------------------
# 定义分组元数据
# ---------------------
tags_metadata = [
    {
        "name": "用户相关",
        "description": "包含 **用户注册、登录、查询** 等接口。",
    },
    {
        "name": "订单相关",
        "description": "订单的增删改查接口，可以用于订单管理。",
        "externalDocs": {
            "description": "查看更多文档",
            "url": "https://example.com/orders-docs",
        },
    },
]

# ---------------------
# 初始化 FastAPI
# ---------------------
app = FastAPI(
    title="我的API文档",
    description="这是一个演示 **FastAPI Swagger** 的文档，支持分组和详细说明。",
    openapi_tags=tags_metadata,
    version="1.0.0",
)


# ---------------------
# 定义数据模型
# ---------------------
class User(BaseModel):
    id: int
    name: str


class Order(BaseModel):
    id: int
    item: str
    price: float


# ---------------------
# 用户相关路由
# ---------------------
user_router = APIRouter(prefix="/users", tags=["用户相关"])


@user_router.get("/", response_model=List[User], summary="获取用户列表", description="分页获取系统中的用户信息")
async def get_users():
    return [User(id=1, name="Alice"), User(id=2, name="Bob")]


@user_router.post("/", response_model=User, summary="创建新用户", description="提交用户信息，创建一个新用户。")
async def create_user(user: User):
    return user


# ---------------------
# 订单相关路由
# ---------------------
order_router = APIRouter(prefix="/orders", tags=["订单相关"])


@order_router.get("/", response_model=List[Order], summary="获取订单列表", description="查询用户的所有订单。")
async def get_orders():
    return [
        Order(id=101, item="Book", price=29.9),
        Order(id=102, item="Laptop", price=5999.0),
    ]


@order_router.post("/", response_model=Order, summary="创建订单", description="根据传入的订单信息创建新订单。")
async def create_order(order: Order):
    return order


# ---------------------
# 注册路由
# ---------------------
app.include_router(user_router)
app.include_router(order_router)
