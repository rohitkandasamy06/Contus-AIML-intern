import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from collections import Counter

# ==========================================
# PREMIUM HIGH-END GRAPHICAL THEME SETUP
# ==========================================
# Base layout configurations
plt.rcParams['figure.figsize'] = (11, 6.5)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']

# High-contrast typography hierarchy
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlepad'] = 20
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# Premium dark slate grid structure
sns.set_theme(style="whitegrid", rc={
    "grid.color": "#EAECEE",
    "grid.linestyle": "--",
    "grid.linewidth": 0.8,
    "axes.edgecolor": "#AEB6BF",
    "axes.linewidth": 1.0
})

LINE_COLOR_ACCENT = "#2C3E50"  # Midnight Charcoal
LINE_MARKER_COLOR = "#E74C3C"  # Coral Spark

# ==========================================
# STEP 1: LOAD AND CLEAN YOUR LOCAL CSV FILE
# ==========================================
csv_filename = "Sales_Analysis.csv" 

if not os.path.exists(csv_filename):
    print(f"Error: Missing file! Place '{csv_filename}' in the same folder as this script.")
    exit()

print(f"--- Loading Dataset: {csv_filename} ---")
df = pd.read_csv(csv_filename)
print(f"File loaded. Raw Row Count: {len(df)}")
print(f"Available Columns: {df.columns.tolist()}\n")

# Clean empty lines and header repetitions found in raw file
df = df.dropna(how='all').copy()
if 'Quantity Ordered' in df.columns:
    df = df[df['Quantity Ordered'] != 'Quantity Ordered']

# Safely convert data types to metrics
df['Quantity Ordered'] = pd.to_numeric(df['Quantity Ordered'], errors='coerce')
df['Price Each'] = pd.to_numeric(df['Price Each'], errors='coerce')
df = df.dropna().copy()

# Generate the missing 'Sales Total' column needed for financial tracking
df['Sales Total'] = df['Quantity Ordered'] * df['Price Each']

# ==========================================
# STEP 2: COLUMN STANDARDIZATION
# ==========================================
ORDER_ID_COL = 'Order ID'
PRODUCT_COL  = 'Product'
REVENUE_COL  = 'Sales Total'      
DATE_COL     = 'Order Date'
CITY_COL     = 'City'            

# --- TIMESTAMPS ---
df[DATE_COL] = pd.to_datetime(df[DATE_COL])
df['Month'] = df[DATE_COL].dt.strftime('%B')
df['Hour'] = df[DATE_COL].dt.hour

# --- GEOGRAPHY ---
if CITY_COL not in df.columns and 'Purchase Address' in df.columns:
    df[CITY_COL] = df['Purchase Address'].apply(lambda x: str(x).split(',')[1].strip() if len(str(x).split(',')) > 1 else 'Unknown')

print("Data processing complete. Running metrics...\n")

# ==========================================
# STEP 3: HIGH-END GRAPHICAL GENERATION
# ==========================================

# --- CHART 1: Monthly Revenue Performance ---
print("Generating Premium Monthly Revenue Chart...")
monthly_sales = df.groupby('Month')[REVENUE_COL].sum()
months_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December']
monthly_sales = monthly_sales.reindex([m for m in months_order if m in monthly_sales.index])

fig, ax = plt.subplots()

# Safe palette handling using a native Python list reverse [::-1]
blues_palette = sns.color_palette("Blues", n_colors=len(monthly_sales))[::-1]

bars = sns.barplot(
    x=monthly_sales.index, 
    y=monthly_sales.values, 
    palette=blues_palette, 
    hue=monthly_sales.index, 
    alpha=0.9, 
    edgecolor="#2C3E50", 
    linewidth=0.8
)
if hasattr(ax, 'legend_') and ax.legend_ is not None:
    ax.legend_.remove()

# Add smart inline data labels above bars
for bar in bars.patches:
    height = bar.get_height()
    if height > 0:
        ax.annotate(f"${height:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold', color='#5D6D7E')

plt.title("FINANCIAL REVENUE TRAJECTORY BY MONTH", loc='left', color="#2C3E50")
plt.xticks(rotation=30, ha='right')
plt.ylabel("Revenue ($)")
plt.xlabel("Fiscal Reporting Month")
sns.despine(left=True, bottom=False)
plt.tight_layout()
plt.savefig('revenue_by_month.png', dpi=300, bbox_inches='tight')
plt.close()


# --- CHART 2: Market Performance by City ---
print("Generating Premium Regional Analysis Chart...")
city_sales = df.groupby(CITY_COL)[REVENUE_COL].sum().sort_values(ascending=False)

fig, ax = plt.subplots()

# Fixed palette configuration to bypass environment syntax constraints
crest_palette = sns.color_palette("crest", n_colors=len(city_sales))[::-1]

bars = sns.barplot(
    x=city_sales.values, 
    y=city_sales.index, 
    palette=crest_palette, 
    hue=city_sales.index, 
    alpha=0.9, 
    edgecolor="#2C3E50", 
    linewidth=0.8
)
if hasattr(ax, 'legend_') and ax.legend_ is not None:
    ax.legend_.remove()

# Add clear metrics next to horizontal bars
for bar in bars.patches:
    width = bar.get_width()
    if width > 0:
        ax.annotate(f" ${width:,.2f}",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),  
                    textcoords="offset points",
                    ha='left', va='center', fontsize=9, fontweight='bold', color='#34495E')

