/**
 * Logiciel de Numérisation & Segmentation de Signal Vocal (Partie 1)
 * SignaVox Edition - 2026
 */

let mediaRecorder;      // Instance pour la capture audio
let audioChunks = [];    // Buffer pour les données capturées
let audioBlob;          // Blob final de l'enregistrement
let lastSavedFilePath = ""; // Chemin serveur du dernier fichier enregistré
let timerInterval;      // ID de l'intervalle pour le chronomètre
let startTime;          // Timestamp du début de l'enregistrement

// Variables globales pour gérer la lecture des segments
let currentPlayingAudio = null; // Stocke l'objet Audio en cours de lecture
let currentPlayingButton = null; // Stocke le bouton Play/Stop du segment en cours


// Récupération des éléments DOM
const btnRecord = document.getElementById('btnRecord');
const btnStop = document.getElementById('btnStop');
const btnSave = document.getElementById('btnSave');
const btnSegment = document.getElementById('btnSegment');
const status = document.getElementById('status');
const audioPlayback = document.getElementById('audioPlayback');

/**
 * Met à jour dynamiquement l'affichage du temps sur le bouton Record
 */
function updateTimer() {
    const now = Date.now();
    const diff = now - startTime;
    const seconds = Math.floor((diff / 1000) % 60);
    const minutes = Math.floor((diff / (1000 * 60)) % 60);
    const timeStr = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // On cible le span à l'intérieur du bouton pour ne pas écraser l'icône
    const span = btnRecord.querySelector('span');
    if (span) span.innerText = timeStr;
}

/**
 * Lance la capture du flux audio via l'API Web MediaDevices
 */
btnRecord.onclick = async () => {
    try {
        // Demande d'accès au microphone
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Initialisation du recorder (le navigateur choisit souvent WebM/Ogg comme conteneur)
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        // Événement déclenché à chaque paquet de données reçu
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        // Événement déclenché à l'arrêt du recorder
        mediaRecorder.onstop = () => {
            // Création du blob audio final
            audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            
            // Mise à jour de l'aperçu audio HTML5
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;
            audioPlayback.style.display = 'block';
            btnSave.disabled = false;
            
            // Réinitialisation de l'état du bouton
            const span = btnRecord.querySelector('span');
            if (span) span.innerText = "Enregistrer";
            btnRecord.classList.remove('active', 'pulse-red');
            clearInterval(timerInterval);
        };

        // Récupération de la durée limite de sécurité
        const dureeSec = parseFloat(document.getElementById('duree').value) || 5;
        
        // Déclenchement de l'acquisition
        mediaRecorder.start();
        
        // Initialisation du chronomètre visuel
        startTime = Date.now();
        timerInterval = setInterval(updateTimer, 500);

        // Mise à jour de l'UI vers l'état "Recording"
        btnRecord.disabled = true;
        btnRecord.classList.add('active', 'pulse-red');
        btnStop.disabled = false;
        
        status.innerHTML = '<i class="fas fa-microphone-alt animate__animated animate__flash animate__infinite"></i> Signal en cours d\'acquisition...';
        status.style.color = "var(--danger)";

        // Sécurité : Arrêt automatique si l'utilisateur dépasse la durée max
        setTimeout(() => {
            if (mediaRecorder && mediaRecorder.state === "recording") {
                btnStop.click();
            }
        }, dureeSec * 1000);

    } catch (err) {
        alert("Erreur d'accès au micro : " + err);
        status.innerText = "Accès micro refusé ou indisponible.";
    }
};

/**
 * Arrête proprement l'enregistrement en cours
 */
btnStop.onclick = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        btnRecord.disabled = false;
        btnStop.disabled = true;
        status.innerHTML = '<i class="fas fa-check-circle"></i> Signal capturé. Prêt pour la sauvegarde.';
        status.style.color = "var(--success)";
        
        // Arrêt des pistes média pour libérer le micro (icône caméra/micro rouge disparait)
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
};

/**
 * Envoie le blob audio et les métadonnées au serveur Flask
 */
