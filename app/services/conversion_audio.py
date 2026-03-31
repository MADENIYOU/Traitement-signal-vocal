import os
from pathlib import Path
from pydub import AudioSegment


def convertir_en_wav(chemin_source: str, dossier_sortie: str = "database/temp") -> str:
    """
    Convertit un fichier audio (MP3, OGG, FLAC, etc.) en WAV mono.

    Paramètres:
        chemin_source (str): Chemin vers le fichier audio source.
        dossier_sortie (str): Dossier où sauvegarder le fichier WAV converti.

    Retour:
        str: Chemin absolu du fichier WAV généré.
    """
    Path(dossier_sortie).mkdir(parents=True, exist_ok=True)

    nom_base = Path(chemin_source).stem
    chemin_sortie = os.path.join(dossier_sortie, f"{nom_base}_converti.wav")

    audio = AudioSegment.from_file(chemin_source)
    audio = audio.set_channels(1)  # Mono obligatoire pour le traitement signal
    audio.export(chemin_sortie, format="wav")

    return chemin_sortie