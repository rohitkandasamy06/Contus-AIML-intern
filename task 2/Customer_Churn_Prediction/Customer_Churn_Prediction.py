import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 1. Load your local dataset
csv_filename = "customer_churn.csv"

print(f"Reading dataset from local file: {csv_filename}...", flush=True)
try:
    df = pd.read_csv(csv_filename)
except FileNotFoundError:
    print(f"Error: Could not find '{csv_filename}'. Make sure it is in your project folder.", flush=True)
    exit()

print(f"Dataset successfully loaded! Total rows parsed: {df.shape[0]}", flush=True)

# 2. Separate independent classification features (X) from the target variable (y)
features = ['Tenure_Months', 'Monthly_Charges', 'Total_Charges', 'Support_Calls', 'Usage_Gb']
X = df[features]
y = df['Churn']

# 3. Train-Test Split (80% Training, 20% Testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize and train the Random Forest Classifier Classification Algorithm
model = RandomForestClassifier(n_estimators=100, random_state=42)
print("\nTraining Random Forest Classification Ensemble...", flush=True)
model.fit(X_train, y_train)

# 5. Run evaluation predictions
predictions = model.predict(X_test)

# 6. PRINT CLASSIFICATION SUMMARY OUTPUT ON TERMINAL
accuracy = accuracy_score(y_test, predictions)

print("\n================ CUSTOMER CHURN CLASSIFICATION RESULTS ================", flush=True)
print(f"Overall Model Classification Accuracy: {accuracy * 100:.2f}%", flush=True)
print("=======================================================================", flush=True)

# Detailed Breakdown Report text matrix (Precision, Recall, F1-Score)
print("\nDetailed Classification Performance Report:\n", classification_report(y_test, predictions), flush=True)

# Print a text registry representation of the Confusion Matrix
cm = confusion_matrix(y_test, predictions)
print("Terminal Confusion Matrix Grid Summary:")
print(f" -> True Retained (Correct stays): {cm[0][0]}")
print(f" -> False Churn (False Alarms)  : {cm[0][1]}")
print(f" -> False Retained (Missed drops): {cm[1][0]}")
print(f" -> True Churn (Correct catches): {cm[1][1]}\n")

# 7. Extract Feature Importance metrics directly from the Classification Engine
importances = model.feature_importances_
indices = np.argsort(importances)
sorted_features = [features[i] for i in indices]
sorted_importances = importances[indices] * 100  # Convert to percentage scale

# 8. HIGH-END VISUALIZATION GENERATION: Dual-Panel Bar & Behavior Analysis
output_image_name = "churn_classification_analysis.png"

plt.style.use('seaborn-v0_8-whitegrid')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), facecolor='#F8F9FA')

# PANEL 1: Feature Importance Horizontal Bar Graph (What the algorithm prioritized)
colors_bar = plt.cm.Blues(np.linspace(0.4, 0.9, len(features)))
bars = ax1.barh(sorted_features, sorted_importances, color=colors_bar, edgecolor='#E0E0E0', height=0.6)

# Add clear value tracking tags to the tips of the bars
for bar in bars:
    width = bar.get_width()
    ax1.annotate(f'{width:.1f}%',
                 xy=(width, bar.get_y() + bar.get_height() / 2),
                 xytext=(5, 0), textcoords="offset points",
                 ha='left', va='center', fontsize=10, fontweight='bold', color='#264653')

ax1.set_title('Classifier Logic: What Metrics Drive Churn Decisions?', fontsize=12, fontweight='bold', color='#1D3557', pad=15)
ax1.set_xlabel('Relative Decision Weight Impact (%)', fontsize=10, fontweight='semibold')
ax1.set_xlim(0, max(sorted_importances) + 8)
ax1.grid(True, linestyle=':', alpha=0.5, axis='x')

# PANEL 2: Real-World Distribution based on Top Classifier Feature (Support Calls)
retained = df[df['Churn'] == 0]['Support_Calls']
churned = df[df['Churn'] == 1]['Support_Calls']

ax2.hist([retained, churned], bins=10, stacked=True, color=['#2A9D8F', '#E63946'], 
         alpha=0.8, edgecolor='#FFFFFF', label=['Retained (Stay)', 'Churned (Left)'], rwidth=0.85)

ax2.set_title('Behavior Separation: Support Call Volumes vs. Customer Loss', fontsize=12, fontweight='bold', color='#1D3557', pad=15)
ax2.set_xlabel('Number of Support Complaints Logged', fontsize=10, fontweight='semibold')
ax2.set_ylabel('Total Customer Profiles Count', fontsize=10, fontweight='semibold')
ax2.grid(True, linestyle=':', alpha=0.5, axis='y')
ax2.legend(loc='upper right', frameon=True, facecolor='#FFFFFF', edgecolor='#E0E0E0')

# Polish backgrounds and border spines cleanly
for ax in [ax1, ax2]:
    ax.set_facecolor('#FFFFFF')
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_color('#E0E0E0')

plt.tight_layout()

# ==========================================
# FILE SAVING METHOD: Saves image automatically to the active directory
# ==========================================
plt.savefig(output_image_name, dpi=300, bbox_inches='tight')
plt.close()
