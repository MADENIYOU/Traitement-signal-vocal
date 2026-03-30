let mediaRecorder;
let audioChunks = [];
let audioBlob;
let lastSavedFilePath = "";
let timerInterval;
let startTime;

const btnRecord = document.getElementById('btnRecord');
const btnStop = document.getElementById('btnStop');
const btnSave = document.getElementById('btnSave');
const btnSegment = document.getElementById('btnSegment');
const status = document.getElementById('status');
const audioPlayback = document.getElementById('audioPlayback');
const btnRecordSpan = btnRecord.querySelector('span');

function updateTimer() {
    const now = Date.now();
    const diff = now - startTime;
    const seconds = Math.floor((diff / 1000) % 60);
    const minutes = Math.floor((diff / (1000 * 60)) % 60);
    const timeStr = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    btnRecord.querySelector('span').innerText = timeStr;
}

btnRecord.onclick = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;
            audioPlayback.style.display = 'block';
            btnSave.disabled = false;
            
            // Reset button text
            btnRecord.querySelector('span').innerText = "Enregistrer";
            btnRecord.classList.remove('active', 'pulse-red');
            clearInterval(timerInterval);
        };

        const dureeSec = parseFloat(document.getElementById('duree').value) || 5;
        mediaRecorder.start();
        
        // Start Timer
        startTime = Date.now();
        timerInterval = setInterval(updateTimer, 1000);

        btnRecord.disabled = true;
        btnRecord.classList.add('active', 'pulse-red');
        btnStop.disabled = false;
        
        status.innerHTML = '<i class="fas fa-microphone-alt animate__animated animate__flash animate__infinite"></i> Acquisition du signal en cours...';
        status.style.color = "var(--danger)";

        // Arrêt automatique après la durée définie
        setTimeout(() => {
            if (mediaRecorder.state === "recording") {
                btnStop.click();
            }
        }, dureeSec * 1000);

    } catch (err) {
        alert("Erreur micro : " + err);
    }
};

btnStop.onclick = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        btnRecord.disabled = false;
        btnStop.disabled = true;
        status.innerHTML = '<i class="fas fa-check-circle"></i> Signal capturé avec succès.';
        status.style.color = "var(--success)";
    }
};

btnSave.onclick = async () => {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    formData.append('locuteur', document.getElementById('locuteur').value);
    formData.append('frequence', document.getElementById('frequence').value);
    formData.append('codage', document.querySelector('select[name="codage"]').value);

    status.innerHTML = '<i class="fas fa-sync fa-spin"></i> Envoi des données au serveur...';
    
    try {
        const response = await fetch('/partie1/sauvegarder', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (result.path) {
            lastSavedFilePath = result.path;
            status.innerHTML = '<i class="fas fa-file-audio"></i> Fichier .wav généré et prêt.';
            btnSegment.disabled = false;
            btnSegment.classList.add('animate__animated', 'animate__pulse');
            document.getElementById('segmentStatus').innerText = "Prêt pour la segmentation automatique.";
        }
    } catch (err) {
        status.innerText = "Erreur de communication avec le serveur.";
    }
};

btnSegment.onclick = async () => {
    const data = {
        filepath: lastSavedFilePath,
        seuil: document.getElementById('seuil').value,
        duree_min: document.getElementById('duree_min').value
    };

    const segStatus = document.getElementById('segmentStatus');
    segStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Algorithme de segmentation en cours...';

    try {
        const response = await fetch('/partie1/segmenter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        displaySegments(result.segments);
        segStatus.innerText = result.message;
        
        // AUTO-SCROLL to results
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (err) {
        segStatus.innerText = "Erreur lors du traitement algorithmique.";
    }
};

function displaySegments(segments) {
    const body = document.getElementById('segmentsBody');
    const countSpan = document.getElementById('segmentCount');
    body.innerHTML = "";
    countSpan.innerText = `${segments.length} segments`;
    
    segments.forEach((seg, index) => {
        const row = `
            <tr class="animate__animated animate__fadeInUp" style="animation-delay: ${index * 0.1}s">
                <td style="font-weight: 600; color: var(--accent-cyan);">#${seg.id.toString().padStart(3, '0')}</td>
                <td>${seg.nom}</td>
                <td><span style="background: rgba(34, 211, 238, 0.1); padding: 0.2rem 0.5rem; border-radius: 4px; font-family: monospace;">${seg.duree.toFixed(3)}s</span></td>
                <td style="text-align: right;">
                    <div style="display: flex; gap: 10px; justify-content: flex-end;">
                        <button onclick="playSegment('${seg.path}')" class="btn" style="padding: 0.5rem; background: var(--accent-blue); width: 35px; height: 35px;">
                            <i class="fas fa-play"></i>
                        </button>
                        <a href="${seg.path}" download class="btn" style="padding: 0.5rem; background: rgba(255,255,255,0.1); width: 35px; height: 35px;">
                            <i class="fas fa-download"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `;
        body.innerHTML += row;
    });
}

function playSegment(path) {
    const audio = new Audio(path);
    audio.play();
}
