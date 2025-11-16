# evaluation/evaluate_model_c_irrigation.py

import pandas as pd, joblib
from utility import evaluate_regressor, explain_model

model = joblib.load("backend/models/pkl/irrigation_model.pkl")
data = pd.read_csv("data/irrigation_dataset.csv")
label_encoders = joblib.load("backend/models/pkl/encoders.pkl")

target = "Irrigation_Level"
X = data.drop(columns=["Irrigation_Level","Date","State","District"])
y = data[target]

for col in X.select_dtypes(include="object").columns:
    X[col] = label_encoders[col].transform(X[col])

r2, rmse, mae = evaluate_regressor(model, X, y, "Irrigation")
top = explain_model(model, X, "Irrigation")

print(f"\n✅ Model C - R²: {r2:.3f} | RMSE: {rmse:.3f} | MAE: {mae:.3f}")
print("🏆 Top Features:", ", ".join(top.index))
