import pandas as pd
from sklearn.preprocessing import LabelEncoder,StandardScaler
from sklearn.metrics import r2_score,mean_squared_error
from sklearn.model_selection import train_test_split, KFold,cross_val_score
from sklearn.ensemble import RandomForestRegressor
import joblib

#load data
df=pd.read_csv(r"C:\ABHIRAM\Mini Project\crop_system\data\irrigation_dataset.csv")

#select features and targets
target="Irrigation_Level"
X=df.drop(columns=["Irrigation_Level","Date","State","District"])
y=df[target]

#Encode categorical columns
label_encoders=joblib.load(r"C:\ABHIRAM\Mini Project\crop_system\backend\models\pkl\encoders.pkl")
cat_col = X.select_dtypes(include="object").columns
for col in cat_col:
    if col in label_encoders and col in df.columns:
        le = label_encoders[col]
        X[col] = X[col].apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else -1
        )

print("✅ Encoding done for:", cat_col)


#Train test split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)
print("Train and test split done")


#Scaling
scaler=StandardScaler()
X_train_scaled=scaler.fit_transform(X_train)
X_test_scaled=scaler.fit_transform(X_test)

#train model
model=RandomForestRegressor(n_estimators=200,random_state=42)
model.fit(X_train_scaled,y_train)
print("Model training done")

#Evaluate
preds=model.predict(X_test_scaled)
print("R2 score:",round(r2_score(y_test,preds),3))
print("RMSE:",round((mean_squared_error(y_test, preds) ** 0.5),3))

#retrain on full data
X_scaled=scaler.fit_transform(X)
model.fit(X,y)
print("Final model retrained on full data")

#Save model and encoders
joblib.dump(model,"backend/models/pkl/irrigation_model.pkl")
print("Model and encoders saved")