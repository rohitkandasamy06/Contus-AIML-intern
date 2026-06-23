import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# 1. Load your local dataset
csv_filename = "loan_approval.csv"

print(f"Reading dataset from local file: {csv_filename}...", flush=True)
try:
    df = pd.read_csv(csv_filename)
except FileNotFoundError:
    print(f"Error: Could not find '{csv_filename}'. Make sure it is in your project folder.", flush=True)
    exit()

# 2. Separate features (X) from the target (y)
features = ['Income', 'CIBIL_Score', 'Loan_Amount', 'Existing_Debts']
X = df[features]
y = df['Loan_Status']

# 3. Train-Test Split (80% Training, 20% Testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train the Logistic Regression Model
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# 5. Terminal Diagnostics Text Output
predictions = model.predict(X_test)
print("\n================= LOAN APPROVAL LOGISTIC REGRESSION =================", flush=True)
print(f"Overall Model Classification Accuracy: {accuracy_score(y_test, predictions) * 100:.2f}%", flush=True)
print("=======================================================================", flush=True)
print("\nDetailed Performance Diagnostics:\n", classification_report(y_test, predictions), flush=True)

# 6. HIGH-END VISUALIZATION GENERATION: Decision Boundary Mapping
output_image_name = "loan_decision_boundary.png"
print(f"Generating premium classification boundary map as '{output_image_name}'...", flush=True)

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 7.5), facecolor='#F8F9FA')
ax.set_facecolor('#FFFFFF')

# Separate the test set into Approved and Rejected categories for distinct plotting
approved = X_test[y_test == 1]
rejected = X_test[y_test == 0]

# Scatter plot real test observations with crisp borders
ax.scatter(approved['CIBIL_Score'], approved['Income'] / 1000, 
           color='#2A9D8F', alpha=0.7, s=60, edgecolors='#FFFFFF', linewidths=0.5, label='Approved Application (Status=1)')
ax.scatter(rejected['CIBIL_Score'], rejected['Income'] / 1000, 
           color='#E63946', alpha=0.7, s=60, edgecolors='#FFFFFF', linewidths=0.5, label='Rejected Application (Status=0)')

# 7. MATHEMATICAL BOUNDARY EXTRACTION
# Formula for Logistic Regression Boundary: w0*x0 + w1*x1 + mean_offset_bias = 0
# Income_axis = -(w_cibil * CIBIL_axis + intercept + mean_other_features) / w_income
cibil_weights = model.coef_[0][1]
income_weight = model.coef_[0][0]
intercept = model.intercept_[0]

# Factor in average constants for Loan Amount & Debts to keep the 2D plane perfectly balanced
other_features_bias = (model.coef_[0][2] * X_test['Loan_Amount'].mean()) + (model.coef_[0][3] * X_test['Existing_Debts'].mean())

# Generate boundary line tracking coordinates
cibil_range = np.linspace(300, 900, 100)
boundary_income = -(cibil_weights * cibil_range + intercept + other_features_bias) / income_weight
boundary_income_k = boundary_income / 1000  # Convert scale to match thousands line

# Plot the clean line separating choices
ax.plot(cibil_range, boundary_income_k, color='#1D3557', linestyle='-', linewidth=2.5, 
        label='Model Decision Boundary Line')

# Shading background risk territories to visually explain the classification space
ax.fill_between(cibil_range, boundary_income_k, 160, color='#2A9D8F', alpha=0.06)
ax.fill_between(cibil_range, 20, boundary_income_k, color='#E63946', alpha=0.06)

# Typography & Chart Polish
ax.set_title('Logistic Regression Logic: CIBIL vs Income Loan Approval Space', 
             fontsize=13, fontweight='bold', pad=20, color='#1D3557', name='Arial')
ax.set_xlabel('Applicant CIBIL Score Rating (300 - 900)', fontsize=11, fontweight='semibold', labelpad=10)
ax.set_ylabel('Applicant Annual Income (in ₹ Thousands)', fontsize=11, fontweight='semibold', labelpad=10)

# Set clean operational viewport limits
ax.set_xlim(280, 920)
ax.set_ylim(20, 160)

# Clean minimalist frame spines
for spine in ['top', 'right', 'left', 'bottom']:
    ax.spines[spine].set_color('#E0E0E0')

ax.legend(loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#E0E0E0', fontsize=10)
plt.tight_layout()

# Export file cleanly straight to your sidebar files panel
plt.savefig(output_image_name, dpi=300, bbox_inches='tight')
plt.close()