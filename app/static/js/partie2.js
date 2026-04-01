let fichierCourant = null;
let signalChartInstance = null;
let fftChartInstance = null;

// Upload + analyse
document.getElementById("btnUpload").addEventListener("click", async () => {
    const fileInput = document.getElementById("audioFile");
    const status = document.getElementById("uploadStatus");

    if (!fileInput.files.length) {
        status.innerText = "❌ Aucun fichier sélectionné";
        return;
    }

    const formData = new FormData();
    formData.append("fichier", fileInput.files[0]);

    status.innerText = "⏳ Upload en cours...";

    try {
        const res = await fetch("/partie2/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (!data.succes) throw new Error(data.erreur);

        fichierCourant = data.fichier_wav;

        status.innerText = `✅ Chargé (${data.duree}s, ${data.fe} Hz)`;

        afficherSignal(data.temporel);
        afficherFFT(data.spectral);

    } catch (err) {
        status.innerText = "❌ " + err.message;
    }
});


// Filtrage
document.getElementById("btnFilter").addEventListener("click", async () => {
    const status = document.getElementById("filterStatus");

    if (!fichierCourant) {
        status.innerText = "❌ Aucun fichier chargé";
        return;
    }

    const fmin = document.getElementById("fmin").value;
    const fmax = document.getElementById("fmax").value;
    const type = document.getElementById("typeFiltre").value;

    status.innerText = "⏳ Filtrage en cours...";

    try {
        const res = await fetch("/partie2/filtrer", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                fichier_wav: fichierCourant,
                f_min: fmin,
                f_max: fmax,
                type_filtre: type
            })
        });

        const data = await res.json();

        if (!data.succes) throw new Error(data.erreur);

        // Debug rapide
        console.log("Données reçues:", data);

        // Sécurité anti-crash
        if (!data.graphiques || !data.graphiques.temporel_apres) {
            throw new Error("Données graphiques invalides");
        }

        status.innerText = "✅ Filtrage terminé";

        afficherSignal(data.graphiques.temporel_apres);
        afficherFFT(data.graphiques.spectral_apres);

        // Audio
        const audio = document.getElementById("audioResult");
        audio.src = "/partie2/telecharger?fichier=" + data.fichier_filtre;

        // Download
        const link = document.getElementById("downloadLink");
        link.href = audio.src;

    } catch (err) {
        status.innerText = "❌ " + err.message;
    }
});


// Graph signal
function afficherSignal(data) {
    const ctx = document.getElementById("signalChart");

    // 🔥 DESTROY ancien chart
    if (signalChartInstance) {
        signalChartInstance.destroy();
    }

    signalChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.temps,
            datasets: [{
                label: "Signal",
                data: data.signal,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {title: {display: true, text: "Temps (s)"}},
                y: {title: {display: true, text: "Amplitude"}}
            }
        }
    });
}


// Graph FFT
function afficherFFT(data) {
    const ctx = document.getElementById("fftChart");

    // 🔥 DESTROY ancien chart
    if (fftChartInstance) {
        fftChartInstance.destroy();
    }

    fftChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.freqs,
            datasets: [{
                label: "Spectre FFT",
                data: data.amplitudes,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {title: {display: true, text: "Fréquence (Hz)"}},
                y: {title: {display: true, text: "Amplitude"}}
            }
        }
    });
}
