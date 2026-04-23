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
        if len(group) != target_frames:
            continue
            
        label = gesture_name
        # On garde les 63 colonnes de coordonnées (x,y,z)
        features = group.drop(columns=["gesture", "sequence_id"]).values
        
        sequences.append(features)
        labels.append(label)
        
    return np.array(sequences), np.array(labels)


def augment_data(X_train, y_train, num_augments_per_seq=5):
    X_aug = []
    y_aug = []
    
    for X, y in zip(X_train, y_train):
        X_aug.append(X)
        y_aug.append(y)
        
        for _ in range(num_augments_per_seq):
            # Jittering léger sur les positions brutes
            noise = np.random.normal(0, 0.015, X.shape)
            jittered = X + noise
            
            # Décalage temporel
            shift = np.random.randint(-3, 4)
            shifted = np.roll(jittered, shift, axis=0)
            
            if shift > 0:
                shifted[:shift] = shifted[shift]
            elif shift < 0:
                shifted[shift:] = shifted[shift-1]
                
            X_aug.append(shifted)
            y_aug.append(y)
            
    return np.array(X_aug), np.array(y_aug)


def compute_fusion(X):
    """
    Prend un tenseur de dimensions (Nb_Séquences, 30_frames, 63_positions)
    Renvoie un tenseur de dimensions (Nb_Séquences, 30_frames, 126_features)
    """
    # Calcul des deltas sur l'axe du temps (axis=1)
    # prepend=X[:, 0:1, :] duplique la première frame pour garder une taille de 30
    deltas = np.diff(X, axis=1, prepend=X[:, 0:1, :])
    
    # Concaténation des positions et des deltas sur l'axe des features (axis=2)
    X_fusion = np.concatenate((X, deltas), axis=2)
    return X_fusion


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
    
    model.compile(optimizer='adam', 
                  loss='sparse_categorical_crossentropy', 
                  metrics=['accuracy'])
    return model


def train_dynamic_model(data_file="data/dynamic_gestures.csv",
                        model_out="gesture_model.keras",
                        labels_out="gesture_labels_dynamic.pkl"):

    print("Chargement des séquences...")
    X, y = load_sequence_data(data_file, target_frames=30)
    
    if len(X) == 0:
        print("Erreur: Aucune donnée trouvée ou format incorrect.")
        return

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    num_classes = len(label_encoder.classes_)
    
    print(f"Classes détectées ({num_classes}): {label_encoder.classes_}")

    X_train, X_temp, y_train, y_temp = train_test_split(X, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

    X_train_aug, y_train_aug = augment_data(X_train, y_train, num_augments_per_seq=9) 

    print("Calcul des deltas et fusion (Position + Vitesse)...")
    X_train_fusion = compute_fusion(X_train_aug)
    X_val_fusion = compute_fusion(X_val)
    X_test_fusion = compute_fusion(X_test)

    print(f"Format final des données d'entrée : {X_train_fusion.shape}")

    print("Construction du modèle 1D CNN...")
    model = build_1d_cnn(input_shape=(30, 126), num_classes=num_classes)

    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    print("Début de l'entraînement...")
    history = model.fit(
        X_train_fusion, y_train_aug,
        epochs=50,
        batch_size=16,
        validation_data=(X_val_fusion, y_val),
        callbacks=[early_stop],
        verbose=1
    )

    print("\n--- Évaluation du modèle sur le set de Test ---")
    loss, accuracy = model.evaluate(X_test_fusion, y_test, verbose=0)
    print(f"Accuracy (Test Set): {accuracy:.4f}")
    
    y_pred_probs = model.predict(X_test_fusion, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    model.save(model_out)
    joblib.dump(label_encoder, labels_out)

    print(f"Modèle sauvegardé sous {model_out}")
    print(f"Labels sauvegardés sous {labels_out}")

if __name__ == "__main__":
    import sys
    data_f = sys.argv[1] if len(sys.argv) > 1 else "data/dynamic_gestures.csv"
    train_dynamic_model(data_f)