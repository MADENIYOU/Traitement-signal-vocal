"""
=============================================================================
MODULE FFT_FILTRAGE - Traitement Numérique du Signal
=============================================================================

Ce module implémente les fonctions de traitement numérique pour la Partie 2 :
Analyse fréquentielle par FFT et filtrage fréquentiel par masque rectangulaire.

CONTRAINTE TECHNIQUE ABSOLUE (imposée par le sujet) :
----------------------------------------------------
Le filtrage DOIT être réalisé EXCLUSIVEMENT par un masque fréquentiel rectangulaire,
selon l'une des deux méthodes suivantes :
    • Passe-bande : conserve les fréquences dans [fmin, fmax]
    • Coupe-bande : supprime les fréquences dans [fmin, fmax]

Tout autre filtre (Butterworth, Hanning, Hamming, etc.) entraînerait un zéro.

Formulation mathématique du masque (sujet) :
    H(f) = { 1  si fmin ≤ |f| ≤ fmax   (passe-bande)
           { 0  sinon

    H̄(f) = 1 - H(f)  (coupe-bande)

Implémentation dans le domaine spectral :
    X = FFT(x)                          # Transformée de Fourier du signal
    masque = (|f| >= fmin) & (|f| <= fmax)
    X_filtre = X ⊙ masque               # Multiplication élément par élément (Hadamard)
    x_filtre = IFFT(X_filtre)           # Transformée de Fourier Inverse

Auteur      : Khadimou Rassoul Mbacké MBAYE
Encadrant   : Dr. Moustapha MBAYE
Institution : ESP/UCAD - DIC 2 (2025-2026)
Module      : Traitement Numérique du Signal
=============================================================================

Bibliothèques utilisées :
------------------------
- numpy (np)         : Calculs numériques, manipulations de tableaux
                       Documentation : https://numpy.org/doc/
- scipy.fft         : FFT et IFFT optimisées (algorithme Cooley-Tukey)
                       Documentation : https://docs.scipy.org/doc/scipy/reference/fft.html
- soundfile (sf)    : Lecture/écriture de fichiers audio WAV
                       Documentation : https://python-soundfile.readthedocs.io/
- pathlib (Path)    : Manipulation de chemins de fichiers (Python 3.4+)

=============================================================================
"""

import numpy as np
from scipy.fft import fft, ifft, fftfreq
import soundfile as sf
from pathlib import Path


def charger_signal(chemin_wav: str) -> tuple:
    """
    =============================================================================
    CHARGEMENT D'UN FICHIER AUDIO WAV
    =============================================================================
    
    Charge un fichier WAV et retourne le signal temporel ainsi que sa fréquence
    d'échantillonnage. Le signal est converti en mono si nécessaire.
    
    Paramètres
    ----------
    chemin_wav : str
        Chemin absolu ou relatif vers le fichier WAV à charger.
        Exemple : "database/uploads_partie2/audio.wav"
    
    Retour
    ------
    tuple : (signal, fe)
        - signal : np.ndarray de type float64, signal temporel échantillonné
        - fe : int, fréquence d'échantillonnage en Hz (ex: 44100)
    
    Implémentation
    --------------
    Utilise la bibliothèque soundfile qui s'appuie sur libsndfile (C),
    une bibliothèque robuste et rapide pour la lecture audio.
    
    Documentation soundfile.read :
    https://python-soundfile.readthedocs.io/en/latest/api.html#soundfile.read
    
    Exemple
    -------
    >>> signal, fe = charger_signal("audio.wav")
    >>> print(f"Durée: {len(signal)/fe:.2f}s, Fe: {fe}Hz")
    Durée: 3.45s, Fe: 44100Hz
    =============================================================================
    """
    # soundfile.read retourne (data, samplerate)
    # dtype='float64' garantit la précision pour les calculs FFT
    signal, fe = sf.read(chemin_wav, dtype='float64')
    
    # Vérification si le signal est stéréo (2 canaux)
    # Le traitement du signal nécessite un signal mono (1 canal)
    if signal.ndim > 1:
        # Sélection du canal gauche (indice 0) si stéréo
        # Alternative : np.mean(signal, axis=1) pour moyenne des canaux
        signal = signal[:, 0]
    
    return signal, fe


