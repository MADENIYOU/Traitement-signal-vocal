import os
import io
import glob
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from datetime import datetime

def sauvegarder_audio(audio_file, locuteur, session, params):
    """
    Traite et sauvegarde un flux audio brut en fichier WAV conforme aux spécifications.

    Cette fonction effectue la conversion du format reçu (souvent WebM/Ogg via MediaRecorder)
    vers le format WAV PCM, tout en respectant l'arborescence de stockage demandée :
    database/locuteur_{ID}/session_{SESSION}/enreg_{INDEX}_{FREQ}_{BITS}.wav

    Args:
        audio_file (FileStorage): Objet fichier Flask contenant les données binaires de l'audio.
        locuteur (str): Identifiant unique du locuteur (ex: '01').
        session (str): Identifiant de la session d'enregistrement.
        params (dict): Dictionnaire contenant 'freq' (Hz) et 'bits' (16/32).

    Returns:
        str: Le chemin absolu du fichier sauvegardé sur le serveur.
    
    Raises:
        ValueError: Si les paramètres de fréquence ou de codage sont invalides.
    """
    # 1. Préparation des chemins de stockage
    # On se base sur le répertoire courant pour garantir la portabilité
    base_dir = os.path.join(os.getcwd(), 'database')
    locuteur_dir = os.path.join(base_dir, f'locuteur_{locuteur}')
    session_dir = os.path.join(locuteur_dir, f'session_{session}')
    
    # Création récursive des dossiers si nécessaire
    if not os.path.exists(session_dir):
        os.makedirs(session_dir, exist_ok=True)
        
    # 2. Génération du nom de fichier intelligent
    # On compte les fichiers existants pour incrémenter l'index de l'enregistrement
    existing_files = glob.glob(os.path.join(session_dir, "enreg_*.wav"))
    next_index = len(existing_files) + 1
    
    # Formatage de la fréquence pour le nom de fichier (ex: 44100 -> 44,1kHz)
    freq_val = float(params['freq'])
    freq_khz = freq_val / 1000
    # On remplace le point par la virgule pour les fréquences décimales comme 22,05kHz
    freq_str = f"{freq_khz:g}kHz".replace('.', ',')
    
    # Construction du nom final selon le pattern : enreg_XXX_YYkHz_ZZb.wav
    filename = f"enreg_{next_index:03d}_{freq_str}_{params['bits']}b.wav"
    filepath = os.path.join(session_dir, filename)

    # 3. Conversion et Traitement du signal
    # On utilise Pydub pour décoder le format source (souvent compressé par le navigateur)
    audio_data = audio_file.read()
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))

    # Normalisation : Forçage de la fréquence d'échantillonnage et passage en Mono
    target_freq = int(freq_val)
    audio_segment = audio_segment.set_frame_rate(target_freq).set_channels(1)

    # 4. Exportation via Soundfile (plus précis pour le contrôle du codage bits)
    # Conversion de l'objet Pydub en tableau Numpy normalisé entre -1.0 et 1.0
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    # Calcul de la valeur maximale possible selon la résolution binaire d'origine
    max_val = float(1 << (8 * audio_segment.sample_width - 1))
    samples /= max_val

    # Choix du sous-type PCM (16 bits ou 32 bits float) selon le choix utilisateur
    # Note : PCM_32 est souvent utilisé pour garder une précision maximale en TNS
    subtype = 'PCM_16' if params['bits'] == '16' else 'FLOAT'
    
    # Écriture finale sur le disque
    sf.write(filepath, samples, target_freq, subtype=subtype)
    
    return filepath
