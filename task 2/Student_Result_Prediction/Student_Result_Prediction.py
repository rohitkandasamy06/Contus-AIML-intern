import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt

# 1. Define your downloaded local physical file name
csv_filename = "student_results.csv"

print(f"Reading student dataset from local file: {csv_filename}...", flush=True)
try:
    df = pd.read_csv(csv_filename)
except FileNotFoundError:
    print(f"Error: Could not find '{csv_filename}'. Make sure it is in your project folder.", flush=True)
    exit()

print(f"Dataset successfully loaded! Records parsed: {df.shape[0]}", flush=True)

# 2. Separate independent factors (X) from the final outcome score (y)
features = ['Study_Hours', 'Attendance_Percentage', 'Sleep_Hours', 'Mock_Exam_Score']
X = df[features]
y = df['Final_Score']

# 3. Train-Test Split (80% Training, 20% Testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize and fit the Random Forest Regressor
# n_estimators=100 means the model will build 100 independent decision trees to vote
model = RandomForestRegressor(n_estimators=100, random_state=42)
print("\nTraining the Random Forest Ensemble Model (Building 100 Trees)...", flush=True)
model.fit(X_train, y_train)

# 5. Predict on the test data
predictions = model.predict(X_test)

# 6. Evaluate model error and variance scores
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\n================ RANDOM FOREST REGRESSION RESULTS ================", flush=True)
print(f"Model Accuracy Metric (R-squared Score): {r2 * 100:.2f}%", flush=True)
print(f"Mean Absolute Error (Average Score Deviance): {mae:.2f} Marks", flush=True)
print("====================================================================", flush=True)

# 7. Feature Importance Analysis
# Unlike linear regression which uses weights, Random Forest ranks columns by relative importance %
print("\nFeature Importance Breakdown (How much each factor matters to the trees):", flush=True)
importances = model.feature_importances_
for feature_name, importance in zip(features, importances):
    print(f" -> {feature_name}: {importance * 100:.2f}% importance score", flush=True)

# 8. Scenario Analysis: Predict a grade for an arbitrary student footprint
# Configuration format: [Study_Hours, Attendance_Percentage, Sleep_Hours, Mock_Exam_Score]
custom_student = [[6.5, 85, 7, 78]] 
predicted_grade = model.predict(custom_student)
print(f"\nPredicted Final Grade for the custom student profile: {predicted_grade[0]:.1f} / 100\n", flush=True)

# 9. Render Ultra-HD Premium Performance Visualizations
output_image_name = "student_rf_performance_plot.png"
print(f"Generating premium graphics matrix plot as '{output_image_name}'...", flush=True)

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(9, 7), facecolor='#F4F6F9')
ax.set_facecolor('#FFFFFF')

# High-End Visual: Deep Emerald/Teal markers with translucent overlap layering
ax.scatter(y_test, predictions, 
           color='#457B9D', 
           alpha=0.6, 
           s=60, 
           edgecolors='#FFFFFF', 
           linewidths=0.5, 
           label='Predicted vs Actual Student Profiles')

# Perfect performance alignment reference vector
perfect_line = [min(y_test), max(y_test)]
ax.plot(perfect_line, perfect_line, 
        color='#E63946', 
        linestyle='--', 
        linewidth=2.5, 
        label='Perfect Alignment Baseline (True = Predicted)')

# Formatting Title and Labels
ax.set_title('Academic Analytics: Random Forest Regression Evaluation', 
             fontsize=13, fontweight='bold', pad=15, color='#1D3557', name='Arial')
ax.set_xlabel('Actual Final Score (True Registry Marks)', fontsize=11, fontweight='semibold', labelpad=10, color='#4A4A4A')
ax.set_ylabel('Random Forest Predicted Score Evaluation', fontsize=11, fontweight='semibold', labelpad=10, color='#4A4A4A')

ax.grid(True, linestyle=':', alpha=0.6, color='#CCCCCC')

for spine in ['top', 'right', 'left', 'bottom']:
    ax.spines[spine].set_color('#E0E0E0')

ax.legend(loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#E0E0E0', fontsize=10)

# Export high-res graphic straight to your sidebar files
plt.savefig(output_image_name, dpi=300, bbox_inches='tight')
plt.close()

print("High-end student graphic exported successfully! View 'student_rf_performance_plot.png' in your sidebar panel.", flush=True)