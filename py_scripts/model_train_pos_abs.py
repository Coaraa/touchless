import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout, BatchNormalization

def load_sequence_data(data_file="data/dynamic_gestures.csv", target_frames=30):
    df = pd.read_csv(data_file)
    sequences = []
    labels = []
    for (gesture_name, seq_id), group in df.groupby(["gesture", "sequence_id"]):
        if len(group) != target_frames: continue
        label = gesture_name
        features = group.drop(columns=["gesture", "sequence_id"]).values
        sequences.append(features)
        labels.append(label)
    return np.array(sequences), np.array(labels)

# NOUVEAU : Normalisation Séquentielle
def sequential_normalization(X):
    X_norm = np.zeros_like(X)
    for i in range(X.shape[0]): # Pour chaque séquence
        # On prend la position x, y, z du poignet à la frame 0
        wrist_t0 = X[i, 0, 0:3] 
        # On la duplique 21 fois pour l'aligner avec les 63 caractéristiques (21 points * 3)
        wrist_t0_tiled = np.tile(wrist_t0, 21)
        # On soustrait cette position de départ à TOUTES les frames de la séquence
        X_norm[i] = X[i] - wrist_t0_tiled
    return X_norm

def augment_data(X_train, y_train, num_augments_per_seq=5):
    X_aug = []
    y_aug = []
    for X, y in zip(X_train, y_train):
        X_aug.append(X)
        y_aug.append(y)
        for _ in range(num_augments_per_seq):
            noise = np.random.normal(0, 0.015, X.shape)
            jittered = X + noise
            shift = np.random.randint(-3, 4)
            shifted = np.roll(jittered, shift, axis=0)
            if shift > 0: shifted[:shift] = shifted[shift]
            elif shift < 0: shifted[shift:] = shifted[shift-1]
            X_aug.append(shifted)
            y_aug.append(y)
    return np.array(X_aug), np.array(y_aug)

def compute_fusion(X):
    deltas = np.diff(X, axis=1, prepend=X[:, 0:1, :])
    return np.concatenate((X, deltas), axis=2)

def build_1d_cnn(input_shape, num_classes):
    model = Sequential([
        Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=input_shape),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),
        Conv1D(filters=128, kernel_size=3, activation='relu'),
        BatchNormalization(),
        MaxPooling1D(pool_size=2),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def train_dynamic_model(data_file="data/dynamic_gestures.csv", model_out="gesture_model_1dcnn.keras", labels_out="gesture_labels_dynamic.pkl"):
    print("Chargement des séquences...")
    X_raw, y = load_sequence_data(data_file, target_frames=30)
    
    if len(X_raw) == 0: return

    # Application de la normalisation séquentielle sur les données brutes
    X = sequential_normalization(X_raw)

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    num_classes = len(label_encoder.classes_)
    print(f"Classes détectées : {label_encoder.classes_}")

    X_train, X_temp, y_train, y_temp = train_test_split(X, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

    X_train_aug, y_train_aug = augment_data(X_train, y_train, num_augments_per_seq=9) 

    X_train_fusion = compute_fusion(X_train_aug)
    X_val_fusion = compute_fusion(X_val)
    X_test_fusion = compute_fusion(X_test)

    print("Entraînement du CNN...")
    model = build_1d_cnn(input_shape=(30, 126), num_classes=num_classes)
    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    model.fit(X_train_fusion, y_train_aug, epochs=50, batch_size=16, validation_data=(X_val_fusion, y_val), callbacks=[early_stop], verbose=1)

    loss, accuracy = model.evaluate(X_test_fusion, y_test, verbose=0)
    print(f"Accuracy (Test Set): {accuracy:.4f}")
    
    model.save(model_out)
    joblib.dump(label_encoder, labels_out)
    print("Modèle sauvegardé.")

if __name__ == "__main__":
    import sys
    data_f = sys.argv[1] if len(sys.argv) > 1 else "data/dynamic_gestures.csv"
    train_dynamic_model(data_f)