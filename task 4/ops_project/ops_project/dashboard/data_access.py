"""
data_access.py - All queries use exact column names from schema
"""
import pandas as pd
from db_config import get_engine

engine = get_engine()

def get_warehouses():
    df = pd.read_sql("SELECT DISTINCT city FROM warehouses ORDER BY city", engine)
    return ["All"] + df["city"].tolist()

def get_categories():
    df = pd.read_sql("SELECT DISTINCT category FROM products ORDER BY category", engine)
    return ["All"] + df["category"].tolist()

def get_carriers():
    df = pd.read_sql("SELECT DISTINCT carrier FROM shipments ORDER BY carrier", engine)
    return ["All"] + df["carrier"].tolist()

def get_date_range():
    df = pd.read_sql("SELECT MIN(order_date) AS min_date, MAX(order_date) AS max_date FROM orders", engine)
    return df["min_date"][0], df["max_date"][0]

def get_kpis(start_date, end_date):
    query = f"""
        SELECT
            COUNT(DISTINCT o.order_id)              AS total_orders,
            ROUND(SUM(oi.quantity * oi.unit_price)::numeric, 2) AS total_revenue,
            ROUND(AVG(oi.quantity * oi.unit_price)::numeric, 2) AS avg_order_value,
            SUM(oi.quantity)                        AS total_units_sold
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
        AND o.status != 'Cancelled'
    """
    return pd.read_sql(query, engine).iloc[0]

def get_production_kpis(start_date, end_date):
    query = f"""
        SELECT
            SUM(units_produced)   AS total_produced,
            SUM(units_defective)  AS total_defective,
            ROUND(SUM(units_defective)::numeric / NULLIF(SUM(units_produced),0) * 100, 2) AS defect_rate_pct
        FROM production_runs
        WHERE run_date BETWEEN '{start_date}' AND '{end_date}'
    """
    return pd.read_sql(query, engine).iloc[0]

def get_monthly_revenue(start_date, end_date, category="All"):
    cat_filter = f"AND p.category = '{category}'" if category != "All" else ""
    query = f"""
        SELECT
            DATE_TRUNC('month', o.order_date)::date AS month,
            SUM(oi.quantity * oi.unit_price)        AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        JOIN products p     ON p.product_id = oi.product_id
        WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
        AND o.status != 'Cancelled'
        {cat_filter}
        GROUP BY 1 ORDER BY 1
    """
    return pd.read_sql(query, engine)

def get_monthly_production(start_date, end_date):
    query = f"""
        SELECT
            DATE_TRUNC('month', run_date)::date AS month,
            SUM(units_produced)                 AS total_produced,
            SUM(units_defective)                AS total_defective,
            ROUND(SUM(units_defective)::numeric / NULLIF(SUM(units_produced),0) * 100, 2) AS defect_rate_pct
        FROM production_runs
        WHERE run_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY 1 ORDER BY 1
    """
    return pd.read_sql(query, engine)

def get_machine_performance():
    return pd.read_sql("SELECT * FROM vw_machine_performance ORDER BY defect_rate_pct DESC", engine)

def get_category_revenue(start_date, end_date):
    query = f"""
        SELECT p.category, SUM(oi.quantity * oi.unit_price) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        JOIN products p     ON p.product_id = oi.product_id
        WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
        AND o.status != 'Cancelled'
        GROUP BY p.category ORDER BY revenue DESC
    """
    return pd.read_sql(query, engine)

def get_delivery_performance(carrier="All"):
    carrier_filter = f"WHERE carrier = '{carrier}'" if carrier != "All" else ""
    return pd.read_sql(f"SELECT * FROM vw_delivery_performance {carrier_filter}", engine)

def get_inventory_health():
    return pd.read_sql("SELECT * FROM vw_inventory_health ORDER BY below_reorder_level DESC, quantity_on_hand ASC", engine)

def get_ticket_summary(start_date, end_date):
    query = f"""
        SELECT issue_type, priority, COUNT(*) AS total,
               SUM(CASE WHEN status IN ('Resolved','Closed') THEN 1 ELSE 0 END) AS resolved
        FROM support_tickets
        WHERE opened_at::date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY issue_type, priority ORDER BY total DESC
    """
    return pd.read_sql(query, engine)

def get_customer_geo():
    return pd.read_sql("SELECT * FROM vw_customer_geo_sales WHERE latitude IS NOT NULL", engine)

def get_top_products(start_date, end_date, n=5):
    query = f"""
        SELECT p.name, p.category, SUM(oi.quantity) AS units_sold,
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        JOIN products p     ON p.product_id = oi.product_id
        WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
        AND o.status != 'Cancelled'
        GROUP BY p.name, p.category ORDER BY revenue DESC LIMIT {n}
    """
    return pd.read_sql(query, engine)