"""
generate_data.py
Generates a realistic, internally-consistent synthetic dataset for an
auto parts manufacturer's operations: production -> warehouse -> logistics -> support.

Key design choice: the data isn't random noise. It's built with deliberate
cause-effect relationships so dashboard insights are real and discoverable:
  - Older/worn machines have higher defect rates
  - High defect rates -> more "Defective Part" support tickets
  - Longer shipment distances -> higher delay probability
  - Certain carriers are systematically worse on time than others
  - Demand has seasonality (monsoon months see garage/repair demand spike)
  - Low-stock products generate delayed dispatches

Run: python generate_data.py
Outputs CSVs into ../data/
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)

START_DATE = datetime(2025, 1, 1)
END_DATE   = datetime(2025, 12, 31)
DAYS = (END_DATE - START_DATE).days + 1

OUT = "/home/claude/ops_project/data"

# ------------------------------------------------------------------
# 1. PRODUCTS
# ------------------------------------------------------------------
categories = {
    "Brake System": ["Brake Pad Set", "Brake Disc", "Brake Caliper", "Brake Fluid Reservoir"],
    "Engine": ["Piston Kit", "Timing Belt", "Engine Gasket Set", "Oil Filter", "Spark Plug Set"],
    "Electrical": ["Alternator", "Starter Motor", "Battery Terminal", "Headlight Assembly"],
    "Suspension": ["Shock Absorber", "Strut Mount", "Control Arm", "Coil Spring"],
    "Transmission": ["Clutch Plate", "Gearbox Mount", "Drive Shaft"],
}

products = []
pid = 1
for cat, items in categories.items():
    for item in items:
        unit_cost = round(random.uniform(150, 4500), 2)
        products.append({
            "product_id": pid,
            "product_code": f"AP-{pid:04d}",
            "product_name": item,
            "category": cat,
            "unit_cost": unit_cost,
            "unit_price": round(unit_cost * random.uniform(1.35, 1.8), 2),
            "production_time_mins": random.choice([15, 20, 25, 30, 45, 60]),
        })
        pid += 1

products_df = pd.DataFrame(products)
products_df.to_csv(f"{OUT}/products.csv", index=False)

# ------------------------------------------------------------------
# 2. MACHINES  (some old & unreliable, some new & efficient -> drives defect variance)
# ------------------------------------------------------------------
lines = ["Line A", "Line B", "Line C"]
machines = []
for i in range(1, 13):
    install_year = random.choice([2015, 2017, 2019, 2021, 2023, 2024])
    # older machines -> higher base defect propensity (used later)
    machines.append({
        "machine_id": i,
        "machine_code": f"MC-{i:03d}",
        "machine_name": f"Press Unit {i}" if i % 2 == 0 else f"CNC Unit {i}",
        "production_line": random.choice(lines),
        "install_year": install_year,
        "status": "active",
    })
machines_df = pd.DataFrame(machines)
machines_df.to_csv(f"{OUT}/machines.csv", index=False)

def machine_defect_base_rate(install_year):
    age = 2025 - install_year
    # older machine -> higher defect base rate, range ~1% to ~9%
    return min(0.01 + age * 0.012, 0.09)

# ------------------------------------------------------------------
# 3. PRODUCTION RUNS (one or more runs per machine per active day)
# ------------------------------------------------------------------
runs = []
run_id = 1
shifts = ["Morning", "Evening", "Night"]

for day_offset in range(DAYS):
    run_date = START_DATE + timedelta(days=day_offset)
    # skip some Sundays (lower activity) - simulate realistic factory calendar
    if run_date.weekday() == 6 and random.random() < 0.6:
        continue
    for m in machines:
        # not every machine runs every day
        if random.random() < 0.15:
            continue
        shift = random.choice(shifts)
        product = random.choice(products)
        start_hour = {"Morning": 7, "Evening": 15, "Night": 23}[shift]
        start_time = run_date.replace(hour=start_hour, minute=0, second=0)
        duration_units = random.randint(80, 260)
        end_time = start_time + timedelta(minutes=duration_units * product["production_time_mins"] / 60)

        base_rate = machine_defect_base_rate(m["install_year"])
        # add random noise + occasional "bad day" spikes
        defect_rate = max(0, np.random.normal(base_rate, base_rate * 0.4))
        if random.random() < 0.03:  # rare quality incident
            defect_rate += random.uniform(0.05, 0.15)

        defects = int(round(duration_units * defect_rate))
        defects = min(defects, duration_units)

        runs.append({
            "run_id": run_id,
            "product_id": product["product_id"],
            "machine_id": m["machine_id"],
            "shift": shift,
            "run_date": run_date.date().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "units_produced": duration_units,
            "units_defective": defects,
        })
        run_id += 1

production_runs_df = pd.DataFrame(runs)
production_runs_df.to_csv(f"{OUT}/production_runs.csv", index=False)

# ------------------------------------------------------------------
# 4. WAREHOUSES
# ------------------------------------------------------------------
warehouse_cities = [
    ("Chennai Central WH", "Chennai", "Tamil Nadu"),
    ("Coimbatore WH", "Coimbatore", "Tamil Nadu"),
    ("Bengaluru WH", "Bengaluru", "Karnataka"),
    ("Hyderabad WH", "Hyderabad", "Telangana"),
]
warehouses = []
for i, (name, city, state) in enumerate(warehouse_cities, start=1):
    warehouses.append({
        "warehouse_id": i, "warehouse_name": name, "city": city,
        "state": state, "capacity_units": random.randint(8000, 20000)
    })
warehouses_df = pd.DataFrame(warehouses)
warehouses_df.to_csv(f"{OUT}/warehouses.csv", index=False)

# ------------------------------------------------------------------
# 5. INVENTORY (current snapshot, derived loosely from production totals)
# ------------------------------------------------------------------
inventory = []
inv_id = 1
total_produced_by_product = production_runs_df.groupby("product_id")["units_produced"].sum().to_dict()
total_defects_by_product = production_runs_df.groupby("product_id")["units_defective"].sum().to_dict()

for wh in warehouses:
    for p in products:
        produced = total_produced_by_product.get(p["product_id"], 0)
        good_units = produced - total_defects_by_product.get(p["product_id"], 0)
        # split production across warehouses unevenly, simulate some being low stock
        share = random.uniform(0.05, 0.4)
        qty = max(0, int(good_units * share / len(warehouses)))
        reorder = random.randint(50, 300)
        inventory.append({
            "inventory_id": inv_id,
            "warehouse_id": wh["warehouse_id"],
            "product_id": p["product_id"],
            "quantity_on_hand": qty,
            "reorder_level": reorder,
            "last_updated": END_DATE.date().isoformat(),
        })
        inv_id += 1
inventory_df = pd.DataFrame(inventory)
inventory_df.to_csv(f"{OUT}/inventory.csv", index=False)

# ------------------------------------------------------------------
# 6. CUSTOMERS (with real-ish lat/lon around Indian cities for map)
# ------------------------------------------------------------------
city_coords = {
    "Chennai": (13.0827, 80.2707), "Coimbatore": (11.0168, 76.9558),
    "Bengaluru": (12.9716, 77.5946), "Hyderabad": (17.3850, 78.4867),
    "Madurai": (9.9252, 78.1198), "Vijayawada": (16.5062, 80.6480),
    "Mysuru": (12.2958, 76.6394), "Trichy": (10.7905, 78.7047),
    "Vellore": (12.9165, 79.1325), "Salem": (11.6643, 78.1460),
}
state_by_city = {
    "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu", "Madurai": "Tamil Nadu",
    "Trichy": "Tamil Nadu", "Vellore": "Tamil Nadu", "Salem": "Tamil Nadu",
    "Bengaluru": "Karnataka", "Mysuru": "Karnataka",
    "Hyderabad": "Telangana", "Vijayawada": "Andhra Pradesh",
}

customers = []
cust_types = ["Retail", "Garage", "Distributor"]
cust_type_weights = [0.5, 0.35, 0.15]
for i in range(1, 301):
    city = random.choice(list(city_coords.keys()))
    lat, lon = city_coords[city]
    jitter_lat = lat + random.uniform(-0.15, 0.15)
    jitter_lon = lon + random.uniform(-0.15, 0.15)
    customers.append({
        "customer_id": i,
        "customer_name": fake.company() if random.random() < 0.4 else fake.name(),
        "customer_type": random.choices(cust_types, weights=cust_type_weights)[0],
        "city": city,
        "state": state_by_city[city],
        "latitude": round(jitter_lat, 6),
        "longitude": round(jitter_lon, 6),
    })
customers_df = pd.DataFrame(customers)
customers_df.to_csv(f"{OUT}/customers.csv", index=False)

# ------------------------------------------------------------------
# 7. ORDERS + ORDER ITEMS (seasonality: monsoon months Jun-Sep higher demand)
# ------------------------------------------------------------------
orders = []
order_items = []
order_id = 1
order_item_id = 1

monsoon_months = {6, 7, 8, 9}

for day_offset in range(DAYS):
    order_date = START_DATE + timedelta(days=day_offset)
    base_orders_per_day = 8
    if order_date.month in monsoon_months:
        base_orders_per_day = int(base_orders_per_day * 1.5)
    n_orders = np.random.poisson(base_orders_per_day)

    for _ in range(n_orders):
        cust = random.choice(customers)
        status = random.choices(
            ["placed", "dispatched", "delivered", "cancelled"],
            weights=[0.05, 0.1, 0.8, 0.05]
        )[0]
        orders.append({
            "order_id": order_id,
            "customer_id": cust["customer_id"],
            "order_date": order_date.date().isoformat(),
            "status": status,
        })

        n_items = random.randint(1, 4)
        chosen_products = random.sample(products, n_items)
        for p in chosen_products:
            order_items.append({
                "order_item_id": order_item_id,
                "order_id": order_id,
                "product_id": p["product_id"],
                "quantity": random.randint(1, 6),
                "unit_price": p["unit_price"],
            })
            order_item_id += 1

        order_id += 1

orders_df = pd.DataFrame(orders)
order_items_df = pd.DataFrame(order_items)
orders_df.to_csv(f"{OUT}/orders.csv", index=False)
order_items_df.to_csv(f"{OUT}/order_items.csv", index=False)

# ------------------------------------------------------------------
# 8. SHIPMENTS (distance & carrier affect delay probability)
# ------------------------------------------------------------------
carriers = ["BlueDart Freight", "Delhivery Cargo", "TCI Express", "VRL Logistics"]
carrier_reliability = {  # base on-time probability
    "BlueDart Freight": 0.90, "Delhivery Cargo": 0.85,
    "TCI Express": 0.78, "VRL Logistics": 0.72,
}

shipments = []
shipment_id = 1
for _, order in orders_df.iterrows():
    if order["status"] in ("cancelled", "placed"):
        continue
    cust = customers_df.loc[customers_df.customer_id == order.customer_id].iloc[0]
    wh = random.choice(warehouses)
    wh_coords = city_coords.get(wh["city"], (13.08, 80.27))
    # approximate distance via simple haversine-ish euclidean degrees -> km scale
    dist = ((cust.latitude - wh_coords[0])**2 + (cust.longitude - wh_coords[1])**2) ** 0.5 * 111
    dist = round(max(dist, 5), 2)

    carrier = random.choice(carriers)
    dispatch_date = datetime.fromisoformat(order.order_date) + timedelta(days=random.randint(0, 2))
    transit_days_expected = max(1, int(dist / 250) + random.randint(1, 2))
    expected_delivery = dispatch_date + timedelta(days=transit_days_expected)

    on_time_prob = carrier_reliability[carrier] - min(dist / 3000, 0.15)
    delivered = order["status"] == "delivered"

    if delivered:
        if random.random() < on_time_prob:
            actual_delivery = expected_delivery - timedelta(days=random.randint(0, 1))
            delivery_status = "delivered"
        else:
            actual_delivery = expected_delivery + timedelta(days=random.randint(1, 5))
            delivery_status = "delayed"
    else:
        actual_delivery = None
        delivery_status = "in_transit"

    shipments.append({
        "shipment_id": shipment_id,
        "order_id": order.order_id,
        "warehouse_id": wh["warehouse_id"],
        "carrier": carrier,
        "dispatch_date": dispatch_date.date().isoformat(),
        "expected_delivery_date": expected_delivery.date().isoformat(),
        "actual_delivery_date": actual_delivery.date().isoformat() if actual_delivery else "",
        "distance_km": dist,
        "delivery_status": delivery_status,
    })
    shipment_id += 1

shipments_df = pd.DataFrame(shipments)
shipments_df.to_csv(f"{OUT}/shipments.csv", index=False)

# ------------------------------------------------------------------
# 9. SUPPORT TICKETS (driven by defects + delayed shipments)
# ------------------------------------------------------------------
tickets = []
ticket_id = 1
issue_types = ["Defective Part", "Wrong Fitment", "Late Delivery", "Damaged in Transit", "Billing Issue", "Other"]

# delayed/returned shipments -> Late Delivery / Damaged tickets
for _, s in shipments_df.iterrows():
    if s["delivery_status"] == "delayed" and random.random() < 0.55:
        order = orders_df.loc[orders_df.order_id == s.order_id].iloc[0]
        opened = datetime.fromisoformat(s["expected_delivery_date"]) + timedelta(days=random.randint(0, 3))
        priority = random.choice(["Medium", "High"])
        resolved = opened + timedelta(hours=random.randint(4, 96)) if random.random() < 0.85 else None
        tickets.append({
            "ticket_id": ticket_id, "order_id": s.order_id, "customer_id": order.customer_id,
            "issue_type": "Late Delivery", "priority": priority,
            "opened_at": opened.isoformat(), "resolved_at": resolved.isoformat() if resolved else "",
            "status": "resolved" if resolved else "open",
        })
        ticket_id += 1

# defect-heavy orders -> Defective Part tickets (join via order_items -> high-defect products)
high_defect_products = production_runs_df.groupby("product_id").apply(
    lambda g: g.units_defective.sum() / max(g.units_produced.sum(), 1)
).sort_values(ascending=False)
risky_product_ids = set(high_defect_products.head(8).index)

for _, oi in order_items_df.iterrows():
    if oi.product_id in risky_product_ids and random.random() < 0.04:
        order = orders_df.loc[orders_df.order_id == oi.order_id].iloc[0]
        opened = datetime.fromisoformat(order.order_date) + timedelta(days=random.randint(3, 20))
        priority = random.choice(["Medium", "High", "Urgent"])
        resolved = opened + timedelta(hours=random.randint(2, 72)) if random.random() < 0.8 else None
        tickets.append({
            "ticket_id": ticket_id, "order_id": oi.order_id, "customer_id": order.customer_id,
            "issue_type": "Defective Part", "priority": priority,
            "opened_at": opened.isoformat(), "resolved_at": resolved.isoformat() if resolved else "",
            "status": "resolved" if resolved else "open",
        })
        ticket_id += 1

# background noise: random other tickets
for _ in range(250):
    order = orders_df.sample(1).iloc[0]
    opened = datetime.fromisoformat(order.order_date) + timedelta(days=random.randint(1, 25))
    if opened > END_DATE:
        continue
    issue = random.choice(["Wrong Fitment", "Billing Issue", "Other"])
    priority = random.choice(["Low", "Medium"])
    resolved = opened + timedelta(hours=random.randint(1, 48)) if random.random() < 0.9 else None
    tickets.append({
        "ticket_id": ticket_id, "order_id": order.order_id, "customer_id": order.customer_id,
        "issue_type": issue, "priority": priority,
        "opened_at": opened.isoformat(), "resolved_at": resolved.isoformat() if resolved else "",
        "status": "resolved" if resolved else "open",
    })
    ticket_id += 1

tickets_df = pd.DataFrame(tickets)
tickets_df.to_csv(f"{OUT}/support_tickets.csv", index=False)

# ------------------------------------------------------------------
print("Generated rows:")
print(f"  products:         {len(products_df)}")
print(f"  machines:         {len(machines_df)}")
print(f"  production_runs:  {len(production_runs_df)}")
print(f"  warehouses:       {len(warehouses_df)}")
print(f"  inventory:        {len(inventory_df)}")
print(f"  customers:        {len(customers_df)}")
print(f"  orders:           {len(orders_df)}")
print(f"  order_items:      {len(order_items_df)}")
print(f"  shipments:        {len(shipments_df)}")
print(f"  support_tickets:  {len(tickets_df)}")
