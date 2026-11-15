from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.db.session import SessionDep
from app.models.product import Product

router = APIRouter(prefix="/products", tags=["products"])


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    category: str
    product_type: str
    brand: str
    price: int
    stock: int
    rating: Decimal | None
    description: str | None
    attributes: dict[str, Any]
    created_at: datetime


@router.get("/", response_model=list[ProductOut])
async def list_products(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    result = await session.scalars(
        select(Product).order_by(Product.id).limit(limit).offset(offset)
    )
    return result.all()


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, session: SessionDep):
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
