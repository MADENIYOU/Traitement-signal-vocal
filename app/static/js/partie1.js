let mediaRecorder;
let audioChunks = [];
let audioBlob;
let lastSavedFilePath = "";

const btnRecord = document.getElementById('btnRecord');
const btnStop = document.getElementById('btnStop');
const btnSave = document.getElementById('btnSave');
const btnSegment = document.getElementById('btnSegment');
const status = document.getElementById('status');
const audioPlayback = document.getElementById('audioPlayback');

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
        };

        mediaRecorder.start();
        btnRecord.disabled = true;
        btnRecord.classList.add('recording-pulse');
        btnStop.disabled = false;
        status.innerHTML = '<i class="fas fa-circle animate__animated animate__flash animate__infinite"></i> Enregistrement en cours...';
        status.style.color = "#ff5252";
        status.style.background = "rgba(255, 82, 82, 0.1)";
    } catch (err) {
        alert("Erreur micro : " + err);
    }
};

btnStop.onclick = () => {
    mediaRecorder.stop();
    btnRecord.disabled = false;
    btnRecord.classList.remove('recording-pulse');
    btnStop.disabled = true;
    status.innerHTML = '<i class="fas fa-check-circle"></i> Enregistrement terminé.';
    status.style.color = "var(--vert-nature)";
    status.style.background = "rgba(46, 125, 50, 0.1)";
};

btnSave.onclick = async () => {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    formData.append('locuteur', document.getElementById('locuteur').value);
    formData.append('frequence', document.getElementById('frequence').value);
    formData.append('codage', document.querySelector('input[name="codage"]:checked').value);

    status.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sauvegarde sur le serveur...';
    
    try {
        const response = await fetch('/partie1/sauvegarder', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (result.path) {
            lastSavedFilePath = result.path;
            status.innerHTML = '<i class="fas fa-cloud-upload-alt"></i> Fichier sauvegardé avec succès !';
            btnSegment.disabled = false;
            btnSegment.classList.add('animate__animated', 'animate__pulse');
            document.getElementById('segmentStatus').innerText = "Fichier prêt pour segmentation.";
        }
    } catch (err) {
        status.innerText = "Erreur lors de la sauvegarde.";
    }
};

btnSegment.onclick = async () => {
    const data = {
        filepath: lastSavedFilePath,
        seuil: document.getElementById('seuil').value,
        duree_min: document.getElementById('duree_min').value
    };

    const segStatus = document.getElementById('segmentStatus');
    segStatus.innerText = "Segmentation en cours...";

    try {
        const response = await fetch('/partie1/segmenter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        displaySegments(result.segments);
        segStatus.innerText = result.message;
    } catch (err) {
        segStatus.innerText = "Erreur lors de la segmentation.";
    }
};

function displaySegments(segments) {
    const body = document.getElementById('segmentsBody');
    body.innerHTML = "";
    
    segments.forEach(seg => {
        const row = `
            <tr>
                <td>${seg.id}</td>
                <td>${seg.filename}</td>
                <td>${seg.duration.toFixed(2)}</td>
                <td>
                    <a href="${seg.path}" download class="btn btn-primary" style="padding: 0.3rem 0.6rem;">
                        <i class="fas fa-download"></i>
                    </a>
                </td>
            </tr>
        `;
        body.innerHTML += row;
    });
}
