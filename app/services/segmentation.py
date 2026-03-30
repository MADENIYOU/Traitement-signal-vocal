import os
import numpy as np
import librosa
import soundfile as sf

# Durée minimale d'un segment conservé (en ms) — filtre les parasites courts
MIN_SEGMENT_LEN_MS = 100

def segmenter_audio(chemin: str, top_db: float = 40.0, min_silence_len_ms: int = 300) -> list:
    """
    Découpe un fichier WAV en segments vocaux en ignorant les silences.
    """
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    # 1. Charger le signal (mono, fréquence native)
    signal, sr = librosa.load(chemin, sr=None, mono=True)

    if len(signal) == 0:
        return []

    # 2. Détecter les intervalles non-silencieux
    # hop_length=512 → résolution temporelle ~11ms à 44100Hz
    hop_length = 512
    intervalles = librosa.effects.split(
        signal,
        top_db=top_db,
        hop_length=hop_length
    )

    if len(intervalles) == 0:
        return []

    # 3. Fusionner les intervalles séparés par un silence trop court
    gap_min_samples = int((min_silence_len_ms / 1000.0) * sr)
    intervalles_fusionnes = _fusionner_intervalles(intervalles, gap_min_samples)

    # 4. Filtrer les segments trop courts (parasites)
    min_seg_samples = int((MIN_SEGMENT_LEN_MS / 1000.0) * sr)
    intervalles_filtres = [
        (d, f) for d, f in intervalles_fusionnes if (f - d) >= min_seg_samples
    ]

    if not intervalles_filtres:
        return []

    # 5. Créer le dossier de sortie par fichier source
    base_name = os.path.splitext(os.path.basename(chemin))[0]
    segments_root = os.path.join(os.getcwd(), 'segments')
    dossier_sortie = os.path.join(segments_root, base_name)
    
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie, exist_ok=True)
    else:
        _nettoyer_dossier(dossier_sortie)

    # 6. Exporter chaque segment
    resultats = []
    for i, (debut_s, fin_s) in enumerate(intervalles_filtres, start=1):
        segment = signal[debut_s:fin_s]
        nom = f'segment_{str(i).zfill(3)}.wav'
        chemin_sortie = os.path.join(dossier_sortie, nom)

        # Export forcé en PCM_16 pour compatibilité maximale
        sf.write(chemin_sortie, segment, sr, subtype='PCM_16')

        resultats.append({
            'id': i,
            'nom': nom,
            'duree': round((fin_s - debut_s) / sr, 3),
            'path': f'/segments/{base_name}/{nom}',
            'debut': round(debut_s / sr, 3),
            'fin': round(fin_s / sr, 3),
        })

    return resultats

def _fusionner_intervalles(intervalles: np.ndarray, gap_min_samples: int) -> list:
    """
    Fusionne les intervalles dont l'écart inter-segment est inférieur à gap_min_samples.
    """
    if len(intervalles) == 0:
        return []

    fusionnes = [list(intervalles[0])]

    for debut, fin in intervalles[1:]:
        ecart = debut - fusionnes[-1][1]
        if ecart < gap_min_samples:
            fusionnes[-1][1] = fin
        else:
            fusionnes.append([debut, fin])

    return [tuple(iv) for iv in fusionnes]

def _nettoyer_dossier(dossier: str):
    """
    Supprime les fichiers .wav existants dans un dossier.
    """
    if os.path.exists(dossier):
        for f in os.listdir(dossier):
            if f.endswith('.wav'):
                os.remove(os.path.join(dossier, f))
