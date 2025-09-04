from typing import Optional

from pydantic import BaseModel
from datetime import datetime

class OrderItem(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
