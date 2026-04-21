import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import joblib
import random

def jitter_motion_vector(vec, num_augments=50):
    augmented = []
    for j in range(num_augments):
        new_vec = []
        for i in range(0, len(vec), 2):
            magnitude = vec[i]
            angle = vec[i+1]
            mag_j = magnitude + random.gauss(0, 0.02)
            ang_j = angle + random.gauss(0, 0.05)
            new_vec.extend([mag_j, ang_j])
        augmented.append(new_vec)
    return augmented


def train_gesture_model(data_file="data/gesture_data_movement.csv",
                        model_out="gesture_model_movement_xgb.pkl",
                        labels_out="gesture_labels_movement.pkl"):

    df = pd.read_csv(data_file)

    y = df["gesture"]
    X = df.drop(columns=["gesture"]).values

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_temporary, y_train, y_temporary = train_test_split(
        X, y_encoded, test_size=0.3, random_state=42, shuffle=True
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temporary, y_temporary, test_size=0.5, random_state=42, shuffle=True
    )

    X_train_augmented = []
    y_train_augmented = []

    for vec, label in zip(X_train, y_train):
        X_train_augmented.append(vec)
        y_train_augmented.append(label)

        for aug in jitter_motion_vector(vec, num_augments=50):
            X_train_augmented.append(aug)
            y_train_augmented.append(label)

    X_train_augmented = np.array(X_train_augmented)
    y_train_augmented = np.array(y_train_augmented)


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

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=True
    )


    y_pred = model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n",
          classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    joblib.dump(model, model_out)
    joblib.dump(label_encoder, labels_out)

    print(f"Model saved as {model_out}")
    print(f"Labels saved as {labels_out}")


if __name__ == "__main__":
    import sys

    data_file = sys.argv[1] if len(sys.argv) > 1 else "data/gesture_data_mouvement.csv"
    model_out = sys.argv[2] if len(sys.argv) > 2 else "gesture_model_mouvement_xgb.pkl"
    labels_out = sys.argv[3] if len(sys.argv) > 3 else "gesture_labels_mouvement.pkl"

    train_gesture_model(data_file, model_out, labels_out)

