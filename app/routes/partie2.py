import os
import time
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from app.services.conversion_audio import convertir_en_wav
from app.services.fft_filtrage import (
    charger_signal,
    appliquer_filtre,
    sauvegarder_signal,
    preparer_donnees_graphique,
    calculer_fft
)

partie2_bp = Blueprint('partie2', __name__)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac'}

def extension_autorisee(filename: str) -> bool:
    """
    Vérifie si l'extension du fichier est autorisée.

    Paramètres:
        filename (str): Nom du fichier uploadé.

    Retour:
        bool: True si autorisée, False sinon.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@partie2_bp.route('/', methods=['GET'])
def index():
    """Route principale de la Partie 2 — affiche l'interface filtrage."""
    from flask import render_template
    return render_template('partie2.html')


@partie2_bp.route('/upload', methods=['POST'])
def upload_audio():
    """
    Reçoit un fichier audio, le convertit en WAV si nécessaire,
    calcule sa FFT et retourne les données pour visualisation.

    Retour:
        JSON: signal temporel, spectre FFT, durée, fréquence d'échantillonnage.
    """
    if 'fichier' not in request.files:
        return jsonify({"erreur": "Aucun fichier reçu"}), 400

    fichier = request.files['fichier']
    if fichier.filename == '' or not extension_autorisee(fichier.filename):
        return jsonify({"erreur": "Fichier invalide ou format non supporté"}), 400

    nom_secure = secure_filename(fichier.filename)
    upload_folder = current_app.config['UPLOAD_PARTIE2']
    chemin_upload = os.path.join(upload_folder, nom_secure)
    fichier.save(chemin_upload)

    # Conversion en WAV si nécessaire
    if not nom_secure.lower().endswith('.wav'):
        chemin_wav = convertir_en_wav(chemin_upload, upload_folder)
    else:
        chemin_wav = chemin_upload

    signal, fe = charger_signal(chemin_wav)
    freqs, amplitudes = calculer_fft(signal, fe)

    import numpy as np
    pas = max(1, len(signal) // 2000)
    temps = (np.arange(len(signal)) / fe).tolist()

    return jsonify({
        "succes": True,
        "fe": fe,
        "duree": round(len(signal) / fe, 2),
        "nb_echantillons": len(signal),
        "fichier_wav": os.path.basename(chemin_wav),  # Sécurité: uniquement nom fichier
        "temporel": {
            "temps": temps[::pas],
            "signal": signal[::pas].tolist()
        },
        "spectral": {
            "freqs": freqs[::max(1, len(freqs) // 2000)].tolist(),
            "amplitudes": amplitudes[::max(1, len(amplitudes) // 2000)].tolist()
        }
    })


@partie2_bp.route('/filtrer', methods=['POST'])
def filtrer_signal():
    """
    Applique un filtre rectangulaire (passe-bande ou coupe-bande) sur un fichier WAV.

    Body JSON attendu:
        fichier_wav (str): Chemin du fichier WAV déjà uploadé.
        f_min (float): Fréquence minimale du filtre en Hz.
        f_max (float): Fréquence maximale du filtre en Hz.
        type_filtre (str): "passe_bande" ou "coupe_bande".

    Retour:
        JSON: données graphiques avant/après + chemin fichier filtré.
    """
    data = request.get_json()
    upload_folder = current_app.config['UPLOAD_PARTIE2']
    chemin_wav = os.path.join(upload_folder, data.get('fichier_wav'))  # Reconstruction sécurisée du chemin
    f_min = float(data.get('f_min', 300))
    f_max = float(data.get('f_max', 3400))
    type_filtre = data.get('type_filtre', 'passe_bande')

    if not chemin_wav or not os.path.exists(chemin_wav):
        return jsonify({"erreur": "Fichier WAV introuvable"}), 404

    signal, fe = charger_signal(chemin_wav)

    if f_min >= f_max or f_max > fe / 2:
        return jsonify({"erreur": f"Fréquences invalides. f_max doit être < {fe//2} Hz"}), 400

    signal_filtre, _, _ = appliquer_filtre(signal, fe, f_min, f_max, type_filtre)

    nom_sortie = f"filtre_{int(time.time())}_{type_filtre}_{int(f_min)}_{int(f_max)}.wav"  # Nom unique avec timestamp
    filtered_folder = current_app.config['FILTERED_FOLDER']
    chemin_sortie = os.path.join(filtered_folder, nom_sortie)
    sauvegarder_signal(signal_filtre, fe, chemin_sortie)

    graphiques = preparer_donnees_graphique(signal, signal_filtre, fe)

    return jsonify({
        "succes": True,
        "fichier_filtre": os.path.basename(chemin_sortie),
        "f_min": f_min,
        "f_max": f_max,
        "type_filtre": type_filtre,
        "graphiques": graphiques
    })


@partie2_bp.route('/telecharger', methods=['GET'])
def telecharger_signal_filtre():
    """
    Permet de télécharger un signal filtré de manière sécurisée.

    Paramètres GET:
        fichier (str): Nom du fichier filtré à télécharger (uniquement le nom).

    Retour:
        Fichier WAV en téléchargement.
    """
    nom_fichier = request.args.get('fichier')
    
    if not nom_fichier:
        return jsonify({"erreur": "Nom fichier manquant"}), 400
    
    # Reconstruction sécurisée du chemin
    filtered_folder = current_app.config['FILTERED_FOLDER']
    chemin = os.path.join(filtered_folder, nom_fichier)
    
    if not os.path.exists(chemin):
        return jsonify({"erreur": f"Fichier introuvable: {nom_fichier}"}), 404
    
    return send_file(chemin, as_attachment=True)