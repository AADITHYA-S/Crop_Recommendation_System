# evaluation/evaluate_model_a_crop_stage.py

import pandas as pd, joblib
from utility import evaluate_classifier, explain_model

model_A = joblib.load("backend/models/pkl/crop_stage_model.pkl")
data_A = pd.read_csv("data/combined_crop_stage_dataset.csv")
label_encoders = joblib.load("backend/models/pkl/encoders.pkl")

features = ['NDVI','humidity','days_since_sowing','Crop']
target = "Crop_Stage"

X_A = data_A[features]
y_A = data_A[target].str.lower()
X_A["Crop"] = label_encoders["Crop"].transform(X_A["Crop"])
y_A = label_encoders["Crop_Stage"].transform(y_A)

# acc, report = evaluate_classifier(model_A, X_A, y_A, "Crop_Stage")
# top = explain_model(model_A, X_A, "Crop_Stage")

# print(f"\n✅ Model A - Accuracy: {acc:.3f}")
# print("🏆 Top Features:", ", ".join(top.index))
import matplotlib.pyplot as plt
y_pred = model_A.predict(X_A)
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

cm = confusion_matrix(y_A, y_pred)
sns.heatmap(cm, annot=True, cmap="Blues", fmt="d")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Model A")
plt.show()
