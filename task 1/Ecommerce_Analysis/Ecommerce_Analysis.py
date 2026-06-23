import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# PREMIUM HIGH-END GRAPHICAL THEME SETUP
# ==========================================
plt.rcParams['figure.figsize'] = (11, 6.5)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']

plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlepad'] = 20
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

sns.set_theme(style="whitegrid", rc={
    "grid.color": "#EAECEE",
    "grid.linestyle": "--",
    "grid.linewidth": 0.8,
    "axes.edgecolor": "#AEB6BF",
    "axes.linewidth": 1.0
})

LINE_COLOR_ACCENT = "#2768A8"  # Midnight Charcoal
ALERT_COLOR = "#F7AE0F"         # Coral Spark

# ==========================================
# STEP 1: LOAD AND CLEAN ENVIRONMENT DATA
# ==========================================
csv_filename = "Amazon Sale Report.csv"
print(f"--- Loading Dataset: {csv_filename} ---")
# Using low_memory=False as the file might have mixed types
df = pd.read_csv(csv_filename, low_memory=False)

# Clean data: Parse amount to numeric, fill NaNs
if 'Amount' in df.columns:
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

# Set global shorthand labels mapping variables based on uploaded CSV
CATEGORY_COL = 'Category'
AMOUNT_COL = 'Amount'
STATUS_COL = 'Status'
STATE_COL = 'ship-state'

print("Data processing complete. Running E-Commerce analytics...\n")

# ==========================================
# STEP 2: CORE E-COMMERCE INVESTIGATIONS
# ==========================================

# --- CHART 1: Total Revenue by Category ---
print("Generating Category Revenue Chart...")
category_revenue = df.groupby(CATEGORY_COL)[AMOUNT_COL].sum().sort_values(ascending=False).head(10)

fig, ax = plt.subplots()
crest_palette = sns.color_palette("crest", n_colors=len(category_revenue))[::-1]

bars = sns.barplot(
    x=category_revenue.values, 
    y=category_revenue.index, 
    palette=crest_palette, 
    hue=category_revenue.index, 
    alpha=0.9, edgecolor="#2C3E50", linewidth=0.8
)

for bar in bars.patches:
    width = bar.get_width()
    if width > 0:
        # formatting as millions or thousands depending on size
        label_text = f" ₹{width/1000000:.2f}M" if width > 1000000 else f" ₹{width/1000:.1f}k"
        ax.annotate(label_text,
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),  
                    textcoords="offset points",
                    ha='left', va='center', fontsize=9, fontweight='bold', color='#34495E')

plt.title("TOTAL SALES REVENUE BY PRODUCT CATEGORY", loc='left', color="#2C3E50")
plt.xlabel("Total Revenue (INR)")
plt.ylabel("Product Category")
ax.set_xlim(0, category_revenue.max() * 1.15)
sns.despine(left=False, bottom=True)
plt.tight_layout()
plt.savefig('ecom_revenue_by_category.png', dpi=300, bbox_inches='tight')
plt.close()


# --- CHART 2: Order Status Distribution ---
print("Generating Order Status Distribution Chart...")
status_counts = df[STATUS_COL].value_counts().head(8)

fig, ax = plt.subplots()
blues_palette = sns.color_palette("Blues", n_colors=len(status_counts))[::-1]

bars = sns.barplot(
    x=status_counts.values, 
    y=status_counts.index, 
    palette=blues_palette, 
    hue=status_counts.index,
    alpha=0.9, edgecolor="#2C3E50", linewidth=0.8
)

for bar in bars.patches:
    width = bar.get_width()
    if width > 0:
        ax.annotate(f" {int(width):,}",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),  
                    textcoords="offset points",
                    ha='left', va='center', fontsize=9, fontweight='bold', color='#34495E')

plt.title("OVERALL ORDER STATUS DISTRIBUTION", loc='left', color="#2C3E50")
plt.xlabel("Number of Orders")
plt.ylabel("Order Status")
ax.set_xlim(0, status_counts.max() * 1.15)
sns.despine(left=False, bottom=True)
plt.tight_layout()
plt.savefig('ecom_order_status.png', dpi=300, bbox_inches='tight')
plt.close()


# --- CHART 3: Top Performing States by Revenue ---
print("Generating Regional Revenue Distribution Chart...")
state_revenue = df.groupby(STATE_COL)[AMOUNT_COL].sum().sort_values(ascending=False).head(10)

fig, ax = plt.subplots()
# Use a distinct palette for regions
flare_palette = sns.color_palette("flare", n_colors=len(state_revenue))[::-1]

bars = sns.barplot(
    x=state_revenue.index, 
    y=state_revenue.values, 
    palette=flare_palette, 
    hue=state_revenue.index,
    alpha=0.9, edgecolor="#2C3E50", linewidth=0.8
)

for bar in bars.patches:
    height = bar.get_height()
    if height > 0:
        label_text = f"₹{height/1000000:.1f}M" if height > 1000000 else f"₹{height/1000:.0f}k"
        ax.annotate(label_text,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold', color='#34495E')

plt.title("TOP 10 REGIONS (STATES) BY SALES REVENUE", loc='left', color="#2C3E50")
plt.ylabel("Total Revenue (INR)")
plt.xlabel("Shipping State")
plt.xticks(rotation=45, ha='right')
sns.despine(left=True, bottom=False)
plt.tight_layout()
plt.savefig('ecom_revenue_by_state.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# STEP 3: E-COMMERCE METRICS EXECUTIVE REPORT
# ==========================================
total_orders = len(df)
total_revenue = df[AMOUNT_COL].sum()
top_category = category_revenue.idxmax()
top_state = state_revenue.idxmax()

print("\n" + "="*50)
print("            E-COMMERCE ANALYTICS EXECUTIVE REPORT             ")
print("="*50)
print(f"Total Order Volume           : {total_orders:,} units")
print(f"Gross Merchandise Value (GMV): ₹{total_revenue:,.2f}")
print(f"Top Performing Category      : {top_category} (₹{category_revenue.max():,.2f})")
print(f"Primary Regional Market      : {top_state} (₹{state_revenue.max():,.2f})")
print("="*50)
print("High-end image output plots successfully generated in folder:")
print(" -> ecom_revenue_by_category.png\n -> ecom_order_status.png\n -> ecom_revenue_by_state.png")