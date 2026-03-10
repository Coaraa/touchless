# Touchless

***Atelier pratique en IA***  
***Université du Québec à Chicoutimi (UQAC) - Hiver 2026***

## 📖 Description du projet

**Touchless** est un projet visant à offrir un contrôle gestuel sans contact des commandes générales d'un PC. 

L'idée répond à un problème du quotidien : vouloir interagir avec un écran (comme revenir en arrière sur une vidéo de recette) alors que l'on a les mains sales. Cette solution vise également le secteur B2B, par exemple pour des employés dans l'industrie qui utilisent des logiciels métiers où toucher un clavier est impossible.

## 🚀 Fonctionnalités

* **Gestes de base** : Reconnaissance des actions Grab, Screen, Move, Click, Swipe et Close.
* **Contrôle du système** : Déplacement de la souris et clic simple. La traduction des prédictions de gestes en actions clavier/souris se fait via Pyautogui.
* **Personnalisation** : L'utilisateur peut changer le geste ou l'association et un script détecte et enregistre le symbole de l'utilisateur.
* **Entraînement sur mesure** : L'utilisateur peut cliquer sur un bouton d'entraînement pour réentraîner le modèle avec ses propres données.

## 🛠️ Outils Technologiques

* **Langages** : Python et Rust.
* **Vision et IA** : OpenCV, Mediapipe, Scikit-learn et Pytorch.
* **Interopérabilité et Contrôle système** : PyO3 et PyAutoGui.

## 👥 L'équipe et Répartition des Tâches

- BOEHM Marin
- HABIÉ Yann
- MONARQUE Vincent
- SITHIDEJ Clara
- TOURAINE Florian