btnSave.onclick = async () => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'temp_recording.wav');
    formData.append('locuteur', document.getElementById('locuteur').value);
    formData.append('frequence', document.getElementById('frequence').value);
    formData.append('codage', document.querySelector('select[name="codage"]').value);

    status.innerHTML = '<i class="fas fa-sync fa-spin"></i> Transmission des données...';
    
    try {
        const response = await fetch('/partie1/sauvegarder', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (result.path) {
            lastSavedFilePath = result.path;
            status.innerHTML = '<i class="fas fa-file-audio"></i> Signal sauvegardé avec succès sur le serveur.';
            btnSegment.disabled = false;
            btnSegment.classList.add('animate__animated', 'animate__pulse');
            document.getElementById('segmentStatus').innerText = "Veuillez lancer la segmentation automatique.";
        }
    } catch (err) {
        status.innerText = "Erreur lors de la communication serveur.";
    }
};

/**
 * Appelle l'API de segmentation et gère l'affichage des résultats
 */
btnSegment.onclick = async () => {
    const data = {
        filepath: lastSavedFilePath,
        seuil: document.getElementById('seuil').value,
        duree_min: document.getElementById('duree_min').value
    };

    const segStatus = document.getElementById('segmentStatus');
    segStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Traitement algorithmique en cours...';

    try {
        const response = await fetch('/partie1/segmenter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        // Affichage dynamique des résultats
        displaySegments(result.segments);
        segStatus.innerText = result.message;
        
        // UX : Défilement fluide vers la section des résultats pour attirer l'attention de l'utilisateur
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (err) {
        segStatus.innerText = "Erreur lors de l'exécution de l'algorithme.";
    }
};

/**
 * Génère le tableau HTML dynamiquement à partir des segments détectés
 * @param {Array} segments - Liste des segments envoyée par le serveur
 */
function displaySegments(segments) {
    const body = document.getElementById('segmentsBody');
    const countSpan = document.getElementById('segmentCount');
    
    body.innerHTML = "";
    countSpan.innerText = `${segments.length} segment(s) utile(s)`;
    
    segments.forEach((seg, index) => {
        // Utilisation des template literals pour une meilleure lisibilité du HTML dynamique
        const row = `
            <tr class="reveal-chill" style="animation-delay: ${index * 0.05}s">
                <td style="font-weight: 600; color: var(--accent-cyan);">#${seg.id.toString().padStart(3, '0')}</td>
                <td>${seg.nom}</td>
                <td><span class="badge-mono">${seg.duree.toFixed(3)}s</span></td>
                <td style="text-align: right;">
                    <div class="action-cell-buttons">
                        <button onclick="playSegment('${seg.path}', this)" class="btn-icon play-pause-btn" title="Écouter / Arrêter">
                            <i class="fas fa-play"></i>
                        </button>
                        <a href="${seg.path}" download class="btn-icon" title="Télécharger">
                            <i class="fas fa-download"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `;
        body.innerHTML += row;
    });
}

/**
 * Gère la lecture et l'arrêt des segments audio.
 * Assure qu'un seul segment est lu à la fois.
 * @param {string} path - URL du fichier segment
 * @param {HTMLButtonElement} buttonElement - Le bouton qui a déclenché l'action (pour changer l'icône)
 */
function playSegment(path, buttonElement) {
    const icon = buttonElement.querySelector('i');

    // Si un autre audio est en cours de lecture
    if (currentPlayingAudio && currentPlayingAudio !== buttonElement._audioInstance) {
        currentPlayingAudio.pause();
        currentPlayingAudio.currentTime = 0;
        if (currentPlayingButton) {
            currentPlayingButton.querySelector('i').classList.replace('fa-stop', 'fa-play');
        }
    }

    // Associer l'instance Audio au bouton pour un accès facile
    if (!buttonElement._audioInstance) {
        buttonElement._audioInstance = new Audio(path);
        buttonElement._audioInstance.onended = () => {
            icon.classList.replace('fa-stop', 'fa-play');
            currentPlayingAudio = null;
            currentPlayingButton = null;
        };
    }
    
    const audio = buttonElement._audioInstance;

    if (audio.paused) {
        // Démarrer la lecture
        audio.play();
        icon.classList.replace('fa-play', 'fa-stop');
        currentPlayingAudio = audio;
        currentPlayingButton = buttonElement;
    } else {
        // Mettre en pause
        audio.pause();
        audio.currentTime = 0; // Remettre à zéro pour la prochaine lecture
        icon.classList.replace('fa-stop', 'fa-play');
        currentPlayingAudio = null;
        currentPlayingButton = null;
    }
}
