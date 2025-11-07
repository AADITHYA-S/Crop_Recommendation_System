import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
df = pd.read_csv(r"C:\ABHIRAM\Mini Project\crop_system\data\yield_prediction_dataset.csv")

# Columns to encode
categorical_cols = ['Crop', 'Crop_Stage', 'Soil_Type', 'Fertilizer_Name', 'Season']

# Encode each categorical column
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le  # store encoder for later inverse transform if needed

print("✅ Encoding complete. Encoded columns:")
print(categorical_cols)

# Save the encoded dataset
joblib.dump(label_encoders,"backend/models/pkl/encoders.pkl")
