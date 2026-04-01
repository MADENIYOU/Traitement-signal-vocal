from flask import Blueprint, render_template, request, jsonify, current_app
import os
from app.services.enregistrement import sauvegarder_audio
from app.services.segmentation import segmenter_audio

# Initialisation du Blueprint pour le module de Numérisation & Segmentation
partie1_bp = Blueprint('partie1', __name__)

@partie1_bp.route('/')
def interface():
    """
    Sert la page principale de la Partie 1.
    
    Returns:
        Rendered HTML : Le template 'partie1.html' avec les contrôles d'enregistrement.
    """
    return render_template('partie1.html')

@partie1_bp.route('/sauvegarder', methods=['POST'])
def sauvegarder():
    """
    API : Reçoit, traite et enregistre le fichier audio sur le serveur.
    
    Attend une requête POST multipart/form-data contenant :
    - audio: Le blob binaire (file)
    - locuteur: L'ID du locuteur (string)
    - session: L'ID de session (string, optionnel)
    - frequence: Fréquence d'échantillonnage choisie (string)
    - codage: Résolution binaire (16/32)
    
    Returns:
        JSON: Le succès de l'opération et le chemin du fichier créé.
    """
    if 'audio' not in request.files:
        return jsonify({"error": "Aucun fichier audio reçu dans la requête"}), 400
    
    audio_file = request.files['audio']
    locuteur = request.form.get('locuteur', 'inconnu')
    # On peut étendre le système pour gérer plusieurs sessions dynamiques
    session = request.form.get('session', 'session_01')
    
    # Récupération des paramètres techniques pour le TNS
    freq = request.form.get('frequence')
    bits = request.form.get('codage')

    # Validation stricte selon les contraintes du sujet (Section 2.1)
    FREQS_AUTORISEES = ['16000', '22050', '44100']
    BITS_AUTORISES = ['16', '32']

    if freq not in FREQS_AUTORISEES or bits not in BITS_AUTORISES:
        return jsonify({
            "status": "error", 
            "message": f"Paramètres invalides. Valeurs autorisées : Fréquences {FREQS_AUTORISEES} Hz, Codage {BITS_AUTORISES} bits."
        }), 400

    params = {
        'freq': freq,
        'bits': bits
    }
    
    try:
        # Appel au service de bas niveau pour la gestion disque et conversion
        chemin_complet = sauvegarder_audio(audio_file, locuteur, session, params)
        
        return jsonify({
            "status": "success",
            "message": "Signal vocal enregistré et converti au format PCM",
            "path": chemin_complet
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@partie1_bp.route('/segmenter', methods=['POST'])
def segmenter():
    """
    API : Analyse un fichier existant pour le découper en segments.
    
    Attend un JSON contenant :
    - filepath: Le chemin serveur du fichier source
    - seuil: Le seuil dB (top_db) pour la détection
    - duree_min: Durée minimale de silence entre segments (ms)
    
    Returns:
        JSON: Liste des segments générés avec leurs métadonnées temporelles.
    """
    data = request.json
    filepath = data.get('filepath')
    
    # Conversion et validation des paramètres algorithmiques
    top_db = float(data.get('seuil', 20))
    min_silence_len_ms = int(data.get('duree_min', 500))
    
    if not filepath:
        return jsonify({"error": "Le chemin du fichier source est manquant"}), 400
    
    try:
        # Déclenchement de l'algorithme de segmentation (librosa)
        segments_detectes = segmenter_audio(
            filepath, 
            top_db=top_db, 
            min_silence_len_ms=min_silence_len_ms
        )
        
        return jsonify({
            "status": "success",
            "count": len(segments_detectes),
            "message": f"Segmentation terminée : {len(segments_detectes)} éléments utiles isolés.",
            "segments": segments_detectes
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Échec de l'analyse : {str(e)}"}), 500
