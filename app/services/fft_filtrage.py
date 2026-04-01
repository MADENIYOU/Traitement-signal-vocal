import numpy as np
from scipy.fft import fft, ifft, fftfreq
import soundfile as sf
from pathlib import Path


def charger_signal(chemin_wav: str) -> tuple:
    """
    Charge un fichier WAV et retourne le signal et sa fréquence d'échantillonnage.

    Paramètres:
        chemin_wav (str): Chemin vers le fichier WAV.

    Retour:
        tuple: (signal numpy array float64, fréquence d'échantillonnage int)
    """
    signal, fe = sf.read(chemin_wav, dtype='float64')
    if signal.ndim > 1:
        signal = signal[:, 0]  # Prendre canal gauche si stéréo
    return signal, fe


def calculer_fft(signal: np.ndarray, fe: int) -> tuple:
    """
    Calcule la FFT d'un signal et retourne les fréquences et amplitudes.

    Paramètres:
        signal (np.ndarray): Signal temporel.
        fe (int): Fréquence d'échantillonnage en Hz.

    Retour:
        tuple: (freqs array, amplitudes array) — seulement la moitié positive du spectre.
    """
    N = len(signal)
    X = fft(signal)
    freqs = fftfreq(N, d=1.0 / fe)

    # Garder uniquement la moitié positive (spectre réel)
    moitie = N // 2
    freqs_pos = freqs[:moitie]
    amplitudes_pos = (2.0 / N) * np.abs(X[:moitie])

    return freqs_pos, amplitudes_pos


def appliquer_filtre(signal: np.ndarray, fe: int,
                     f_min: float, f_max: float,
                     type_filtre: str = "passe_bande") -> tuple:
    """
    Applique un filtre rectangulaire fréquentiel (passe-bande ou coupe-bande).
    Utilise uniquement un masque FFT — aucun filtre récursif.

    Paramètres:
        signal (np.ndarray): Signal temporel d'entrée.
        fe (int): Fréquence d'échantillonnage en Hz.
        f_min (float): Fréquence minimale du masque en Hz.
        f_max (float): Fréquence maximale du masque en Hz.
        type_filtre (str): "passe_bande" ou "coupe_bande".

    Retour:
        tuple: (signal_filtre np.ndarray, X_filtre spectre complexe, freqs array)
    """
    N = len(signal)
    X = fft(signal)
    freqs = fftfreq(N, d=1.0 / fe)

    # Construire le masque rectangulaire
    masque = np.zeros(N, dtype=bool)
    masque[(np.abs(freqs) >= f_min) & (np.abs(freqs) <= f_max)] = True

    if type_filtre == "passe_bande":
        X_filtre = X * masque
    elif type_filtre == "coupe_bande":
        X_filtre = X * (~masque)
    else:
        raise ValueError("type_filtre doit être 'passe_bande' ou 'coupe_bande'")

    signal_filtre = np.real(ifft(X_filtre))
    return signal_filtre, X_filtre, freqs


def sauvegarder_signal(signal: np.ndarray, fe: int,
                       chemin_sortie: str) -> str:
    """
    Sauvegarde un signal numpy en fichier WAV.

    Paramètres:
        signal (np.ndarray): Signal à sauvegarder.
        fe (int): Fréquence d'échantillonnage.
        chemin_sortie (str): Chemin complet du fichier de sortie.

    Retour:
        str: Chemin du fichier sauvegardé.
    """
    Path(chemin_sortie).parent.mkdir(parents=True, exist_ok=True)
    # Normaliser pour éviter la saturation
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * 0.9
    sf.write(chemin_sortie, signal, fe)
    return chemin_sortie


def preparer_donnees_graphique(signal_avant: np.ndarray,
                                signal_apres: np.ndarray,
                                fe: int) -> dict:
    """
    Prépare les données JSON pour l'affichage des graphiques frontend.

    Paramètres:
        signal_avant (np.ndarray): Signal original.
        signal_apres (np.ndarray): Signal filtré.
        fe (int): Fréquence d'échantillonnage.

    Retour:
        dict: Données formatées pour Chart.js/Plotly.
    """
    # Limiter à 2000 points pour ne pas surcharger le front
    pas = max(1, len(signal_avant) // 2000)

    temps = np.arange(len(signal_avant)) / fe
    freqs_av, amp_av = calculer_fft(signal_avant, fe)
    freqs_ap, amp_ap = calculer_fft(signal_apres, fe)

    pas_fft = max(1, len(freqs_av) // 2000)
    
    return {
        "temporel_avant": {
            "temps": temps[::pas].tolist(),
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