import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split,StratifiedKFold,cross_val_score
import joblib
from sklearn.preprocessing import LabelEncoder,StandardScaler
from sklearn.metrics import classification_report,accuracy_score,r2_score,mean_squared_error
from xgboost import XGBClassifier,XGBRegressor

df=pd.read_csv(r'C:\ABHIRAM\Mini Project\crop_system\data\fertilizer_dataset_full.csv')


#Encode categorical features
label_encoders=joblib.load(r"C:\ABHIRAM\Mini Project\crop_system\backend\models\pkl\encoders.pkl")
cat_col=["Crop","Crop_Stage","Soil_Type","Fertilizer_Name"]

for col in cat_col:
    if col in label_encoders and col in df.columns:
        le = label_encoders[col]
        df[col] = df[col].apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else -1
        )

print("✅ Encoding done for:", cat_col)


#Fill missing values
# df = df.fillna(df.median())



#Features and Targets
features=["Temperature","Humidity","Moisture","Soil_Type","Crop","Nitrogen","Potassium","Phosphorous","N_need","P_need","K_need"]
X=df[features]
y_class=df["Fertilizer_Name"]
y_reg=df["Fertilizer Quantity (kg/acre)"]

#Scaleing
scaler=StandardScaler()
X_scaled=scaler.fit_transform(X)

#training test split
# Split once only!
X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
    X_scaled, y_class, y_reg,
    test_size=0.2,
    random_state=42,
    stratify=y_class
)
print("Data split into training and test")

#Training XGBoost classifier
clf=XGBClassifier(
    objective='multi:softmax',
    eval_metric='mlogloss',
    num_class=len(label_encoders["Fertilizer_Name"].classes_),
    n_estimators=300,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)
clf.fit(X_train,y_class_train)

reg=XGBRegressor(
    objective='reg:squarederror',
    n_estimators=400,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)
reg.fit(X_train,y_reg_train)
print("Model trained")

#Predict
y_pred_class=clf.predict(X_test)
print("\nFertilizer Type classifier")
print("Acuuracy Score:",accuracy_score(y_class_test,y_pred_class))

fert_le = label_encoders["Fertilizer_Name"]
print("Classification Report:\n",
      classification_report(
          y_class_test, 
          y_pred_class, 
          labels=range(len(fert_le.classes_)),      # e.g. 0,1,2,... for each fertilizer
          target_names=fert_le.classes_,            # ['Urea', 'DAP', '14-35-14', ...]
          zero_division=0
      )
)


cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(clf, X_scaled, y_class, cv=cv, scoring='accuracy')
print(f"Cross-validation accuracies: {scores}")
print(f"Mean accuracy: {np.mean(scores):.4f} ± {np.std(scores):.4f}")

#Regression
y_pred_reg=reg.predict(X_test)
print("\nFertilizer Quantity Regressor")
print("R2 Score:", round(r2_score(y_reg_test,y_pred_reg),3))
print("RMSE:",round((mean_squared_error(y_reg_test, y_pred_reg) ** 0.5),3))

#Retrain on full data
clf.fit(X_scaled, y_class)
reg.fit(X_scaled, y_reg)
print("Final model retrained on full data")

#save model and encoders
joblib.dump(clf,"backend/models/pkl/fertilizer_type_model.pkl")

joblib.dump(scaler,"backend/models/pkl/fertilizer_scaler.pkl")
print("Model saved")
  


