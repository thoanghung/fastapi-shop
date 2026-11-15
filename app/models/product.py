from datetime import datetime
from decimal import Decimal
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Product(Base):
    # Table is created by scripts/import_products.sql
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sku: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    category: Mapped[str]
    product_type: Mapped[str]
    brand: Mapped[str]
    price: Mapped[int]  # VND
    stock: Mapped[int] = mapped_column(default=0)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(2, 1))
    description: Mapped[str | None]
    attributes: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), deferred=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
