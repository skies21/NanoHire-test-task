from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Product, Order, OrderItem
from app.schemas import OrderItem as OrderItemSchema
from app.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/add_to_order/")
async def add_to_order(item: OrderItemSchema, db: Session = Depends(get_db)):
    # Проверка наличия товара в базе
    product = db.query(Product).filter(Product.id == item.product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.quantity < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough product in stock")

    # Получаем заказ по ID
    order = db.query(Order).filter(Order.id == item.order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Проверка, есть ли товар уже в заказе
    order_item = db.query(OrderItem).filter(OrderItem.order_id == item.order_id,
                                            OrderItem.product_id == item.product_id).first()

    if order_item:
        # Если товар уже в заказе, обновляем его количество
        order_item.quantity += item.quantity
        db.commit()

        # Уменьшаем количество товара в базе
        product.quantity -= item.quantity
        db.commit()

        # Получаем актуальное значение из базы данных
        db.refresh(order_item)
        db.refresh(product)

        return {"message": "Product quantity updated"}

    # Если товара нет в заказе, добавляем новый элемент
    new_order_item = OrderItem(order_id=item.order_id, product_id=item.product_id, quantity=item.quantity)
    db.add(new_order_item)

    product.quantity -= item.quantity
    db.commit()

    db.refresh(new_order_item)
    db.refresh(product)

    return {"message": "Product added to order"}
