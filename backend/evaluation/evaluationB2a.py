import shap
import joblib
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------
# Load models
# -------------------------------------
N_model = joblib.load("backend/models/pkl/N_need_model.pkl")
P_model = joblib.load("backend/models/pkl/P_need_model.pkl")
K_model = joblib.load("backend/models/pkl/K_need_model.pkl")

encoders = joblib.load("backend/models/pkl/encoders.pkl")

# -------------------------------------
# Load data (use a sample for speed)
# -------------------------------------
df = pd.read_csv("data/fertilizer_dataset_full.csv")

SAMPLE = 500
df = df.sample(SAMPLE, random_state=42)

# -------------------------------------
# Feature list
# -------------------------------------
features = [
    "Temperature","Humidity","Moisture",
    "Soil_Type", "Crop",
    "Nitrogen","Phosphorous","Potassium"
]

X = df[features].copy()

# Encode categories
for col in ["Crop", "Soil_Type"]:
    le = encoders[col]
    X[col] = X[col].apply(lambda v: le.transform([v])[0] if v in le.classes_ else -1)

# -------------------------------------
# SHAP for each nutrient model
# -------------------------------------
def run_shap(model, X, name):
    print(f"\n🔍 Running SHAP for {name} model...")

    # Extract model component from pipeline
    scaler = model.named_steps["scaler"]
    reg = model.named_steps["model"]

    X_scaled = scaler.transform(X)
    
    explainer = shap.TreeExplainer(reg)
    shap_values = explainer.shap_values(X_scaled)

    # Beeswarm
    shap.summary_plot(
        shap_values, 
        X_scaled, 
        feature_names=features,
        show=False
    )
    plt.title(f"{name} Need – SHAP Beeswarm")
    plt.savefig(f"evaluation/shap_{name}_beeswarm.png", dpi=300)
    plt.show()

    # Bar plot
    shap.summary_plot(
        shap_values,
        X_scaled,
        plot_type="bar",
        feature_names=features,
        show=False
    )
    plt.title(f"{name} Need – SHAP Feature Importance")
    plt.savefig(f"evaluation/shap_{name}_bar.png", dpi=300)
    plt.show()

# -------------------------------------
# Run SHAP for N, P, K models
# -------------------------------------
run_shap(N_model, X, "N")
run_shap(P_model, X, "P")
run_shap(K_model, X, "K")

print("\n🎉 SHAP plots saved for N, P, K nutrient models!")
