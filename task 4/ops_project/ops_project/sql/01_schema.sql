-- ============================================================
-- AutoParts Operations Analytics - Schema
-- Columns match CSV output from generate_data.py exactly
-- ============================================================

DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS shipments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS warehouses CASCADE;
DROP TABLE IF EXISTS production_runs CASCADE;
DROP TABLE IF EXISTS machines CASCADE;
DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE products (
    product_id              SERIAL PRIMARY KEY,
    product_code            VARCHAR(20) UNIQUE NOT NULL,
    name                    VARCHAR(120) NOT NULL,
    category                VARCHAR(50) NOT NULL,
    unit_cost               NUMERIC(10,2) NOT NULL CHECK (unit_cost >= 0),
    unit_price              NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    production_time_mins    INTEGER NOT NULL CHECK (production_time_mins > 0)
);

CREATE TABLE machines (
    machine_id      SERIAL PRIMARY KEY,
    machine_code    VARCHAR(20) UNIQUE NOT NULL,
    machine_name    VARCHAR(100) NOT NULL,
    line_id         VARCHAR(20) NOT NULL,
    install_year    INTEGER NOT NULL,
    status          VARCHAR(30) NOT NULL DEFAULT 'Active'
);

CREATE TABLE warehouses (
    warehouse_id    SERIAL PRIMARY KEY,
    warehouse_code  VARCHAR(20) UNIQUE NOT NULL,
    city            VARCHAR(50) NOT NULL,
    state           VARCHAR(50) NOT NULL,
    capacity_units  INTEGER NOT NULL CHECK (capacity_units > 0)
);

CREATE TABLE customers (
    customer_id     SERIAL PRIMARY KEY,
    customer_name   VARCHAR(120) NOT NULL,
    customer_type   VARCHAR(40) NOT NULL,
    city            VARCHAR(50) NOT NULL,
    state           VARCHAR(50) NOT NULL,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6)
);

CREATE TABLE production_runs (
    run_id              SERIAL PRIMARY KEY,
    product_id          INTEGER NOT NULL REFERENCES products(product_id),
    machine_id          INTEGER NOT NULL REFERENCES machines(machine_id),
    shift               VARCHAR(10) NOT NULL,
    run_date            DATE NOT NULL,
    start_time          TIMESTAMP NOT NULL,
    end_time            TIMESTAMP NOT NULL,
    units_produced      INTEGER NOT NULL CHECK (units_produced >= 0),
    units_defective     INTEGER NOT NULL CHECK (units_defective >= 0)
);

CREATE INDEX idx_prodruns_date     ON production_runs(run_date);
CREATE INDEX idx_prodruns_machine  ON production_runs(machine_id);
CREATE INDEX idx_prodruns_product  ON production_runs(product_id);

CREATE TABLE inventory (
    inventory_id        SERIAL PRIMARY KEY,
    warehouse_id        INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
    product_id          INTEGER NOT NULL REFERENCES products(product_id),
    quantity_on_hand    INTEGER NOT NULL CHECK (quantity_on_hand >= 0),
    reorder_level       INTEGER NOT NULL CHECK (reorder_level >= 0),
    last_updated        DATE NOT NULL,
    UNIQUE (warehouse_id, product_id)
);

CREATE TABLE orders (
    order_id        SERIAL PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date      DATE NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'Placed'
);

CREATE INDEX idx_orders_date     ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);

CREATE TABLE order_items (
    order_item_id   SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(order_id),
    product_id      INTEGER NOT NULL REFERENCES products(product_id),
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0)
);

CREATE INDEX idx_orderitems_order   ON order_items(order_id);
CREATE INDEX idx_orderitems_product ON order_items(product_id);

CREATE TABLE shipments (
    shipment_id     SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(order_id),
    warehouse_id    INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
    carrier         VARCHAR(60) NOT NULL,
    dispatch_date   DATE NOT NULL,
    delivery_date   DATE,
    distance_km     NUMERIC(8,2),
    delivery_status VARCHAR(30) NOT NULL DEFAULT 'In Transit'
);

CREATE INDEX idx_shipments_order    ON shipments(order_id);
CREATE INDEX idx_shipments_dispatch ON shipments(dispatch_date);

CREATE TABLE support_tickets (
    ticket_id       SERIAL PRIMARY KEY,
    order_id        INTEGER REFERENCES orders(order_id),
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    issue_type      VARCHAR(50) NOT NULL,
    priority        VARCHAR(10) NOT NULL,
    opened_at       TIMESTAMP NOT NULL,
    resolved_at     TIMESTAMP,
    status          VARCHAR(20) NOT NULL DEFAULT 'Open'
);

CREATE INDEX idx_tickets_opened   ON support_tickets(opened_at);
CREATE INDEX idx_tickets_customer ON support_tickets(customer_id);