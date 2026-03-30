import os
import numpy as np
import librosa
import soundfile as sf

# Durée minimale d'un segment conservé (en ms) pour filtrer les parasites et bruits impulsionnels
MIN_SEGMENT_LEN_MS = 100

def segmenter_audio(chemin: str, top_db: float = 40.0, min_silence_len_ms: int = 300) -> list:
    """
    Algorithme de détection d'activité vocale (VAD) et de segmentation automatique.

    Cette fonction analyse un signal audio, identifie les zones de silence selon un seuil d'amplitude,
    et découpe l'audio en segments UTILES. Elle fusionne les silences trop courts pour éviter
    un découpage excessif au milieu d'un même mot.

    Args:
        chemin (str): Chemin absolu du fichier WAV source à segmenter.
        top_db (float): Seuil en décibels sous la crête pour la détection du silence (défaut: 40.0).
                        Une valeur plus élevée rend le détecteur plus sensible.
        min_silence_len_ms (int): Durée minimale de silence (ms) requise pour séparer deux segments.

    Returns:
        list: Une liste de dictionnaires, chacun contenant les métadonnées d'un segment (id, nom, duree, chemin).
    
    Raises:
        FileNotFoundError: Si le fichier audio spécifié n'existe pas.
    """
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Fichier introuvable sur le serveur : {chemin}")

    # 1. Chargement du signal
    # sr=None permet de garder la fréquence d'échantillonnage native du fichier d'origine
    signal, sr = librosa.load(chemin, sr=None, mono=True)

    if len(signal) == 0:
        return []

    # 2. Détection des intervalles de "parole"
    # L'algorithme se base sur l'énergie du signal (RMS)
    # hop_length définit la fenêtre temporelle de l'analyse (par défaut 512 échantillons)
    hop_length = 512
    intervalles = librosa.effects.split(
        signal,
        top_db=top_db,
        hop_length=hop_length
    )

    if len(intervalles) == 0:
        return []

    # 3. Fusion des intervalles proches (Post-processing)
    # Si deux segments sont séparés par un silence plus court que min_silence_len_ms,
    # on les considère comme faisant partie du même ensemble sémantique.
    gap_min_samples = int((min_silence_len_ms / 1000.0) * sr)
    intervalles_fusionnes = _fusionner_intervalles(intervalles, gap_min_samples)

    # 4. Filtrage des segments trop courts
    # On élimine les "segments" qui sont trop brefs pour être de la parole (parasites de commutation, etc.)
    min_seg_samples = int((MIN_SEGMENT_LEN_MS / 1000.0) * sr)
    intervalles_filtres = [
        (debut, fin) for debut, fin in intervalles_fusionnes if (fin - debut) >= min_seg_samples
    ]

    if not intervalles_filtres:
        return []

    # 5. Gestion des dossiers de sortie
    # On crée un sous-dossier spécifique à chaque fichier source pour éviter les collisions
    base_name = os.path.splitext(os.path.basename(chemin))[0]
    segments_root = os.path.join(os.getcwd(), 'segments')
    dossier_sortie = os.path.join(segments_root, base_name)
    
    # Nettoyage automatique avant nouvelle segmentation
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie, exist_ok=True)
    else:
        _nettoyer_dossier(dossier_sortie)

    # 6. Extraction et Exportation des segments physiques
    resultats = []
    for i, (idx_debut, idx_fin) in enumerate(intervalles_filtres, start=1):
        segment_audio = signal[idx_debut:idx_fin]
        nom_segment = f'segment_{str(i).zfill(3)}.wav'
        chemin_complet_sortie = os.path.join(dossier_sortie, nom_segment)

        # Export en PCM_16 par défaut pour les segments (standard universel)
        sf.write(chemin_complet_sortie, segment_audio, sr, subtype='PCM_16')

        # Construction des métadonnées pour le Frontend
        resultats.append({
            'id': i,
            'nom': nom_segment,
            'duree': round((idx_fin - idx_debut) / sr, 3), # Durée précise en secondes
            'path': f'/segments/{base_name}/{nom_segment}', # Route servie par Flask
            'debut_idx': int(idx_debut),
            'fin_idx': int(idx_fin)
        })

    return resultats

def _fusionner_intervalles(intervalles: np.ndarray, gap_min_samples: int) -> list:
    """
    Fonction utilitaire pour fusionner les segments trop proches.
    
    Args:
        intervalles: Tableau numpy des bornes (debut, fin) initiales.
        gap_min_samples: Nombre d'échantillons minimum pour considérer un silence réel.
        
    Returns:
        list: Liste d'intervalles consolidés.
    """
    if len(intervalles) == 0:
        return []

    fusionnes = [list(intervalles[0])]

    for debut, fin in intervalles[1:]:
        # Calcul de l'écart avec le segment précédent
        ecart = debut - fusionnes[-1][1]
        
        if ecart < gap_min_samples:
            # On prolonge la fin du dernier segment au lieu d'en créer un nouveau
            fusionnes[-1][1] = fin
        else:
            # Le silence est suffisant, on démarre un nouveau segment
            fusionnes.append([debut, fin])

    return [tuple(iv) for iv in fusionnes]

def _nettoyer_dossier(dossier: str):
    """
    Supprime tous les fichiers WAV d'un répertoire pour préparer une nouvelle segmentation.
    """
    if os.path.exists(dossier):
        for f in os.listdir(dossier):
            if f.endswith('.wav'):
                os.remove(os.path.join(dossier, f))
