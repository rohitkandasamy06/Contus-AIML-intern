import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. Define your downloaded local physical file name
csv_filename = "house_prices.csv"

print(f"Reading dataset from local file: {csv_filename}...", flush=True)
try:
    df = pd.read_csv(csv_filename)
except FileNotFoundError:
    print(f"Error: Could not find '{csv_filename}'. Make sure it is in the exact same folder as this script.", flush=True)
    exit()

print(f"Dataset successfully loaded! Total rows: {df.shape[0]}", flush=True)

# 2. Separate independent columns (X) from the target variable (y)
features = ['House_Age', 'Total_Rooms', 'Total_Bedrooms', 'Population', 'Median_Income']
X = df[features]
y = df['Price']

# 3. Split data into Training (80%) and Testing (20%) sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize and fit the Multiple Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# 5. Predict on the test data
predictions = model.predict(X_test)

# 6. Evaluate model error and variance scores
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\n================ MULTIPLE LINEAR REGRESSION RESULTS ================", flush=True)
print(f"Model R-squared (Accuracy Metric): {r2 * 100:.2f}%", flush=True)
print(f"Mean Absolute Error (Average Prediction Error): ${mae:.2f}", flush=True)
print("====================================================================", flush=True)

# 7. Print out individual feature weights to see their impact on house pricing
print("\nFeature Weights (Coefficients):", flush=True)
for feature_name, weight in zip(features, model.coef_):
    print(f" -> {feature_name}: {weight:.2f}", flush=True)
print(f" -> Base Intercept Constant (Y-intercept): ${model.intercept_:.2f}", flush=True)

# 8. Run a manual prediction for a single house layout
custom_house = [[15, 5, 3, 1200, 6.5]] 
predicted_value = model.predict(custom_house)
print(f"\nPredicted Valuation for the custom house profile: ${predicted_value[0]:.2f}\n", flush=True)

# 9. HIGH-END GRAPHICS GENERATION
output_image_name = "plot_output.png"
print(f"Generating premium graphics plot as '{output_image_name}'...", flush=True)

# Set a modern, clean grid style
plt.style.use('seaborn-v0_8-whitegrid')

# Initialize figure with professional proportions
fig, ax = plt.subplots(figsize=(9, 7), facecolor='#F8F9FA')
ax.set_facecolor('#FFFFFF')

# Premium Plotting: High-end translucent cyan/blue markers with subtle white borders
ax.scatter(y_test, predictions, 
           color='#0077B6', 
           alpha=0.6, 
           s=55, 
           edgecolors='#FFFFFF', 
           linewidths=0.5, 
           label='Predicted vs Actual Model Data')

# Premium Trendline: Sleek crimson dash representing flawless baseline mapping
perfect_line = [min(y_test), max(y_test)]
ax.plot(perfect_line, perfect_line, 
        color='#E63946', 
        linestyle='--', 
        linewidth=2.5, 
        label='Perfect Alignment Baseline ($Y = \hat{Y}$)')

# High-End Formatting: Convert large numbers to clean '$250k' labels dynamically
formatter = ticker.FuncFormatter(lambda x, pos: f"${int(x/1000)}k")
ax.xaxis.set_major_formatter(formatter)
ax.yaxis.set_major_formatter(formatter)

# Typography & Visual Hierarchy
ax.set_title('House Price Analytics: Multiple Linear Regression Evaluation', 
             fontsize=14, fontweight='bold', pad=15, color='#1D3557', name='Arial')
ax.set_xlabel('Actual Valuation Market Price', fontsize=11, fontweight='semibold', labelpad=10, color='#4A4A4A')
ax.set_ylabel('Model Predicted Valuation Estimates', fontsize=11, fontweight='semibold', labelpad=10, color='#4A4A4A')

# Polish gridlines to look soft and unintrusive
ax.grid(True, linestyle=':', alpha=0.6, color='#CCCCCC')

# Sophisticated Clean Borders (Despining excess frame lines)
for spine in ['top', 'right', 'left', 'bottom']:
    ax.spines[spine].set_color('#E0E0E0')

# Render a modern, rounded background legend box
ax.legend(loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#E0E0E0', fontsize=10)

# CRITICAL EXPORT: Render at Ultra-HD 300 DPI print quality
plt.savefig(output_image_name, dpi=300, bbox_inches='tight')
plt.close()

print("High-end graphic generated successfully! View 'plot_output.png' in your sidebar panel.", flush=True)