-- Запрос для получения топ-5 самых продаваемых товаров за последний месяц
SELECT p.name, SUM(oi.quantity) AS total_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.id
WHERE oi.created_at >= NOW() - INTERVAL '1 month'
GROUP BY p.id
ORDER BY total_sold DESC
LIMIT 5;
