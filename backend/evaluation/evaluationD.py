# evaluation/evaluate_model_d_yield.py

import pandas as pd, joblib
from utility import evaluate_regressor, explain_model

model = joblib.load("backend/models/pkl/yeild_model.pkl")
data = pd.read_csv("data/yield_prediction_dataset.csv")
label_encoders = joblib.load("backend/models/pkl/encoders.pkl")

target = "Yield"
X = data.drop(columns=["Date","State","District","Season","Fertilizer_Name","Yield"])
y = data[target]

for col in X.select_dtypes(include="object").columns:
    X[col] = label_encoders[col].transform(X[col])

r2, rmse, mae = evaluate_regressor(model, X, y, "Yield")
top = explain_model(model, X, "Yield")

print(f"\n✅ Model D - R²: {r2:.3f} | RMSE: {rmse:.3f} | MAE: {mae:.3f}")
print("🏆 Top Features:", ", ".join(top.index))
