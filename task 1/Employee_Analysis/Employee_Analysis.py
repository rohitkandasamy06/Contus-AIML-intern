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

LINE_COLOR_ACCENT = "#2C3E50"  # Midnight Charcoal
ALERT_COLOR = "#E74C3C"         # Coral Spark

# ==========================================
# STEP 1: LOAD AND CLEAN ENVIRONMENT DATA
# ==========================================
csv_filename = "Employee_Analysis.csv"
print(f"--- Loading Dataset: {csv_filename} ---")
df = pd.read_csv(csv_filename)

# Clear corrupted lines
df = df.dropna().copy()

# Set global shorthand labels mapping variables based on uploaded CSV
GROUP_COL = 'City'
COMPENSATION_COL = 'PaymentTier'
ATTRITION_COL = 'LeaveOrNot'
TENURE_COL = 'ExperienceInCurrentDomain'

print("Data processing complete. Running corporate workforce analytics...\n")

# ==========================================
# STEP 2: CORE HUMAN CAPITAL INVESTIGATIONS
# ==========================================

# --- CHART 1: Average Compensation Structure by Group ---
print("Generating Compensation Tier Chart...")
group_comp = df.groupby(GROUP_COL)[COMPENSATION_COL].mean().sort_values(ascending=False)

fig, ax = plt.subplots()
crest_palette = sns.color_palette("crest", n_colors=len(group_comp))[::-1]

bars = sns.barplot(
    x=group_comp.values, 
    y=group_comp.index, 
    palette=crest_palette, 
    hue=group_comp.index, 
    alpha=0.9, edgecolor="#2C3E50", linewidth=0.8
)

for bar in bars.patches:
    width = bar.get_width()
    if width > 0:
        ax.annotate(f" Tier {width:.2f}",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),  
                    textcoords="offset points",
                    ha='left', va='center', fontsize=9, fontweight='bold', color='#34495E')

plt.title("AVERAGE PAYMENT TIER ALLOCATION BY CITY", loc='left', color="#2C3E50")
plt.xlabel("Mean Payment Tier (Scale 1-3)")
plt.ylabel("Operating City")
ax.set_xlim(0, group_comp.max() * 1.15)
sns.despine(left=False, bottom=True)
plt.tight_layout()
plt.savefig('hr_payment_tier_by_city.png', dpi=300, bbox_inches='tight')
plt.close()


# --- CHART 2: Payment Tier Density vs Domain Experience ---
print("Generating Payment Tier Over Time Line Analysis...")
comp_tenure = df.groupby(TENURE_COL)[COMPENSATION_COL].mean()

fig, ax = plt.subplots()
sns.lineplot(
    x=comp_tenure.index, y=comp_tenure.values, marker="o", 
    color=LINE_COLOR_ACCENT, linewidth=3, markersize=7,
    markerfacecolor=ALERT_COLOR, markeredgecolor="white", markeredgewidth=1.5
)
plt.fill_between(comp_tenure.index, comp_tenure.values, color=LINE_COLOR_ACCENT, alpha=0.06)

plt.title("EMPLOYEE PAYMENT TIER CURVE BY DOMAIN EXPERIENCE", loc='left', color="#2C3E50")
plt.xlabel("Experience in Current Domain (Years)")
plt.ylabel("Mean Payment Tier (Scale 1-3)")
plt.xticks(range(int(df[TENURE_COL].min()), int(df[TENURE_COL].max()) + 1))
plt.ylim(1, 3.5)
plt.tight_layout()
plt.savefig('hr_payment_by_experience.png', dpi=300, bbox_inches='tight')
plt.close()


# --- CHART 3: Turnover Attrition Risk Diagnostics ---
print("Generating Turnover Attrition Risk Distribution Chart...")
attrition_rates = df.groupby(GROUP_COL)[ATTRITION_COL].mean() * 100
attrition_rates = attrition_rates.sort_values(ascending=False)

fig, ax = plt.subplots()
blues_palette = sns.color_palette("Blues", n_colors=len(attrition_rates))[::-1]

bars = sns.barplot(
    x=attrition_rates.index, 
    y=attrition_rates.values, 
    palette=blues_palette, 
    hue=attrition_rates.index,
    alpha=0.9, edgecolor="#2C3E50", linewidth=0.8
)

for bar in bars.patches:
    height = bar.get_height()
    if height > 0:
        ax.annotate(f"{height:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color=ALERT_COLOR if height > 15 else '#5D6D7E')

plt.title("WORKFORCE TURNOVER (ATTRITION RATE) BY CITY", loc='left', color="#2C3E50")
plt.ylabel("Calculated Resignation Rate (%)")
plt.xlabel("Operating City")
sns.despine(left=True, bottom=False)
plt.tight_layout()
plt.savefig('hr_attrition_by_city.png', dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# STEP 3: HR METRICS MANAGEMENT LOG REPORT
# ==========================================
total_headcount = len(df)
overall_attrition = df[ATTRITION_COL].mean() * 100
highest_paying_group = group_comp.idxmax()
highest_attrition_group = attrition_rates.idxmax()

print("\n" + "="*50)
print("            PEOPLE ANALYTICS EXECUTIVE REPORT             ")
print("="*50)
print(f"Total Operational Headcount    : {total_headcount} active workers")
print(f"Global Workforce Attrition Rate: {overall_attrition:.2f}%")
print(f"Highest Average Payment Tier   : {highest_paying_group} (Tier {group_comp.max():.2f})")
print(f"Critical Exit Hazard Segment   : {highest_attrition_group} Office ({attrition_rates.max():.1f}%)")
print("="*50)
print("High-end image output plots successfully generated in folder:")
print(" -> hr_payment_tier_by_city.png\n -> hr_payment_by_experience.png\n -> hr_attrition_by_city.png")