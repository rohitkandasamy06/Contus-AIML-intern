-- ============================================================
-- Analytics Views -- all column names match 01_schema.sql exactly
-- ============================================================

-- 1. Daily production KPIs
CREATE OR REPLACE VIEW vw_daily_production AS
SELECT
    pr.run_date,
    p.category,
    m.line_id,
    SUM(pr.units_produced) AS total_units_produced,
    SUM(pr.units_defective) AS total_units_defective,
    ROUND(SUM(pr.units_defective)::numeric / NULLIF(SUM(pr.units_produced),0) * 100, 2) AS defect_rate_pct
FROM production_runs pr
JOIN products p ON p.product_id = pr.product_id
JOIN machines m ON m.machine_id = pr.machine_id
GROUP BY pr.run_date, p.category, m.line_id;

-- 2. Machine performance summary
CREATE OR REPLACE VIEW vw_machine_performance AS
SELECT
    m.machine_id,
    m.machine_code,
    m.machine_name,
    m.line_id,
    m.status,
    COUNT(pr.run_id) AS total_runs,
    SUM(pr.units_produced) AS total_units,
    SUM(pr.units_defective) AS total_defects,
    ROUND(SUM(pr.units_defective)::numeric / NULLIF(SUM(pr.units_produced),0) * 100, 2) AS defect_rate_pct
FROM machines m
LEFT JOIN production_runs pr ON pr.machine_id = m.machine_id
GROUP BY m.machine_id, m.machine_code, m.machine_name, m.line_id, m.status;

-- 3. Inventory health (stockout risk)
CREATE OR REPLACE VIEW vw_inventory_health AS
SELECT
    w.warehouse_code,
    w.city,
    p.name AS product_name,
    p.category,
    i.quantity_on_hand,
    i.reorder_level,
    CASE WHEN i.quantity_on_hand <= i.reorder_level THEN TRUE ELSE FALSE END AS below_reorder_level
FROM inventory i
JOIN warehouses w ON w.warehouse_id = i.warehouse_id
JOIN products p   ON p.product_id   = i.product_id;

-- 4. Monthly sales/revenue trend
CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    DATE_TRUNC('month', o.order_date)::date AS month,
    p.category,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p     ON p.product_id = oi.product_id
WHERE o.status != 'Cancelled'
GROUP BY DATE_TRUNC('month', o.order_date), p.category;

-- 5. Delivery performance
CREATE OR REPLACE VIEW vw_delivery_performance AS
SELECT
    s.carrier,
    w.city AS warehouse_city,
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN s.delivery_status = 'Delivered On Time' THEN 1 ELSE 0 END) AS on_time_count,
    ROUND(SUM(CASE WHEN s.delivery_status = 'Delivered On Time' THEN 1 ELSE 0 END)::numeric
          / NULLIF(COUNT(*),0) * 100, 2) AS on_time_pct,
    ROUND(AVG(s.delivery_date - s.dispatch_date), 2) AS avg_delivery_days,
    ROUND(AVG(s.distance_km)::numeric, 2) AS avg_distance_km
FROM shipments s
JOIN warehouses w ON w.warehouse_id = s.warehouse_id
WHERE s.delivery_date IS NOT NULL
GROUP BY s.carrier, w.city;

-- 6. Customer geo sales (for map)
CREATE OR REPLACE VIEW vw_customer_geo_sales AS
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_type,
    c.city,
    c.state,
    c.latitude,
    c.longitude,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.unit_price) AS lifetime_value
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
WHERE o.status != 'Cancelled'
GROUP BY c.customer_id, c.customer_name, c.customer_type,
         c.city, c.state, c.latitude, c.longitude;

-- 7. Support ticket metrics
CREATE OR REPLACE VIEW vw_ticket_metrics AS
SELECT
    DATE_TRUNC('month', opened_at)::date AS month,
    issue_type,
    priority,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN status IN ('Resolved','Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
    ROUND(AVG(EXTRACT(EPOCH FROM (resolved_at - opened_at)) / 3600)::numeric, 2) AS avg_resolution_hours
FROM support_tickets
GROUP BY DATE_TRUNC('month', opened_at), issue_type, priority;

-- 8. Defect to complaint linkage
CREATE OR REPLACE VIEW vw_defect_to_complaint AS
SELECT
    p.name AS product_name,
    p.category,
    SUM(pr.units_defective) AS total_defects_produced,
    COUNT(DISTINCT st.ticket_id) FILTER (WHERE st.issue_type = 'Quality Defect') AS defect_related_tickets
FROM products p
LEFT JOIN production_runs pr ON pr.product_id = p.product_id
LEFT JOIN order_items oi     ON oi.product_id = p.product_id
LEFT JOIN orders o           ON o.order_id    = oi.order_id
LEFT JOIN support_tickets st ON st.order_id   = o.order_id
GROUP BY p.name, p.category;