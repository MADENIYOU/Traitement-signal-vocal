import os
import wave
from datetime import datetime

def sauvegarder_audio(audio_file, locuteur, session, params):
    """
    Sauvegarde le fichier audio reçu dans la structure de dossiers spécifiée.
    Format : database/locuteur_XX/session_YY/enreg_XXX_freq_bits.wav
    """
    base_dir = os.path.join(os.getcwd(), 'database')
    locuteur_dir = os.path.join(base_dir, f'locuteur_{locuteur}')
    session_dir = os.path.join(locuteur_dir, f'session_{session}')
    
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
        
    # Nom de fichier basé sur le timestamp et les paramètres pour unicité
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"enreg_{timestamp}_{params['freq']}Hz_{params['bits']}b.wav"
    filepath = os.path.join(session_dir, filename)
    
    audio_file.save(filepath)
    
    return filepath