def calculer_fft(signal: np.ndarray, fe: int) -> tuple:
    """
    =============================================================================
    CALCUL DE LA TRANSFORMÉE DE FOURIER RAPIDE (FFT)
    =============================================================================
    
    Calcule la FFT d'un signal et retourne les fréquences et amplitudes spectrales.
    
    CONCEPT MATHÉMATIQUE - Transformée de Fourier Discrète (TFD) :
    -------------------------------------------------------------
    La TFD convertit un signal du domaine temporel au domaine fréquentiel :
    
        X[k] = Σ(n=0 à N-1) x[n] * e^(-j*2π*k*n/N)
    
    où :
        - N : nombre d'échantillons
        - x[n] : signal temporel (échantillon n)
        - X[k] : coefficient spectral à la fréquence k
        - j : unité imaginaire (√-1)
    
    La FFT (Fast Fourier Transform) est un algorithme rapide pour calculer la TFD
    avec une complexité O(N log N) au lieu de O(N²).
    
    Algorithme : Cooley-Tukey (décimation dans le temps)
    Référence  : J. W. Cooley and J. W. Tukey, "An algorithm for the 
                 machine calculation of complex Fourier series", 1965
    
    Paramètres
    ----------
    signal : np.ndarray
        Signal temporel d'entrée (1D, float64)
    fe : int
        Fréquence d'échantillonnage en Hz
    
    Retour
    ------
    tuple : (freqs, amplitudes)
        - freqs : np.ndarray, fréquences correspondantes en Hz (moitié positive)
        - amplitudes : np.ndarray, amplitudes |X(f)| (normalisées)
    
    Implémentation
    --------------
    1. Calcul de la FFT avec scipy.fft.fft
    2. Calcul des fréquences avec scipy.fft.fftfreq
    3. Conservation de la moitié positive du spectre (théorème de Nyquist)
    4. Normalisation des amplitudes par 2/N
    
    Bibliothèque utilisée :
    - scipy.fft.fft      : https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html
    - scipy.fft.fftfreq  : https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fftfreq.html
    
    Théorème de Nyquist-Shannon :
    Pour un signal échantillonné à fe, le spectre utile est limité à fe/2.
    On ne conserve donc que les fréquences positives [0, fe/2].
    
    Exemple
    -------
    >>> signal = np.sin(2 * np.pi * 440 * np.arange(0, 1, 1/44100))  # La4 à 440Hz
    >>> freqs, amps = calculer_fft(signal, 44100)
    >>> peak_idx = np.argmax(amps)
    >>> print(f"Pic de fréquence à {freqs[peak_idx]:.1f} Hz")
    Pic de fréquence à 440.0 Hz
    =============================================================================
    """
    # Nombre d'échantillons dans le signal
    N = len(signal)
    
    # Calcul de la FFT complexe
    # Retourne un tableau de N nombres complexes (partie réelle + imaginaire)
    X = fft(signal)
    
    # Calcul des fréquences correspondantes
    # fftfreq(N, d=1/fe) retourne les fréquences de -fe/2 à +fe/2
    # d = pas temporel = 1/fe (période d'échantillonnage)
    freqs = fftfreq(N, d=1.0 / fe)
    
    # Conservation de la moitié positive du spectre
    # Théorème de Nyquist : pour un signal réel, le spectre est symétrique
    # On garde seulement [0, fe/2] (fréquences positives)
    moitie = N // 2
    freqs_pos = freqs[:moitie]
    
    # Normalisation des amplitudes
    # La formule exacte dépend de la convention utilisée
    # Ici : |X[k]| * (2/N) pour les fréquences positives (sauf DC)
    # Cette normalisation préserve l'énergie du signal
    amplitudes_pos = (2.0 / N) * np.abs(X[:moitie])
    
    return freqs_pos, amplitudes_pos


