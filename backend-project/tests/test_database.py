from app.database import SessionLocal
from app.models import Product, Order, OrderItem
from datetime import datetime, timedelta
from sqlalchemy import text


def test_add_product_to_order():
    db = SessionLocal()

    # Создаем продукт
    product = Product(name="Product C", quantity=50, price=15)
    db.add(product)
    db.commit()

    # Создаем заказ
    order = Order(client_name="Client C")
    db.add(order)
    db.commit()

    try:
        # Добавляем товар в заказ
        order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=5)
        db.add(order_item)

        # уменьшаем количество товара на складе в базе данных
        db.query(Product).filter(Product.id == product.id).update({Product.quantity: Product.quantity - 5})

        db.flush()  # Синхронизируем изменения с базой данных
        db.commit()

        # Проверяем, что товар добавлен в заказ
        order_item_db = db.query(OrderItem).filter(OrderItem.order_id == order.id,
                                                   OrderItem.product_id == product.id).first()
        assert order_item_db is not None, "OrderItem не был добавлен"
        assert order_item_db.quantity == 5, f"Expected 5, but got {order_item_db.quantity}"

        # Проверяем, что количество товара на складе уменьшилось
        product_db = db.query(Product).filter(Product.id == product.id).first()
        db.refresh(product_db)  # Обновляем объект товара из базы
        assert product_db.quantity == 45, f"Expected 45, but got {product_db.quantity}"

        # Добавляем еще 3 единицы товара в заказ
        order_item_db.quantity += 3
        db.commit()  # Один коммит для обновлений

        # Проверяем, что количество в заказе обновилось
        db.refresh(order_item_db)
        assert order_item_db.quantity == 8, f"Expected 8, but got {order_item_db.quantity}"

    except Exception as e:
        db.rollback()
        raise e

    db.close()


def test_top_selling_products():
    db = SessionLocal()

    # Создаем несколько продуктов
    product_a = Product(name="Product A", quantity=100, price=10)
    product_b = Product(name="Product B", quantity=100, price=20)
    product_c = Product(name="Product C", quantity=100, price=15)
    db.add_all([product_a, product_b, product_c])
    db.commit()  # Коммит для создания продуктов

    # Создаем заказы
    order_1 = Order(client_name="Client A")
    order_2 = Order(client_name="Client B")
    db.add_all([order_1, order_2])
    db.commit()  # Коммит для создания заказов

    # Добавляем позиции в заказ
    order_item_1 = OrderItem(order_id=order_1.id, product_id=product_a.id, quantity=5)
    order_item_2 = OrderItem(order_id=order_1.id, product_id=product_b.id, quantity=3)
    order_item_3 = OrderItem(order_id=order_2.id, product_id=product_a.id, quantity=8)
    order_item_4 = OrderItem(order_id=order_2.id, product_id=product_c.id, quantity=10)
    db.add_all([order_item_1, order_item_2, order_item_3, order_item_4])
    db.commit()  # Коммит для добавления товаров в заказ

    # Выполним запрос для получения топ-5 самых продаваемых товаров за последний месяц
    last_month = datetime.now() - timedelta(days=30)

    # Используем text() для текстового SQL-запроса
    result = db.execute(
        text("""
            SELECT p.name, SUM(oi.quantity) AS total_sold
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.created_at >= :last_month
            GROUP BY p.id
            ORDER BY total_sold DESC
            LIMIT 5;
        """),
        {'last_month': last_month}
    ).fetchall()

    # Преобразуем результат в список словарей
    result_dict = [
        {"name": row[0], "total_sold": row[1]}  # Поскольку у нас два столбца: name и total_sold
        for row in result
    ]

    # Выводим результаты для отладки
    print("Top 5 best-selling products in the last month:")
    for row in result_dict:
        print(f"Product: {row['name']}, Total Sold: {row['total_sold']}")

    # Проверяем, что результат не пустой
    assert len(result_dict) > 0, "No results found for top-selling products."

    db.close()
