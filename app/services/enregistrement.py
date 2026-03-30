import os
import io
import glob
import numpy as np
import soundfile as sf
from pydub import AudioSegment

def sauvegarder_audio(audio_file, locuteur, session, params):
    """
    Reçoit un blob audio, le convertit en WAV PCM standard.
    Format de sortie : enreg_001_16kHz_16b.wav
    """
    base_dir = os.path.join(os.getcwd(), 'database')
    locuteur_dir = os.path.join(base_dir, f'locuteur_{locuteur}')
    session_dir = os.path.join(locuteur_dir, f'session_{session}')
    
    if not os.path.exists(session_dir):
        os.makedirs(session_dir, exist_ok=True)
        
    # Calcul du prochain index (ex: 001, 002...)
    files = glob.glob(os.path.join(session_dir, "enreg_*.wav"))
    next_index = len(files) + 1
    
    # Formatage de la fréquence (Hz -> kHz)
    freq_khz = float(params['freq']) / 1000
    freq_str = f"{freq_khz:g}kHz".replace('.', ',') # Utilise la virgule si décimal (22,05kHz)
    
    filename = f"enreg_{next_index:03d}_{freq_str}_{params['bits']}b.wav"
    filepath = os.path.join(session_dir, filename)

    # Lecture et conversion
    audio_data = audio_file.read()
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))

    target_freq = int(params['freq'])
    audio_segment = audio_segment.set_frame_rate(target_freq).set_channels(1)

    # Conversion en array numpy pour soundfile
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    max_val = float(1 << (8 * audio_segment.sample_width - 1))
    samples /= max_val

    # Écriture en WAV PCM
    subtype = 'PCM_16' if params['bits'] == '16' else 'PCM_32'
    sf.write(filepath, samples, target_freq, subtype=subtype)
    
    return filepath
