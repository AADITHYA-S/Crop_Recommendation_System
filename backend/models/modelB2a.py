import pandas as pd
import joblib
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, mean_squared_error

# ------------------------
# Load data
# ------------------------
df = pd.read_csv("data/fertilizer_dataset_full.csv")
label_encoders = joblib.load("backend/models/pkl/encoders.pkl")

# ------------------------
# Recommended features
# ------------------------
features = [
    "Temperature", "Humidity", "Moisture",
    "Soil_Type", "Crop",
    "Nitrogen", "Phosphorous", "Potassium"
]

targets = ["N_need", "P_need", "K_need"]

# Encode categorical features
for col in ["Crop", "Soil_Type"]:
    le = label_encoders[col]
    df[col] = df[col].apply(lambda v: le.transform([v])[0] if v in le.classes_ else -1)

X = df[features]

# Impute missing
imputer = SimpleImputer(strategy="median")
X = pd.DataFrame(imputer.fit_transform(X), columns=features)

# ------------------------
# Train 3 models
# ------------------------
models = {}
kf = KFold(n_splits=5, shuffle=True, random_state=42)

for target in targets:
    print(f"\n🧪 Training model for {target}")

    y = df[target]

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        ))
    ])

    scores = cross_val_score(
        pipeline, X, y, cv=kf, scoring="r2", n_jobs=-1
    )

    print(f"CV R² for {target}: {scores.mean():.3f} ± {scores.std():.3f}")

    # fit final
    pipeline.fit(X, y)
    models[target] = pipeline

# Save models
joblib.dump(models["N_need"], "backend/models/pkl/N_need_model.pkl")
joblib.dump(models["P_need"], "backend/models/pkl/P_need_model.pkl")
joblib.dump(models["K_need"], "backend/models/pkl/K_need_model.pkl")

print("\n🎉 All 3 nutrient need models trained and saved!")