def appliquer_filtre(signal: np.ndarray, fe: int,
                     f_min: float, f_max: float,
                     type_filtre: str = "passe_bande") -> tuple:
    """
    =============================================================================
    APPLICATION DU FILTRE FRÉQUENTIEL PAR MASQUE RECTANGULAIRE
    =============================================================================
    
    CŒUR DU SYSTÈME - Cette fonction implémente la contrainte absolue du sujet :
    le filtrage EXCLUSIVEMENT par masque fréquentiel rectangulaire.
    
    CONCEPT MATHÉMATIQUE - Filtrage dans le domaine spectral :
    ---------------------------------------------------------
    La multiplication dans le domaine spectral équivaut à la convolution dans le
    domaine temporel (propriété fondamentale de la Transformée de Fourier) :
    
        x(t) * h(t)  ⟷  X(f) · H(f)
    
    où * est la convolution et · est la multiplication.
    
    Pour filtrer efficacement, on travaille directement dans le domaine spectral :
    1. Calculer la FFT du signal : X = FFT(x)
    2. Construire le masque H(f) selon les fréquences de coupure
    3. Multiplier : X_filtre = X ⊙ H   (⊙ = produit d'Hadamard, élément par élément)
    4. Reconstruire par IFFT : x_filtre = IFFT(X_filtre)
    
    Masque rectangulaire (conforme au sujet) :
    ------------------------------------------
    Passe-bande (conserve [fmin, fmax]) :
        H(f) = { 1  si fmin ≤ |f| ≤ fmax
               { 0  sinon
    
    Coupe-bande (supprime [fmin, fmax]) :
        H̄(f) = { 0  si fmin ≤ |f| ≤ fmax
               { 1  sinon
             = 1 - H(f)
    
    Pourquoi |f| (valeur absolue) ?
    La FFT retourne un spectre bilatéral avec fréquences positives ET négatives.
    Le masque doit s'appliquer symétriquement autour de 0 Hz.
    
    Paramètres
    ----------
    signal : np.ndarray
        Signal temporel d'entrée x(t)
    fe : int
        Fréquence d'échantillonnage en Hz
    f_min : float
        Fréquence minimale du masque en Hz (borne inférieure)
    f_max : float
        Fréquence maximale du masque en Hz (borne supérieure)
        Contrainte : f_max < fe/2 (théorème de Shannon)
    type_filtre : str, optionnel
        Type de filtre à appliquer :
        - "passe_bande" : conserve les fréquences dans [f_min, f_max]
        - "coupe_bande" : supprime les fréquences dans [f_min, f_max]
        Défaut : "passe_bande"
    
    Retour
    ------
    tuple : (signal_filtre, X_filtre, freqs)
        - signal_filtre : np.ndarray, signal filtré x'(t) (domaine temporel)
        - X_filtre : np.ndarray complexe, spectre filtré X'(f) (domaine fréquentiel)
        - freqs : np.ndarray, tableau des fréquences en Hz
    
    Implémentation détaillée :
    -------------------------
    1. Calcul de la FFT du signal complet (N points)
    2. Calcul des fréquences correspondantes avec fftfreq
    3. Construction du masque booléen avec conditions sur |f|
    4. Application du masque (passe-bande ou coupe-bande)
    5. Reconstruction par IFFT
    6. Extraction de la partie réelle (la partie imaginaire est ~0)
    
    AVERTISSEMENT IMPORTANT :
    ------------------------
    Cette implémentation utilise un masque rectangulaire PUR. Cela introduit
    des effets de Gibbs (oscillations) dans le domaine temporel dues à la
    discontinuité brutale du masque. C'est une limitation connue acceptée
    car la contrainte du sujet interdit tout lissage (filtres Butterworth, etc.).
    
    Référence sur les effets de Gibbs :
    https://en.wikipedia.org/wiki/Gibbs_phenomenon
    
    Raises
    ------
    ValueError
        Si type_filtre n'est pas "passe_bande" ou "coupe_bande"
    
    Exemple
    -------
    >>> signal = np.random.randn(44100)  # Bruit blanc
    >>> signal_filtre, X_filtre, freqs = appliquer_filtre(
    ...     signal, 44100, 300, 3400, "passe_bande"
    ... )
    >>> # Le signal filtré ne contient que les fréquences entre 300 et 3400 Hz
    =============================================================================
    """
    # Nombre d'échantillons
    N = len(signal)
    
    # ÉTAPE 1 : Transformée de Fourier du signal
    # X contient N nombres complexes (parties réelles et imaginaires)
    X = fft(signal)
    
    # ÉTAPE 2 : Calcul des fréquences correspondantes
    # freqs est un tableau de N valeurs allant de -fe/2 à +fe/2
    freqs = fftfreq(N, d=1.0 / fe)
    
    # ÉTAPE 3 : Construction du masque rectangulaire
    # Initialisation d'un masque de False (tout à 0)
    masque = np.zeros(N, dtype=bool)
    
    # Application de la condition : fmin ≤ |f| ≤ fmax
    # np.abs(freqs) prend la valeur absolue (fréquences positives et négatives)
    # L'opérateur & est le ET logique (ET bit à bit pour les booléens)
    masque[(np.abs(freqs) >= f_min) & (np.abs(freqs) <= f_max)] = True
    
    # ÉTAPE 4 : Application du masque selon le type de filtre
    if type_filtre == "passe_bande":
        # Passe-bande : on conserve les fréquences DANS la bande
        # X_filtre[k] = X[k] * 1 si dans la bande, 0 sinon
        X_filtre = X * masque
        
    elif type_filtre == "coupe_bande":
        # Coupe-bande : on supprime les fréquences DANS la bande
        # ~masque inverse le masque (True devient False et vice versa)
        # X_filtre[k] = X[k] * 0 si dans la bande, 1 sinon
        X_filtre = X * (~masque)
        
    else:
        # Vérification de validité du paramètre
        raise ValueError("type_filtre doit être 'passe_bande' ou 'coupe_bande'")
    
    # ÉTAPE 5 : Reconstruction temporelle par IFFT
    # ifft retourne un signal complexe, on prend la partie réelle
    # La partie imaginaire devrait être quasi-nulle (erreurs numériques)
    signal_filtre = np.real(ifft(X_filtre))
    
    return signal_filtre, X_filtre, freqs


