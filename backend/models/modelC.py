import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np

# -------------------------
# Load data
# -------------------------
df = pd.read_csv(r"C:\ABHIRAM\Mini Project\crop_system\data\irrigation_dataset.csv")

# Select features and targets
features = ["Crop", "Soil_Moisture", "Rainfall", "NDVI", "Water_Requirement"]
target = "Irrigation_Level"
X = df[features].copy()
y = df[target]

# -------------------------
# Encode categorical columns
# -------------------------
label_encoders = joblib.load(
    r"C:\ABHIRAM\Mini Project\crop_system\backend\models\pkl\encoders.pkl"
)

cat_col = X.select_dtypes(include="object").columns
for col in cat_col:
    if col in label_encoders:
        le = label_encoders[col]
        X[col] = X[col].apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else -1
        )

print("✅ Encoding done for:", list(cat_col))


# -------------------------
# Train-test split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print("Train and test split done")

# -------------------------
# Scaling
# -------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)   # IMPORTANT FIX

# -------------------------
# Train model
# -------------------------
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train_scaled, y_train)
print("Model training done")

# -------------------------
# Evaluate on Holdout Test
# -------------------------
preds = model.predict(X_test_scaled)
print("Holdout R2 Score:", round(r2_score(y_test, preds), 3))
print("Holdout RMSE:", round((mean_squared_error(y_test, preds)**0.5), 3))

# -------------------------
# K-FOLD CROSS VALIDATION
# -------------------------
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# CV with scaled features
X_scaled_for_cv = scaler.fit_transform(X)

cv_scores = cross_val_score(
    model,
    X_scaled_for_cv,
    y,
    cv=kf,
    scoring="r2"
)

print("\n📊 Cross Validation R2 Scores:", cv_scores)
print("Mean R2:", round(np.mean(cv_scores), 4))
print("Std R2:", round(np.std(cv_scores), 4))

# -------------------------
# Retrain on full scaled data
# -------------------------
model.fit(X_scaled_for_cv, y)
print("Final model retrained on full data")

# -------------------------
# Save model & scaler
# -------------------------
joblib.dump(model, "backend/models/pkl/irrigation_model.pkl")
joblib.dump(scaler, "backend/models/pkl/irrigation_scaler.pkl")

print("\n💾 Model and scaler saved successfully.")
