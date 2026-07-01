"""
load_data.py
ETL script: creates schema + views in Postgres, then cleans and loads the
generated CSVs into the database.

Run order matters because of foreign key dependencies:
products, machines, warehouses, customers  ->  production_runs, inventory, orders
                                            ->  order_items, shipments
                                            ->  support_tickets

Run: python load_data.py
"""

import os
import pandas as pd
from sqlalchemy import text
from db_config import get_engine

DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
SQL_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "sql"))


def run_sql_file(engine, path):
    with open(path, "r") as f:
        sql = f.read()
    with engine.begin() as conn:
        conn.execute(text(sql))
    print(f"  Executed {path}")


def clean_and_validate(df: pd.DataFrame, name: str, dedupe_subset=None) -> pd.DataFrame:
    """Generic cleaning: trim strings, drop exact dupes, report missing values."""
    before = len(df)

    # Trim whitespace on string columns
    str_cols = df.select_dtypes(include="object").columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()
        df[c] = df[c].replace({"nan": None, "": None})

    # Drop full-row duplicates
    df = df.drop_duplicates()

    # Drop duplicates on logical key if given
    if dedupe_subset:
        df = df.drop_duplicates(subset=dedupe_subset, keep="first")

    after = len(df)
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    print(f"  [{name}] rows: {before} -> {after} (removed {before - after} dupes)")
    if not missing.empty:
        print(f"  [{name}] missing values:\n{missing.to_string()}")

    return df


def load_table(engine, df: pd.DataFrame, table_name: str):
    df.to_sql(table_name, engine, if_exists="append", index=False, method="multi", chunksize=1000)
    print(f"  Loaded {len(df)} rows into {table_name}")


def main():
    engine = get_engine()

    print("Step 1: Creating schema...")
    run_sql_file(engine, os.path.join(SQL_DIR, "01_schema.sql"))

    print("\nStep 2: Loading + cleaning data...")

    # --- Independent tables first ---
    products = clean_and_validate(pd.read_csv(os.path.join(DATA_DIR, "products.csv")), "products", ["product_code"])
    machines = clean_and_validate(pd.read_csv(os.path.join(DATA_DIR, "machines.csv")), "machines", ["machine_code"])
    warehouses = clean_and_validate(pd.read_csv(os.path.join(DATA_DIR, "warehouses.csv")), "warehouses")
    customers = clean_and_validate(pd.read_csv(os.path.join(DATA_DIR, "customers.csv")), "customers")

    load_table(engine, products, "products")
    load_table(engine, machines, "machines")
    load_table(engine, warehouses, "warehouses")
    load_table(engine, customers, "customers")

    # --- Dependent tables ---
    production_runs = clean_and_validate(pd.read_csv(os.path.join(DATA_DIR, "production_runs.csv")), "production_runs")
    inventory = clean_and_validate(pd.read_csv(os.path.join(DATA_DIR, "inventory.csv")), "inventory",
                                    ["warehouse_id", "product_id"])
    orders = clean_and_validate(pd.read_csv(os.path.join(DATA_DIR, "orders.csv")), "orders")

    load_table(engine, production_runs, "production_runs")
    load_table(engine, inventory, "inventory")
    load_table(engine, orders, "orders")

    order_items = clean_and_validate(pd.read_csv(os.path.join(DATA_DIR, "order_items.csv")), "order_items")
    load_table(engine, order_items, "order_items")

    shipments = pd.read_csv(os.path.join(DATA_DIR, "shipments.csv"))
    shipments["delivery_date"] = shipments["delivery_date"].replace("", pd.NA)
    shipments = clean_and_validate(shipments, "shipments")
    load_table(engine, shipments, "shipments")

    tickets = pd.read_csv(os.path.join(DATA_DIR, "support_tickets.csv"))
    tickets["resolved_at"] = tickets["resolved_at"].replace("", pd.NA)
    tickets["order_id"] = tickets["order_id"].astype("Int64")
    tickets = clean_and_validate(tickets, "support_tickets")
    load_table(engine, tickets, "support_tickets")

    print("\nStep 3: Creating analytics views...")
    run_sql_file(engine, os.path.join(SQL_DIR, "02_views.sql"))

    print("\nETL complete.")


if __name__ == "__main__":
    main()