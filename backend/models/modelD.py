import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score,mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split,KFold,cross_val_score
import joblib

df=pd.read_csv("C:\ABHIRAM\Mini Project\crop_system\data\yield_prediction_dataset.csv")

#feature selection
target="Yield"
X=df.drop(columns=["Date","State","District","Season","Fertilizer_Name","Yield"])
y=df[target]

#encode categorical columns
label_encoders=joblib.load(r"C:\ABHIRAM\Mini Project\crop_system\backend\models\pkl\encoders.pkl")
cat_col = X.select_dtypes(include="object").columns
for col in cat_col:
    if col in label_encoders and col in df.columns:
        le = label_encoders[col]
        X[col] = X[col].apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else -1
        )

print("✅ Encoding done for:", cat_col)


#training and testing split
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)
print("Training and testing split done")

#train model
model=RandomForestRegressor(n_estimators=200,random_state=42)
model.fit(X_train,y_train)
print("Model training done")

#Evaluating model
pred=model.predict(X_test)
print("R2 Score:",round(r2_score(y_test,pred),3))
print("RMSE:",round((mean_squared_error(y_test,pred)**0.5),3))

#CV
cv = KFold(n_splits=5, shuffle=True, random_state=42)
cv_r2 = cross_val_score(model, X, y, cv=cv, scoring='r2')
print("Mean CV R²:", cv_r2.mean(), "±", cv_r2.std())

#feature importance
feat_imp = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
print(feat_imp.head(10))

#train on full data
model.fit(X,y)
print("Model trained on full data")

#save model
joblib.dump(model,"backend/models/pkl/yeild_model.pkl")
print("model saved")

