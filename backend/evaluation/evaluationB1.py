import shap
import joblib
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 🔹 Load Model & Encoders
# -----------------------------
model = joblib.load("backend/models/pkl/fertilizer_type_model.pkl")  # pipeline
label_encoders = joblib.load("backend/models/pkl/encoders.pkl")

# -----------------------------
# 🔹 Load Data
# -----------------------------
df = pd.read_csv("data/fertilizer_dataset_full.csv")

# -----------------------------
# 🔹 Fertilizer Group Mapping
# -----------------------------
group_map = {
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

df["Fertilizer_Group"] = df["Fertilizer_Name"].map(group_map)

# Encode grouped target
from sklearn.preprocessing import LabelEncoder
group_encoder = LabelEncoder()
df["Fertilizer_Group_Encoded"] = group_encoder.fit_transform(df["Fertilizer_Group"])

# -----------------------------
# 🔹 SAMPLE a subset of data
# -----------------------------
SAMPLE_SIZE = 500   # you can reduce to 200 if needed
df_sample = df.sample(SAMPLE_SIZE, random_state=42).reset_index(drop=True)

print(f"📉 Using sampled subset for SHAP: {df_sample.shape[0]} rows")

# -----------------------------
# 🔹 Define Features
# -----------------------------
features = [
    "Temperature","Humidity","Moisture","Soil_Type","Crop",
    "Nitrogen","Potassium","Phosphorous",
    "N_need","P_need","K_need"
]
X = df_sample[features].copy()

# -----------------------------
# 🔹 Encode categorical features
# -----------------------------
for col in ["Crop", "Soil_Type"]:
    le = label_encoders[col]
    X[col] = X[col].apply(lambda v: le.transform([v])[0] if v in le.classes_ else -1)

# -----------------------------
# 🔹 Scale features using your pipeline scaler
# -----------------------------
scaler = model.named_steps["scaler"]
X_scaled = scaler.transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=features)

# -----------------------------
# 🔹 Extract classifier from pipeline
# -----------------------------
clf = model.named_steps["clf"]

# -----------------------------
# 🔹 SHAP Explainer
# -----------------------------
explainer = shap.TreeExplainer(clf)
print("⚙ Computing SHAP values on sampled dataset...")
shap_values = explainer.shap_values(X_scaled)

# -----------------------------
# 🔹 SHAP Summary (Beeswarm)
# -----------------------------
shap.summary_plot(
    shap_values,
    X_scaled,
    feature_names=features,
    class_names=group_encoder.classes_,
    show=False
)
plt.tight_layout()
plt.savefig("evaluation/shap_grouped_beeswarm_sampled.png", dpi=300)
plt.show()

# -----------------------------
# 🔹 SHAP Summary (Bar Plot)
# -----------------------------
shap.summary_plot(
    shap_values,
    X_scaled,
    plot_type="bar",
    feature_names=features,
    class_names=group_encoder.classes_,
    show=False
)
plt.tight_layout()
plt.savefig("evaluation/shap_grouped_bar_sampled.png", dpi=300)
plt.show()

print("\n🎉 SHAP plots (sampled) saved:")
print(" - evaluation/shap_grouped_beeswarm_sampled.png")
print(" - evaluation/shap_grouped_bar_sampled.png")
