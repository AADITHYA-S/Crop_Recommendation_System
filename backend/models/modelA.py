from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split,StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score
import pandas as pd
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.utils import shuffle

data = pd.read_csv("data/combined_crop_stage_dataset.csv")
data['Crop_Stage'] = data['Crop_Stage'].str.lower()

label_encoders=joblib.load(r"C:\ABHIRAM\Mini Project\crop_system\backend\models\pkl\encoders.pkl")
cat_col=["Crop","Crop_Stage"]
# Encode each categorical column
for col in cat_col:
    if col in label_encoders and col in data.columns:
        le = label_encoders[col]
        data[col] = data[col].apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else -1
        )

print("✅ Encoding done for:", cat_col)


features=['NDVI','humidity','days_since_sowing','Crop']
X=data[features]
print (X.columns)
y=data['Crop_Stage']
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)
print("Spliting Done")
#=======================================================================
model=RandomForestClassifier(n_estimators=150,random_state=42)
model.fit(X_train,y_train)

preds=model.predict(X_test)
print(classification_report(y_test, preds, target_names=label_encoders["Crop_Stage"].classes_))
print("Accuracy:", accuracy_score(y_test, preds))

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy')

print("Cross-Validation Accuracy Scores:", scores)
print("Mean Accuracy:", np.mean(scores))
print("Std Deviation:", np.std(scores))





# 2️⃣ Feature–label correlation
print("\n🔍 Feature–label correlation check:")
label_factorized = pd.factorize(data['Crop_Stage'])[0]
for col in X.columns:
    corr = np.corrcoef(X[col], label_factorized)[0,1]
    print(f"{col:15}: {corr:.3f}")



#Retrain model on entire dataset
model.fit(X_train,y_train)

# joblib.dump(model, "crop_stage_model.pkl")
joblib.dump(model, "backend/models/pkl/crop_stage_model.pkl")
print("Saved")









