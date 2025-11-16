# evaluation/utils.py

import pandas as pd
import numpy as np
import shap
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    r2_score, mean_squared_error, mean_absolute_error
)
from sklearn.metrics import ConfusionMatrixDisplay
import os
import time

os.makedirs("evaluation/plots", exist_ok=True)


# -----------------------------
# 🔹 CLASSIFICATION EVALUATION
# -----------------------------
def evaluate_classifier(model, X, y, model_name):
    """Evaluate classification models"""
    y_pred = model.predict(X)
    acc = accuracy_score(y, y_pred)
    report = classification_report(y, y_pred, output_dict=True)
    ConfusionMatrixDisplay(confusion_matrix(y, y_pred)).plot()
    plt.title(f"{model_name} - Confusion Matrix")
    plt.savefig(f"evaluation/plots/{model_name}_confusion_matrix.png", dpi=300)
    plt.close()
    return acc, report


# -----------------------------
# 🔹 REGRESSION EVALUATION
# -----------------------------
def evaluate_regressor(model, X, y, model_name):
    """Evaluate regression models"""
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    mae = mean_absolute_error(y, y_pred)

    plt.scatter(y, y_pred, alpha=0.6)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
    plt.xlabel("Actual")
    plt.ylabel("Predicted")
    plt.title(f"{model_name} - Actual vs Predicted")
    plt.savefig(f"evaluation/plots/{model_name}_actual_vs_pred.png", dpi=300)
    plt.close()

    return r2, rmse, mae


# -----------------------------
# 🔹 SHAP EXPLAINABILITY
# -----------------------------
def explain_model(model, X, model_name, sample_size=1000):
    """Compute and plot SHAP values for feature importance (handles multiclass safely)."""
    import shap, numpy as np, pandas as pd, matplotlib.pyplot as plt, time, os

    start_time = time.time()
    feature_names = None

    # 1️⃣ Auto-detect feature names
    if hasattr(model, "feature_names_in_"):
        feature_names = list(model.feature_names_in_)
    elif hasattr(model, "get_booster"):  # XGBoost
        booster = model.get_booster()
        feature_names = getattr(booster, "feature_names", None)
    elif hasattr(model, "named_steps"):  # Pipeline
        for _, step in model.named_steps.items():
            if hasattr(step, "feature_names_in_"):
                feature_names = list(step.feature_names_in_)
                break

    # 2️⃣ Convert ndarray → DataFrame
    if isinstance(X, np.ndarray):
        ncols = X.shape[1]
        if feature_names and len(feature_names) == ncols:
            X = pd.DataFrame(X, columns=feature_names)
        else:
            X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(ncols)])
            print(f"⚠️ Using fallback feature names: feature_0..feature_{ncols-1}")

    n_samples, n_features = X.shape
    print(f"\n🔍 Running SHAP for {model_name} on {n_samples} samples × {n_features} features...")

    # 3️⃣ Take sample for performance
    X_sample = X.sample(min(len(X), sample_size), random_state=42)

    # 4️⃣ Compute SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # 5️⃣ Handle multiclass or regression
    if isinstance(shap_values, list):
        print(f"🧮 Detected multiclass SHAP with {len(shap_values)} classes")
        # shap_values = list of arrays, each (n_samples, n_features)
        shap_array = np.stack([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
        # shap_array shape: (n_classes, n_features)
        mean_abs_shap = shap_array.mean(axis=0)  # collapse to (n_features,)
    else:
        shap_array = np.abs(np.array(shap_values))
        # if 3D (e.g., (n_classes, n_samples, n_features)), collapse extra axes
        if shap_array.ndim == 3:
            shap_array = shap_array.mean(axis=(0, 1))
        elif shap_array.ndim == 2:
            shap_array = shap_array.mean(axis=0)
        mean_abs_shap = shap_array

    # 6️⃣ Shape alignment safety
    if len(mean_abs_shap) != X_sample.shape[1]:
        diff = len(mean_abs_shap) - X_sample.shape[1]
        print(f"⚠️ Adjusting SHAP array length: trimming {diff} to match X")
        n = min(len(mean_abs_shap), X_sample.shape[1])
        mean_abs_shap = mean_abs_shap[:n]
        X_sample = X_sample.iloc[:, :n]

    # 7️⃣ Build feature importance Series
    top_features = pd.Series(mean_abs_shap, index=X_sample.columns).sort_values(ascending=False)

    # 8️⃣ Plot SHAP (safe)
    try:
        shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
        plt.title(f"{model_name} - SHAP Feature Importance")
        plt.savefig(f"evaluation/plots/{model_name}_feature_importance.png", dpi=300)
        plt.close()

        shap.summary_plot(shap_values, X_sample, show=False)
        plt.title(f"{model_name} - SHAP Summary Plot")
        plt.savefig(f"evaluation/plots/{model_name}_shap_summary.png", dpi=300)
        plt.close()
    except Exception as e:
        print("⚠️ Skipped SHAP plots due to error:", e)

    print(f"🏆 Top features for {model_name}: {list(top_features.head(5).index)}")
    print(f"✅ Completed SHAP for {model_name} in {time.time() - start_time:.2f} seconds.")
    return top_features.head(5)
