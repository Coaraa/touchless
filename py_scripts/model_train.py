import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import joblib

def preprocess_landmarks(X):
    X = X.reshape(-1, 21, 3)
    wrist = X[:, 0:1, :]
    X = X - wrist
    max_dist = np.max(np.linalg.norm(X, axis=2), axis=1).reshape(-1, 1, 1)
    X = X / max_dist

    return X.reshape(-1, 63)

df = pd.read_csv("data/gesture_data.csv")

y = df["gesture"]
X = df.drop(columns=["gesture"]).values

X = preprocess_landmarks(X)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, shuffle=True
)

model = XGBClassifier(
    n_estimators=400,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="multi:softmax",
    num_class=len(label_encoder.classes_),
    eval_metric="mlogloss",
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(
    y_test, y_pred, target_names=label_encoder.classes_
))

joblib.dump(model, "gesture_model_xgb.pkl")
joblib.dump(label_encoder, "gesture_labels.pkl")

print("\nModel saved as gesture_model_xgb.pkl")
print("Label encoder saved as gesture_labels.pkl")

