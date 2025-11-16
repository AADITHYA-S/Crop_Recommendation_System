"""
fertilizer_classifier_pipeline.py

Usage:
    python fertilizer_classifier_pipeline.py

What it does:
- Loads data
- Loads pre-saved LabelEncoders dictionary (encoders.pkl)
- Encodes categorical columns safely (unknown classes -> -1)
- Imputes missing numeric values with median
- Builds a Pipeline: StandardScaler + XGBClassifier
- Runs Stratified K-Fold CV (5 folds) and prints fold accuracies & mean/std
- Fits final classifier on full data and saves:
    - backend/models/pkl/fertilizer_type_model.pkl
    - backend/models/pkl/fertilizer_scaler_for_classifier.pkl
"""

import os
import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

# === CONFIG ===
DATA_PATH = r'C:\ABHIRAM\Mini Project\crop_system\data\fertilizer_dataset_full.csv'
ENCODERS_PATH = r"C:\ABHIRAM\Mini Project\crop_system\backend\models\pkl\encoders.pkl"
OUT_MODEL_PATH = r"backend/models/pkl/fertilizer_type_model.pkl"
OUT_SCALER_PATH = r"backend/models/pkl/fertilizer_scaler_for_classifier.pkl"
RANDOM_STATE = 42
N_SPLITS = 5

fertilizer_groups = {
    "Urea": "Nitrogenous",
    "20-20": "Nitrogenous",
    "DAP": "Phosphatic",
    "14-35-14": "Phosphatic",
    "10-26-26": "Phosphatic",
    "MOP": "Potassic",
    "28-28": "Potassic",
    "17-17-17": "Balanced",
    "Compost": "Organic",
    "Vermicompost": "Organic",
    "Organic Manure": "Organic",
    "Green Manure": "Organic",
}



# === Load data ===
df = pd.read_csv(DATA_PATH)
print("Loaded data:", df.shape)
df["Fertilizer_Group"] = df["Fertilizer_Name"].map(fertilizer_groups)

# === Safe encoding using existing encoders ===

le_group = LabelEncoder()
df["Fertilizer_Group"] = le_group.fit_transform(df["Fertilizer_Group"])
label_encoders = joblib.load(ENCODERS_PATH)  # dict: column_name -> LabelEncoder
cat_cols = ["Crop", "Crop_Stage", "Soil_Type", "Fertilizer_Name"]

for col in cat_cols:
    if col in df.columns and col in label_encoders:
        le = label_encoders[col]
        # Map unknown classes to -1
        def safe_transform(v):
            try:
                # check membership by converting to string if needed
                if v in le.classes_:
                    return int(le.transform([v])[0])
            except Exception:
                pass
            return -1
        df[col] = df[col].apply(safe_transform)
print("✅ Encoding done for categorical columns (unknown -> -1)")

# === Features and target ===
features = ["Crop","Nitrogen","Potassium","Phosphorous","N_need","P_need","K_need"]
target = "Fertilizer_Group"

# Basic check
for f in features:
    if f not in df.columns:
        raise ValueError(f"Missing feature column: {f}")

X = df[features].copy()
y = df[target].astype(int)  # encoded labels

# Fill numeric missing values with median (simple imputer)
imputer = SimpleImputer(strategy="median")
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

# Create pipeline: scaler + classifier
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", XGBClassifier(
        objective='multi:softprob',
        eval_metric='mlogloss',
        n_estimators=300,
        learning_rate=0.1,
        max_depth=5,
        use_label_encoder=False,
        random_state=RANDOM_STATE,
        verbosity=0
    ))
])

# === Cross-validation (Stratified) ===
cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
scores = cross_val_score(pipeline, X_imputed, y, cv=cv, scoring='accuracy', n_jobs=-1)
print(f"Cross-validation accuracies (Stratified {N_SPLITS}-fold): {scores}")
print(f"Mean accuracy: {scores.mean():.4f} ± {scores.std():.4f}")

# === Optional single train/test split evaluation (not strictly necessary) ===
X_train, X_test, y_train, y_test = train_test_split(
    X_imputed, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
print("\nHoldout Test Accuracy:", accuracy_score(y_test, y_pred))
# Load fertilizer label encoder names for readable report if available
fert_le = label_encoders.get("Fertilizer_Group", None)
if fert_le is not None:
    target_names = list(fert_le.classes_)
else:
    target_names = None
print("Classification report:")
print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

# === Retrain on full data and save the model and scaler ===
pipeline.fit(X_imputed, y)
os.makedirs(os.path.dirname(OUT_MODEL_PATH), exist_ok=True)
joblib.dump(pipeline, OUT_MODEL_PATH)
print("Saved classifier pipeline to:", OUT_MODEL_PATH)

# Save the scaler separately (useful for other preprocessing)
scaler = pipeline.named_steps["scaler"]
joblib.dump(scaler, OUT_SCALER_PATH)
print("Saved scaler to:", OUT_SCALER_PATH)

print("All done for classification pipeline.")