def sauvegarder_signal(signal: np.ndarray, fe: int,
                       chemin_sortie: str) -> str:
    """
    =============================================================================
    SAUVEGARDE DU SIGNAL FILTRÉ EN FICHIER WAV
    =============================================================================
    
    Sauvegarde un signal numpy en fichier WAV standardisé.
    
    Paramètres
    ----------
    signal : np.ndarray
        Signal à sauvegarder (1D, valeurs flottantes)
    fe : int
        Fréquence d'échantillonnage en Hz
    chemin_sortie : str
        Chemin complet du fichier de sortie (ex: "database/filtres/audio_filtre.wav")
    
    Retour
    ------
    str : Chemin absolu du fichier sauvegardé
    
    Pré-traitement
    --------------
    Avant sauvegarde, le signal est normalisé à 90% du maximum pour éviter
    l'écrêtage (clipping) qui introduirait des distorsions.
    
    Normalisation :
        signal_norm = (signal / max|signal|) * 0.9
    
    Cela garantit que l'amplitude maximale reste sous 1.0 (pleine échelle).
    
    Implémentation
    --------------
    Utilise soundfile.write qui encode en PCM 16-bit par défaut,
    compatible avec tous les lecteurs audio.
    
    Documentation :
    https://python-soundfile.readthedocs.io/en/latest/api.html#soundfile.write
    
    Exemple
    -------
    >>> signal_filtre, _, _ = appliquer_filtre(signal, 44100, 300, 3400)
    >>> chemin = sauvegarder_signal(signal_filtre, 44100, "sortie.wav")
    >>> print(f"Fichier sauvegardé : {chemin}")
    =============================================================================
    """
    # Création du dossier parent si inexistant
    # Path.mkdir avec parents=True crée tous les dossiers intermédiaires
    Path(chemin_sortie).parent.mkdir(parents=True, exist_ok=True)
    
    # Normalisation pour éviter la saturation/clipping
    # np.abs(signal) retourne les valeurs absolues
    # np.max trouve la valeur maximale
    max_val = np.max(np.abs(signal))
    
    if max_val > 0:
        # Normalisation à 0.9 (90%) pour marge de sécurité
        signal = signal / max_val * 0.9
    
    # Écriture du fichier WAV
    # Format PCM 16-bit par défaut (optimal pour la qualité/fichier)
    sf.write(chemin_sortie, signal, fe)
    
    return chemin_sortie


