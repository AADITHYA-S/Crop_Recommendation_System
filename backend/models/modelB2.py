"""
fertilizer_regressor_pipeline.py

Usage:
    python fertilizer_regressor_pipeline.py

What it does:
- Loads data
- Loads pre-saved LabelEncoders dictionary (encoders.pkl) and encodes categorical columns safely
- Imputes missing numeric values with median
- Applies log1p transform to skewed target (Fertilizer Quantity)
- Builds a Pipeline: StandardScaler + XGBRegressor
- Runs K-Fold CV (5 folds) with neg_mean_squared_error and prints RMSE + R2 per fold
- Fits final regressor on full data (trained on log1p(y)) and saves:
    - backend/models/pkl/fertilizer_quantity_model.pkl
    - backend/models/pkl/fertilizer_scaler_for_regressor.pkl

Note: Predictions returned are inverse-transformed with expm1.
"""

import os
import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.metrics import r2_score, root_mean_squared_error
from xgboost import XGBRegressor

# === CONFIG ===
DATA_PATH = r'C:\ABHIRAM\Mini Project\crop_system\data\fertilizer_dataset_full.csv'
ENCODERS_PATH = r"C:\ABHIRAM\Mini Project\crop_system\backend\models\pkl\encoders.pkl"
OUT_MODEL_PATH = r"backend/models/pkl/fertilizer_quantity_model.pkl"
OUT_SCALER_PATH = r"backend/models/pkl/fertilizer_scaler_for_regressor.pkl"
RANDOM_STATE = 42
N_SPLITS = 5

# === Load data ===
df = pd.read_csv(DATA_PATH)
print("Loaded data:", df.shape)

# === Safe encoding using existing encoders ===
label_encoders = joblib.load(ENCODERS_PATH)  # dict: column_name -> LabelEncoder
cat_cols = ["Crop", "Crop_Stage", "Soil_Type", "Fertilizer_Name"]

for col in cat_cols:
    if col in df.columns and col in label_encoders:
        le = label_encoders[col]
        def safe_transform(v):
            try:
                if v in le.classes_:
                    return int(le.transform([v])[0])
            except Exception:
                pass
            return -1
        df[col] = df[col].apply(safe_transform)
print("✅ Encoding done for categorical columns (unknown -> -1)")

# === Features and target ===
features = ["Temperature","Humidity","Moisture","Soil_Type","Crop","Nitrogen","Potassium","Phosphorous","N_need","P_need","K_need"]
target_col = "Fertilizer Quantity (kg/acre)"

for f in features:
    if f not in df.columns:
        raise ValueError(f"Missing feature column: {f}")
if target_col not in df.columns:
    raise ValueError(f"Missing target column: {target_col}")

X = df[features].copy()
y_raw = df[target_col].astype(float).copy()

# Impute numeric missing values with median
imputer = SimpleImputer(strategy="median")
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

# Log-transform the target to handle skew (train on y_log)
y_log = np.log1p(y_raw)   # log(1 + y)

# === Build pipeline ===
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("reg", XGBRegressor(
        objective='reg:squarederror',
        n_estimators=800,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        verbosity=0
    ))
])

# === Cross-validation (KFold) on the log-transformed target ===
kf = KFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)

# We use neg_mean_squared_error for scoring, convert to RMSE
cv_mse_scores = cross_val_score(pipeline, X_imputed, y_log, cv=kf, scoring='neg_mean_squared_error', n_jobs=-1)
cv_rmse = np.sqrt(-cv_mse_scores)
print(f"Regression CV RMSE on log(y): {cv_rmse}")
print(f"Mean RMSE (log space): {cv_rmse.mean():.4f} ± {cv_rmse.std():.4f}")

# Optionally show R2 on each fold (apply pipeline inside loop to compute r2 on inverse-transformed predictions)
r2_scores = []
fold = 0
for train_idx, test_idx in kf.split(X_imputed):
    fold += 1
    X_tr, X_te = X_imputed.iloc[train_idx], X_imputed.iloc[test_idx]
    y_tr, y_te = y_log.iloc[train_idx], y_log.iloc[test_idx]

    pipeline.fit(X_tr, y_tr)
    y_pred_log = pipeline.predict(X_te)
    # invert transform
    y_pred = np.expm1(y_pred_log)
    y_true = np.expm1(y_te)

    r2 = r2_score(y_true, y_pred)
    r2_scores.append(r2)
    rmse = root_mean_squared_error(y_true, y_pred)
    print(f"Fold {fold} -> R2: {r2:.4f}, RMSE: {rmse:.4f}")

print(f"Mean R2 (real units): {np.mean(r2_scores):.4f} ± {np.std(r2_scores):.4f}")

# === Optional holdout evaluation ===
X_train, X_test, y_train_log, y_test_log = train_test_split(X_imputed, y_log, test_size=0.2, random_state=RANDOM_STATE)
pipeline.fit(X_train, y_train_log)
y_pred_log_test = pipeline.predict(X_test)
y_pred_test = np.expm1(y_pred_log_test)
y_test_true = np.expm1(y_test_log)

print("\nHoldout evaluation (inverse-transformed):")
print("R2:", r2_score(y_test_true, y_pred_test))
print("RMSE:", root_mean_squared_error(y_test_true, y_pred_test))

# === Retrain on full data and save model & scaler ===
pipeline.fit(X_imputed, y_log)   # train on log target
os.makedirs(os.path.dirname(OUT_MODEL_PATH), exist_ok=True)
joblib.dump(pipeline, OUT_MODEL_PATH)
print("Saved regressor pipeline to:", OUT_MODEL_PATH)

scaler = pipeline.named_steps["scaler"]
joblib.dump(scaler, OUT_SCALER_PATH)
print("Saved scaler to:", OUT_SCALER_PATH)

print("Important: predictions from this regressor will be in log-space. Use np.expm1(pred) to get quantity in original units.")
print("All done for regression pipeline.")
