# 🎙️ SignaVox – Traitement Numérique du Signal Vocal
### Mini-Projet TNS | ESP/UCAD | DIC 2 – Génie Informatique | 2025–2026

**SignaVox** est une application web interactive développée avec **Flask**, dédiée à l'acquisition, la segmentation et l'analyse fréquentielle de signaux sonores. Ce projet s'inscrit dans le cadre du module de Traitement Numérique du Signal (TNS) dirigé par le **Dr. Moustapha MBAYE**.

---

## 📖 Sommaire
1. [Aperçu du Projet](#-aperçu-du-projet)
2. [Structure du Dépôt](#-structure-du-dépôt)
3. [Installation & Lancement](#-installation--lancement)
4. [Partie 1 : Numérisation & Segmentation (TERMINÉE)](#-partie-1--numérisation--segmentation-terminée)
5. [Partie 2 : FFT & Filtrage (TERMINÉE)](#-partie-2--fft--filtrage-terminée)
6. [Contraintes Techniques & Standards](#-contraintes-techniques--standards)

---

## 🌟 Aperçu du Projet
L'application est divisée en deux modules complémentaires :
- **Module 1 :** Acquisition temps réel, configuration des paramètres de numérisation (Shannon) et segmentation automatique basée sur la détection d'activité vocale (VAD).
- **Module 2 :** Analyse spectrale via la Transformée de Fourier Rapide (FFT) et application de filtres fréquentiels rectangulaires (Passe-bande / Coupe-bande).

---

## 📁 Structure du Dépôt
```text
tns_projet_v2/
├── app/
│   ├── main.py                  # Point d'entrée Flask & Configuration
│   ├── routes/
│   │   ├── partie1.py           # API : Enregistrement et Segmentation
│   │   └── partie2.py           # API : FFT / Filtrage
│   ├── services/
│   │   ├── enregistrement.py    # Logique de gestion des fichiers WAV & Dossiers
│   │   ├── segmentation.py      # Algorithme de découpage (Librosa)
│   │   ├── fft_filtrage.py      # Logique de FFT, Masque, IFFT
│   │   └── conversion_audio.py  # Service de conversion audio (MP3/OGG -> WAV)
│   ├── templates/
│   │   ├── base.html            # Layout commun (SignaVox Branding)
│   │   ├── index.html           # Accueil animé
│   │   ├── partie1.html         # UI Numérisation (Terminée)
│   │   └── partie2.html         # UI Filtrage (Terminée)
│   └── static/
│       ├── css/style.css        # Design "Deep Tech" & Glassmorphism
│       └── js/
│           ├── partie1.js       # Chronomètre, VAD UI, Auto-scroll
│           └── partie2.js       # Logique frontend FFT/Filtrage (Graphiques Chart.js)
├── database/                    # Stockage structuré des enregistrements (.wav)
├── segments/                    # Sorties de la segmentation automatique
├── requirements.txt             # Dépendances Python
└── README.md                    # Documentation actuelle
```

---

## 🚀 Lancement rapide (Docker)

### Prérequis
- [Docker](https://www.docker.com/) installé
- [Docker Compose](https://docs.docker.com/compose/) installé

### Démarrer l'application

```bash
# Cloner le repo
git clone [<URL_DU_REPO>](https://github.com/MADENIYOU/Traitement-signal-vocal)
cd tns_projet

# Construire et lancer
docker-compose up --build
```

L'application est accessible sur **http://localhost:5000**

### Arrêter
```bash
docker-compose down
```


## 🚀 Installation Locale & Lancement Local

### Prérequis
- Python 3.10+
- FFmpeg (nécessaire pour la manipulation audio)

### Installation locale
1. **Cloner le projet**
2. **Créer un environnement virtuel :**
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate sur Windows
   ```
3. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```
4. **Lancer l'application :**
   ```bash
   cd app
   python main.py
   ```
   L'interface est accessible sur `http://localhost:5000`.

---

## ✅ Partie 1 : Numérisation & Segmentation (TERMINÉE)

Cette partie permet de capturer et d'organiser une base de données vocale.

### ⚙️ Paramètres de Numérisation
L'utilisateur peut configurer rigoureusement les paramètres avant l'acquisition :
- **Fréquences (Fe) :** 16 kHz, 22.05 kHz, 44.1 kHz.
- **Résolution (Codage) :** 16 bits ou 32 bits.
- **Durée :** Définie par l'utilisateur (avec arrêt automatique).

### 🗄️ Organisation de la Base de Données
Les fichiers sont sauvegardés selon une arborescence stricte imposée par le sujet :
`database/locuteur_{ID}/session_{DATE}/enreg_{TIME}_{Fe}_{Bits}.wav`

### ✂️ Segmentation Automatique
- **Algorithme :** Utilisation de `librosa.effects.split` pour détecter les silences.
- **Paramètres :** Seuil de top_db (dB) et durée minimale de silence (ms).
- **Interface :** Tableau dynamique des segments avec **fonctionnalité Play/Stop intégrée** et téléchargement individuel.

### ✨ Améliorations UI/UX (SignaVox Edition)
- **Chronomètre temps réel :** Affichage MM:SS directement sur le bouton d'enregistrement.
- **Auto-scroll :** Défilement fluide vers les résultats après le traitement.
- **Design :** Thème sombre, animations légères ("Chill Reveal") pour économiser le CPU.
- **Boutons d'action des segments :** Design moderne et interactif avec effets de survol/clic.

---

## ✅ Partie 2 : FFT & Filtrage (TERMINÉE)

Cette partie permet l'analyse fréquentielle et l'application de filtres sur des signaux audio.

### 1. Analyse Fréquentielle
- **Chargement :** Permettre l'upload de n'importe quel format (MP3, OGG) avec un **input de fichier stylisé et convivial**. Conversion automatique en **WAV**.
- **Visualisation :** Afficher le signal temporel $x(t)$ et son spectre d'amplitude $|X(f)|$ calculé par **FFT**.

### 2. Filtrage (Contrainte ABSOLUE)
Le filtrage est réalisé exclusivement par un **masque fréquentiel rectangulaire** :
- **Passe-bande :** Conserver les fréquences dans $[f_{min}, f_{max}]$.
- **Coupe-bande :** Supprimer les fréquences dans $[f_{min}, f_{max}]$.
- *Note : L'utilisation de filtres récursifs (Butterworth, etc.) est proscrite pour ce projet.*

### 3. Restitution
- Reconstruire le signal via la **Transformée de Fourier Inverse (IFFT)**.
- Afficher la comparaison spectrale **Avant / Après**.
- Permettre l'écoute et le téléchargement du signal filtré.

### ✨ Améliorations UI/UX (SignaVox Edition)
- **Input de fichier stylisé :** Conception améliorée pour une meilleure expérience utilisateur lors du choix de fichiers audio.
- **Graphiques interactifs :** Utilisation de Chart.js pour des visualisations claires et responsives du signal temporel et spectral.

---

## 📋 Contraintes Techniques & Standards

- **Code :** Chaque fonction doit impérativement comporter une **Docstring** (Description, Paramètres, Retour).
- **Bibliothèques recommandées :**
    - `numpy` : Manipulations matricielles du signal.
    - `scipy.fft` : Calcul de la FFT et IFFT.
    - `matplotlib` ou `plotly` : Visualisation des spectres.
    - `pydub` : Conversion de formats.
- **Validation :** Tester impérativement sur au moins deux locuteurs différents.

---

## 👥 Équipe & Crédits
- **Binôme 1 :** Mouhamadou Madeniyou SALL (Partie 1 & UI/UX)
- **Binôme 2 :** Khadimou Rassoul Mbacké MBAYE (Partie 2)
- **Enseignant :** Dr. Moustapha MBAYE
- **Institution :** ESP Dakar - DIC 2 (2025-2026)