def preparer_donnees_graphique(signal_avant: np.ndarray,
                                signal_apres: np.ndarray,
                                fe: int) -> dict:
    """
    =============================================================================
    PRÉPARATION DES DONNÉES POUR L'AFFICHAGE GRAPHIQUE (FRONTEND)
    =============================================================================
    
    Cette fonction prépare les données JSON pour l'affichage côté frontend
    avec Chart.js. Elle calcule les représentations temporelles et spectrales
    AVANT et APRÈS filtrage pour permettre la comparaison visuelle.
    
    Paramètres
    ----------
    signal_avant : np.ndarray
        Signal ORIGINAL x(t) avant filtrage
    signal_apres : np.ndarray
        Signal FILTRÉ x'(t) après filtrage
    fe : int
        Fréquence d'échantillonnage en Hz
    
    Retour
    ------
    dict : Structure JSON avec les données pour les 4 graphiques :
        {
            "temporel_avant": { "temps": [...], "signal": [...] },
            "temporel_apres": { "temps": [...], "signal": [...] },
            "spectral_avant": { "freqs": [...], "amplitudes": [...] },
            "spectral_apres": { "freqs": [...], "amplitudes": [...] }
        }
    
    Optimisation pour le Frontend
    -----------------------------
    Pour éviter de surcharger le navigateur avec trop de points de données,
    un sous-échantillonnage est appliqué :
        - Maximum 2000 points par graphique
        - Maintien de la forme globale du signal
    
    Cette limite est arbitraire mais suffisante pour la visualisation.
    Chart.js a des performances dégradées au-delà de ~5000 points.
    
    Exemple
    -------
    >>> signal_filtre, _, _ = appliquer_filtre(signal, 44100, 300, 3400)
    >>> graphiques = preparer_donnees_graphique(signal, signal_filtre, 44100)
    >>> return jsonify({"graphiques": graphiques})
    =============================================================================
    """
    # Sous-échantillonnage pour alléger le frontend
    # Si le signal a 441000 échantillons (10s à 44.1kHz), pas = 220
    # On garde donc 1 point sur 220 → ~2000 points finaux
    pas = max(1, len(signal_avant) // 2000)
    
    # Vecteur temps pour l'axe X (temporel)
    # temps[n] = n / fe (instant de l'échantillon n)
    temps = np.arange(len(signal_avant)) / fe
    
    # Calcul des FFT avant et après filtrage
    # Cela permet de visualiser l'effet du masque sur le spectre
    freqs_av, amp_av = calculer_fft(signal_avant, fe)
    freqs_ap, amp_ap = calculer_fft(signal_apres, fe)
    
    # Sous-échantillonnage des données spectrales (même logique)
    pas_fft = max(1, len(freqs_av) // 2000)
    
    # Construction du dictionnaire JSON
    # Les données sont converties en listes Python standard (.tolist())
    # pour une sérialisation JSON correcte par Flask
    return {
        "temporel_avant": {
            "temps": temps[::pas].tolist(),      # [::pas] = échantillonnage tous les 'pas'
            "signal": signal_avant[::pas].tolist()
        },
        "temporel_apres": {
            "temps": temps[::pas].tolist(),
            "signal": signal_apres[::pas].tolist()
        },
        "spectral_avant": {
            "freqs": freqs_av[::pas_fft].tolist(),
            "amplitudes": amp_av[::pas_fft].tolist()
        },
        "spectral_apres": {
            "freqs": freqs_ap[::pas_fft].tolist(),
            "amplitudes": amp_ap[::pas_fft].tolist()
        }
    }