plt.title("REVENUE PERFORMANCE BY REGIONAL MARKET", loc='left', color="#2C3E50")
plt.xlabel("Gross Sales Revenue ($)")
plt.ylabel("Target Delivery Location")

# Extend right margin slightly so values don't get clipped
ax.set_xlim(0, city_sales.max() * 1.15)
sns.despine(left=False, bottom=True)
plt.tight_layout()
plt.savefig('revenue_by_city.png', dpi=300, bbox_inches='tight')
plt.close()


# --- CHART 3: Peak Hourly Order Demands ---
print("Generating Premium Hourly Optimization Chart...")
hourly_orders = df.groupby('Hour').count()[ORDER_ID_COL]

fig, ax = plt.subplots()

# Sleek line chart with distinct accents
sns.lineplot(
    x=hourly_orders.index, 
    y=hourly_orders.values, 
    marker="o", 
    color=LINE_COLOR_ACCENT, 
    linewidth=3, 
    markersize=7, 
    markerfacecolor=LINE_MARKER_COLOR, 
    markeredgecolor="white", 
    markeredgewidth=1.5
)

# Shaded background area under the curve
plt.fill_between(hourly_orders.index, hourly_orders.values, color=LINE_COLOR_ACCENT, alpha=0.08)

# Highlight peak hour visually with an arrow annotation
if not hourly_orders.empty:
    peak_hour = hourly_orders.idxmax()
    peak_value = hourly_orders.max()
    ax.annotate(f"Operational Peak ({peak_hour}:00)", 
                xy=(peak_hour, peak_value), 
                xytext=(peak_hour + 1.5, peak_value),
                arrowprops=dict(facecolor='#E74C3C', shrink=0.05, width=1, headwidth=6),
                fontsize=9, fontweight='bold', color='#E74C3C')

plt.title("CUSTOMER TRANSACTION VOLUME DISTRIBUTION BY HOUR", loc='left', color="#2C3E50")
plt.xticks(range(0, 24))
plt.xlabel("Hour of Day (24-Hour System)")
plt.ylabel("Total Placed Orders Count")
plt.tight_layout()
plt.savefig('orders_by_hour.png', dpi=300, bbox_inches='tight')
plt.close()


# --- STEP 4: BUNDLING CORRELATION ---
print("Processing Product Bundle Combinations...")
duplicated_orders = df[df[ORDER_ID_COL].duplicated(keep=False)].copy()
duplicated_orders['Grouped'] = duplicated_orders.groupby(ORDER_ID_COL)[PRODUCT_COL].transform(lambda x: ','.join(x))
unique_bundles = duplicated_orders[[ORDER_ID_COL, 'Grouped']].drop_duplicates()

bundle_counter = Counter()
for row in unique_bundles['Grouped']:
    item_list = str(row).split(',')
    bundle_counter.update(Counter(combinations(item_list, 2)))

# ==========================================
# STEP 5: TERMINAL REPORT SUMMARY
# ==========================================
print("\n" + "="*50)
print("             EXECUTIVE SUMMARY REPORT            ")
print("="*50)

if not monthly_sales.empty:
    print(f"Top Performing Month : {monthly_sales.idxmax()} (${monthly_sales.max():,.2f})")
if not city_sales.empty:
    print(f"Top Performing Region: {city_sales.idxmax()} (${city_sales.max():,.2f})")
if not hourly_orders.empty:
    print(f"Peak Ad Scheduling Hour: {hourly_orders.idxmax()}:00 hours")

print("\nTop 3 Recommended Cross-Selling Bundles:")
for bundle, count in bundle_counter.most_common(3):
    print(f"  * {bundle[0]} + {bundle[1]} (Cross-purchased {count} times)")
print("="*50)
print("High-end visual assets successfully generated:")
print(" -> revenue_by_month.png\n -> revenue_by_city.png\n -> orders_by_hour.png")