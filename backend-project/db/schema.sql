CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    quantity INTEGER,
    price INTEGER
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    client_name VARCHAR(255)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER
);
