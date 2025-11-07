from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
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


features=['NDVI','temp','PRECTOTCORR','humidity','days_since_sowing','Crop']
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
#======================================================================================
# xgb = XGBClassifier(
#     n_estimators=300,
#     learning_rate=0.05,
#     max_depth=6,
#     subsample=0.8,
#     colsample_bytree=0.8,
#     eval_metric='mlogloss',
#     random_state=42
# )

# xgb.fit(X_train, y_train)

# y_pred = xgb.predict(X_test)

# print("Accuracy:", accuracy_score(y_test, y_pred))
# print(classification_report(y_test, y_pred, target_names=stage_encoder.classes_))

# scores = cross_val_score(xgb, X, y, cv=5)
# print(scores.mean(), scores.std())

#==================================================================================================
# param_grid = {
#     'n_estimators': [200, 300, 400],
#     'max_depth': [4, 6, 8],               # Controls tree depth (higher = more complex)
#     'learning_rate': [0.05, 0.1],         # Controls step size (lower = more careful)
#     'subsample': [0.8, 1],                # Fraction of samples for each tree (regularization)
#     'colsample_bytree': [0.8, 1],         # Fraction of features to use in each tree
#     'gamma': [0, 1, 5],                   # Minimum loss reduction to make a further partition
#     'objective': ['multi:softmax'],       # Multi-class classification
#     'eval_metric': ['mlogloss'],          # Log-loss for multi-class
#     'num_class': [4]                      # Adjust according to the number of stages in your problem
# }

# xgb_model = XGBClassifier(random_state=42)

# grid_search = GridSearchCV(
#     estimator=xgb_model,
#     param_grid=param_grid,
#     cv=5,                                  # 5-fold cross-validation
#     n_jobs=-1,                             # Use all available CPUs
#     scoring='accuracy',                    # Metric to optimize (accuracy)
#     verbose=1                              # Shows progress
# )

# grid_search.fit(X_train, y_train)

# # Display the best parameters
# print("Best Parameters:", grid_search.best_params_)
# print("Best CV Score:", grid_search.best_score_)

# # Predict using the best model
# y_pred = grid_search.best_estimator_.predict(X_test)

# # Evaluate the model
# print("\nClassification Report:")
# print(classification_report(y_test, y_pred, target_names=label_encoders["Crop_Stage"].classes_))

# # Accuracy score
# print("Accuracy:", accuracy_score(y_test, y_pred))

#==========================================================================================




# # 2️⃣ Feature–label correlation
# print("\n🔍 Feature–label correlation check:")
# label_factorized = pd.factorize(data['Crop_Stage'])[0]
# for col in X.columns:
#     corr = np.corrcoef(X[col], label_factorized)[0,1]
#     print(f"{col:15}: {corr:.3f}")

# # 3️⃣ NDVI/time separability visual (optional)
# import seaborn as sns
# import matplotlib.pyplot as plt
# sns.scatterplot(data=data, x='days_since_sowing', y='NDVI', hue='Crop_Stage')
# plt.title("NDVI vs Days Since Sowing by Stage")
# plt.show()
#==============================================================================================

#Retrain model on entire dataset
model.fit(X_train,y_train)

# joblib.dump(model, "crop_stage_model.pkl")
joblib.dump(model, "backend/models/pkl/crop_stage_model.pkl")
print("Saved")









