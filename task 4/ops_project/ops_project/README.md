# AutoParts Operations Analytics Dashboard

An end-to-end operations analytics platform for a synthetic auto parts
manufacturer, covering the full operational chain:

**Production → Warehouse/Inventory → Logistics/Delivery → Customer Support**

Built with PostgreSQL, SQLAlchemy, pandas, and Streamlit + Plotly.

---

## Why this project is different

Instead of a single-domain dataset (just sales, or just inventory), this
project models a complete operations chain so the dashboard can surface
**cross-domain insights** — e.g. older machines produce more defects, which
drives more "Defective Part" support tickets; certain logistics carriers are
systematically less reliable, which drives "Late Delivery" tickets. The
synthetic dataset was built with deliberate cause-and-effect business logic
(not random noise), so these relationships are real and explorable in the
dashboard, not just window dressing.

---

## Project structure

```
ops_project/
├── data/                  # Generated CSV datasets (10 tables)
├── sql/
│   ├── 01_schema.sql      # Tables, constraints, indexes
│   └── 02_views.sql       # Analytics views for fast dashboard queries
├── etl/
│   ├── db_config.py       # DB connection (reads .env)
│   ├── generate_data.py   # Synthetic data generator
│   └── load_data.py       # ETL: create schema, clean + load CSVs, create views
├── dashboard/
│   ├── data_access.py     # All SQL queries live here (data access layer)
│   └── app.py             # Streamlit dashboard
├── requirements.txt
└── .env.example
```

---

## Setup

### 1. Install PostgreSQL
Native install (postgresql.org) or via Docker:
```bash
docker run --name autoparts-postgres -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 -d postgres
```

Create the database:
```bash
psql -U postgres -h localhost -c "CREATE DATABASE autoparts_ops;"
```

### 2. Python environment
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure credentials
Copy `.env.example` to `.env` and fill in your actual DB password:
```bash
cp .env.example .env
```

### 4. Generate the dataset (already generated, but to regenerate)
```bash
cd etl
python generate_data.py
```

### 5. Load into PostgreSQL (creates schema + views + loads data)
```bash
python load_data.py
```

### 6. Run the dashboard
```bash
cd ../dashboard
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## Dataset overview

| Table | Rows (approx) | Description |
|---|---|---|
| products | 20 | Auto parts across 5 categories |
| machines | 12 | Production machines, varying install years |
| production_runs | ~3,400 | Daily shift-level production with defect tracking |
| warehouses | 4 | Regional warehouses |
| inventory | 80 | Current stock per warehouse/product |
| customers | 300 | Retail, Garage, Distributor customers with geolocation |
| orders | ~3,400 | Customer orders over 1 year |
| order_items | ~8,400 | Line items per order |
| shipments | ~3,000 | Delivery tracking with carrier and distance |
| support_tickets | ~835 | Issue tickets linked to orders/defects |

---

## Dashboard features

- **KPI row**: Revenue, Orders, Defect Rate, On-Time Delivery %, Avg Ticket Resolution
- **Sales & Revenue tab**: Monthly trend, category share, units sold
- **Production Quality tab**: Defect rate trend, machine-level drill-down
- **Inventory tab**: Stock by category, low-stock alerts (below reorder level)
- **Logistics & Map tab**: Carrier on-time performance, customer geolocation map
- **Support Desk tab**: Ticket volume trends, defect-to-complaint correlation chart
- **Filters**: Date range, product category, warehouse, customer type (sidebar)

---

## Notes for your defense / examiner Q&A

- Schema is in 3NF with proper FK constraints, CHECK constraints, and indexes
  on all columns used in WHERE/JOIN/GROUP BY for analytics queries.
- Views (`sql/02_views.sql`) pre-aggregate common analytics so the dashboard
  doesn't repeat heavy joins/aggregations on every page load — this is the
  "optimize analytics queries" requirement from the brief.
- `vw_defect_to_complaint` is a deliberate cross-domain view joining
  production quality data to support ticket data — this is the project's
  key differentiator vs. a single-table dashboard.
- The data access layer (`data_access.py`) keeps all SQL in one place,
  separate from the Streamlit UI code — a basic but important data
  engineering practice.
