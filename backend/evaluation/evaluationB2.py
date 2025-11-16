# evaluation/evaluationB2.py

import pandas as pd
import joblib
from utility import evaluate_regressor, explain_model

# --------------------------
# 🔹 Load model and data
# --------------------------
model = joblib.load("backend/models/pkl/fertilizer_quantity_model.pkl")
data = pd.read_csv("data/fertilizer_dataset_full.csv")

label_encoders = joblib.load("backend/models/pkl/encoders.pkl")
scaler = joblib.load("backend/models/pkl/fertilizer_scaler.pkl")

# --------------------------
# 🔹 Define features / target
# --------------------------
features = [
    "Temperature", "Humidity", "Moisture", "Soil_Type", "Crop",
    "Nitrogen", "Potassium", "Phosphorous",
    "N_need", "P_need", "K_need"
]
target = "Fertilizer Quantity (kg/acre)"

X = data[features].copy()
y = data[target]

# --------------------------
# 🔹 Encode categorical columns
# --------------------------
for col in ["Crop", "Soil_Type"]:
    X.loc[:, col] = label_encoders[col].transform(X[col])

# --------------------------
# 🔹 Scale numeric features
# --------------------------
X_scaled = scaler.transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=features)

# --------------------------
# 🔹 Evaluate model performance
# --------------------------
r2, rmse, mae = evaluate_regressor(model, X_scaled, y, "Fertilizer_Quantity")

# --------------------------
# 🔹 Explain model with SHAP
# --------------------------
top = explain_model(model, X_scaled, "Fertilizer_Quantity")

# --------------------------
# 🔹 Print results
# --------------------------
print(f"\n✅ Model B2 – Fertilizer Quantity Evaluation")
print(f"R²: {r2:.4f} RMSE: {rmse:.4f} MAE: {mae:.4f}")
print("🏆 Top Features:", ", ".join(top.index))
