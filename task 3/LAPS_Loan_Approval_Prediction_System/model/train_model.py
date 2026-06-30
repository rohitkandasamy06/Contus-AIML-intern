import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "loan_data.csv")

df = pd.read_csv(DATA_PATH)

cat_cols = ["gender", "married", "education", "self_employed", "property_area"]
target_col = "loan_status"

encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

target_le = LabelEncoder()
df[target_col] = target_le.fit_transform(df[target_col])

X = df.drop(["loan_id", target_col], axis=1)
y = df[target_col]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=2,
    min_samples_leaf=1,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

preds = model.predict(X_test)
acc = accuracy_score(y_test, preds)
print("Accuracy:", acc)
print("\nClassification report:\n", classification_report(y_test, preds, target_names=target_le.classes_))
print("Confusion matrix:\n", confusion_matrix(y_test, preds))

importances = sorted(zip(X.columns, model.feature_importances_), key=lambda x: -x[1])
print("\nFeature importance:")
for name, score in importances:
    print(f"  {name}: {score:.4f}")

joblib.dump(model, os.path.join(BASE_DIR, "model.pkl"))
joblib.dump(encoders, os.path.join(BASE_DIR, "encoders.pkl"))
joblib.dump(target_le, os.path.join(BASE_DIR, "target_encoder.pkl"))
joblib.dump(list(X.columns), os.path.join(BASE_DIR, "columns.pkl"))
print("\nModel saved successfully!")
