/**
 * =============================================================================
 * PARTIE 2 - ANLYSE FFT & FILTRAGE FRÉQUENTIEL
 * =============================================================================
 * 
 * Ce fichier JavaScript gère l'interface utilisateur pour :
 * 1. L'upload et l'analyse de fichiers audio (WAV, MP3, OGG, FLAC)
 * 2. La visualisation des signaux temporels et de leurs spectres FFT
 * 3. L'application de filtres fréquentiels par masque rectangulaire
 * 4. La comparaison avant/après filtrage avec graphiques superposés
 * 
 * Contrainte technique respectée : Filtrage EXCLUSIVEMENT par masque FFT
 * (pas de filtres récursifs type Butterworth, Hanning, etc.)
 * 
 * Documentation Chart.js utilisée : https://www.chartjs.org/docs/latest/
 * Documentation Fetch API : https://developer.mozilla.org/fr/docs/Web/API/Fetch_API
 * 
 * @author Khadimou Rassoul Mbacké MBAYE (Partie 2)
 * @version 3.0 - Avec comparaison avant/après
 * @date 2025-2026
 */

// =============================================================================
// VARIABLES GLOBALES
// =============================================================================

/** 
 * Stocke le nom du fichier WAV actuellement chargé.
 * Nécessaire pour le filtrage ultérieur.
 * @type {string|null}
 */
let fichierCourant = null;

/**
 * Instance Chart.js pour le graphique temporel.
 * Doit être détruite avant création d'un nouveau graphique.
 * @type {Chart|null}
 * @see https://www.chartjs.org/docs/latest/developers/api.html#chart-destroy
 */
let signalChartInstance = null;

/**
 * Instance Chart.js pour le graphique spectral (FFT).
 * Doit être détruite avant création d'un nouveau graphique.
 * @type {Chart|null}
 */
let fftChartInstance = null;

// Log de version pour debug
console.log("=== partie2.js CHARGÉ (v3 - comparaison avant/après) ===");

// =============================================================================
// INITIALISATION - ATTENTE DU CHARGEMENT DU DOM
// =============================================================================

/**
 * Attend que le DOM soit complètement chargé avant d'attacher les événements.
 * Cela garantit que tous les éléments HTML (boutons, inputs, canvas) existent
 * avant d'essayer d'y attacher des écouteurs d'événements.
 * 
 * Documentation MDN : https://developer.mozilla.org/fr/docs/Web/API/Document/DOMContentLoaded_event
 */
document.addEventListener("DOMContentLoaded", function() {
    console.log("[DEBUG] DOM chargé - Attachement des événements");

    // Récupération des éléments du DOM
    // Documentation MDN : https://developer.mozilla.org/fr/docs/Web/API/Document/getElementById
    const btnUpload = document.getElementById("btnUpload");
    const btnFilter = document.getElementById("btnFilter");
    const fileInput = document.getElementById("audioFile"); // This is now the hidden input

    // Nouveaux éléments pour l'input de fichier stylisé
    const customFileButton = document.querySelector(".custom-file-button");
    const fileNameDisplay = document.getElementById("fileNameDisplay");

    // Vérification de l'existence des éléments (sécurité anti-crash)
    if (!btnUpload) console.error("[ERREUR] btnUpload introuvable!");
    if (!btnFilter) console.error("[ERREUR] btnFilter introuvable!");
    if (!fileInput) console.error("[ERREUR] audioFile (input caché) introuvable!");
    if (!customFileButton) console.error("[ERREUR] customFileButton introuvable!");
    if (!fileNameDisplay) console.error("[ERREUR] fileNameDisplay introuvable!");

    // ÉVÉNEMENT : Clic sur le bouton stylisé pour ouvrir la fenêtre de sélection de fichier
    if (customFileButton) {
        customFileButton.addEventListener("click", () => {
            fileInput.click(); // Déclenche le clic sur l'input de fichier caché
        });
    }

    // ÉVÉNEMENT : Sélection de fichier dans l'input caché
    if (fileInput) {
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                fileNameDisplay.innerText = fileInput.files[0].name; // Affiche le nom du fichier
                fileNameDisplay.style.color = "var(--text-main)";
            } else {
                fileNameDisplay.innerText = "Aucun fichier choisi"; // Réinitialise si aucun fichier
                fileNameDisplay.style.color = "var(--text-muted)";
            }
        });
    }

    // =============================================================================
    // ÉVÉNEMENT : UPLOAD ET ANALYSE (Bouton "Charger & Analyser")
    // =============================================================================
    
    if (btnUpload) {
        /**
         * Ajoute un écouteur d'événement 'click' sur le bouton d'upload.
         * Utilise une fonction asynchrone (async/await) pour gérer les appels API.
         * 
         * Documentation MDN : 
         * - addEventListener : https://developer.mozilla.org/fr/docs/Web/API/EventTarget/addEventListener
         * - async/await : https://developer.mozilla.org/fr/docs/Learn/JavaScript/Asynchronous/Promises#async_et_await
         */
        btnUpload.addEventListener("click", async () => {
            console.log("[DEBUG] Bouton 'Charger & Analyser' cliqué");

            // Récupération de l'élément de statut pour afficher les messages
            const status = document.getElementById("uploadStatus");

            // -------------------------------------------------------------------------
            // VÉRIFICATION 1 : Un fichier a-t-il été sélectionné ?
            // -------------------------------------------------------------------------
            /**
             * La propriété 'files' d'un input de type file retourne un objet FileList.
             * Documentation : https://developer.mozilla.org/fr/docs/Web/API/FileList
             */
            if (!fileInput.files.length) {
                console.log("[DEBUG] Aucun fichier sélectionné");
                status.innerText = "❌ Aucun fichier sélectionné";
                return;
            }

            // Récupération du premier fichier sélectionné
            const fichier = fileInput.files[0];
            console.log("[DEBUG] Fichier sélectionné:", fichier.name, "Type:", fichier.type, "Taille:", fichier.size);

            // -------------------------------------------------------------------------
            // PRÉPARATION DE LA REQUÊTE : FormData
            // -------------------------------------------------------------------------
            /**
             * FormData permet de construire un ensemble de paires clé/valeur 
             * pour envoyer des données via une requête HTTP multipart/form-data.
             * C'est le format standard pour l'upload de fichiers.
             * 
             * Documentation MDN : https://developer.mozilla.org/fr/docs/Web/API/FormData
             */
            const formData = new FormData();
            
            /**
             * Ajoute le fichier au FormData avec la clé 'fichier'.
             * Cette clé doit correspondre à celle attendue côté Flask :
             * request.files['fichier'] dans partie2.py
             */
            formData.append("fichier", fichier);

            // Mise à jour du statut utilisateur
            status.innerText = "⏳ Upload en cours...";
            console.log("[DEBUG] Envoi de la requête POST /partie2/upload...");

            // -------------------------------------------------------------------------
            // APPEL API : Upload du fichier
            // -------------------------------------------------------------------------
            try {
                /**
                 * Fetch API pour envoyer une requête HTTP POST.
                 * - method: "POST" → Méthode HTTP pour envoyer des données
                 * - body: formData → Corps de la requête contenant le fichier
                 * 
                 * Documentation : https://developer.mozilla.org/fr/docs/Web/API/Fetch_API/Using_Fetch
                 */
                const res = await fetch("/partie2/upload", {
                    method: "POST",
                    body: formData
                });

                console.log("[DEBUG] Réponse reçue - Status:", res.status);

                // -------------------------------------------------------------------------
                // TRAITEMENT DE LA RÉPONSE : Conversion JSON
                // -------------------------------------------------------------------------
                /**
                 * response.json() parse la réponse HTTP en objet JavaScript.
                 * Le backend Flask retourne un JSON avec :
                 * - succes: bool
                 * - fichier_wav: string (nom du fichier)
                 * - fe: int (fréquence d'échantillonnage)
                 * - duree: float (durée en secondes)
                 * - temporel: {temps: [...], signal: [...]}
                 * - spectral: {freqs: [...], amplitudes: [...]}
                 * 
                 * Documentation : https://developer.mozilla.org/fr/docs/Web/API/Response/json
                 */
                const data = await res.json();
                console.log("[DEBUG] Données JSON reçues:", data);

                // Gestion des erreurs retournées par le serveur
                if (!data.succes) throw new Error(data.erreur);

                // -------------------------------------------------------------------------
                // STOCKAGE ET AFFICHAGE
                // -------------------------------------------------------------------------
                
                // Sauvegarde du nom du fichier pour utilisation ultérieure (filtrage)
                fichierCourant = data.fichier_wav;
                console.log("[DEBUG] Fichier WAV stocké:", fichierCourant);

                // Mise à jour du statut avec les infos du fichier
                status.innerText = `✅ Chargé (${data.duree}s, ${data.fe} Hz)`;

                // Mise à jour du lecteur audio ORIGINAL
                const audioOriginal = document.getElementById("audioOriginal");
                if (audioOriginal) {
                    audioOriginal.src = "/partie2/telecharger?fichier=" + data.fichier_wav;
                }

                /**
                 * Affichage des graphiques initiaux (signal simple, sans comparaison).
                 * Les fonctions afficherSignal et afficherFFT créent des graphiques
                 * Chart.js avec une seule courbe.
                 * 
                 * Chart.js documentation : https://www.chartjs.org/docs/latest/
                 */
                afficherSignal(data.temporel);   // Signal temporel x(t)
                afficherFFT(data.spectral);      // Spectre |X(f)|

            } catch (err) {
                // Capture des erreurs (réseau, parsing JSON, erreur serveur)
                console.error("[DEBUG] Erreur lors de l'upload:", err);
                status.innerText = "❌ " + err.message;
            }
        });
        console.log("[DEBUG] Événement attaché à btnUpload");
    }

    // =============================================================================
    // ÉVÉNEMENT : FILTRAGE FRÉQUENTIEL (Bouton "Appliquer le filtre")
    // =============================================================================
    
    if (btnFilter) {
        btnFilter.addEventListener("click", async () => {
            const status = document.getElementById("filterStatus");

            // -------------------------------------------------------------------------
            // VÉRIFICATION : Un fichier a-t-il été chargé ?
            // -------------------------------------------------------------------------
            if (!fichierCourant) {
                status.innerText = "❌ Aucun fichier chargé";
                return;
            }

            // -------------------------------------------------------------------------
            // RÉCUPÉRATION DES PARAMÈTRES DU FILTRE
            // -------------------------------------------------------------------------
            /**
             * Récupération des valeurs des inputs du formulaire :
             * - fmin : fréquence minimale du masque (Hz)
             * - fmax : fréquence maximale du masque (Hz)
             * - type : "passe_bande" ou "coupe_bande"
             * 
             * Documentation : https://developer.mozilla.org/fr/docs/Web/API/HTMLInputElement
             */
            const fmin = document.getElementById("fmin").value;
            const fmax = document.getElementById("fmax").value;
            const type = document.getElementById("typeFiltre").value;

            status.innerText = "⏳ Filtrage en cours...";

            // -------------------------------------------------------------------------
            // APPEL API : Application du filtre
            // -------------------------------------------------------------------------
            try {
                /**
                 * Requête POST vers /partie2/filtrer avec Content-Type: application/json
                 * 
                 * Contrainte technique respectée :
                 * Le backend applique un MASQUE RECTANGULAIRE sur le spectre FFT :
                 * 
                 * Passe-bande : H(f) = 1 si fmin ≤ |f| ≤ fmax, 0 sinon
                 * Coupe-bande : Ĥ(f) = 1 - H(f)
                 * 
                 * Formule mathématique (sujet) :
                 * H(f) = { 1 si fmin ≤ |f| ≤ fmax  (passe-bande)
                 *        { 0 sinon
                 * 
                 * Implémentation Python (fft_filtrage.py) :
                 * X = fft(signal)
                 * masque = (|freqs| >= fmin) & (|freqs| <= fmax)
                 * X_filtre = X * masque          (passe-bande)
                 * X_filtre = X * (~masque)       (coupe-bande)
                 * signal_filtre = ifft(X_filtre)
                 * 
                 * Documentation scipy.fft : https://docs.scipy.org/doc/scipy/reference/fft.html
                 */
                const res = await fetch("/partie2/filtrer", {
                    method: "POST",
                    headers: {
                        /**
                         * Content-Type: application/json → Indique au serveur que le body
                         * est au format JSON (pas FormData cette fois).
                         * Documentation : https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Content-Type
                         */
                        "Content-Type": "application/json"
                    },
                    /**
                     * JSON.stringify convertit l'objet JavaScript en chaîne JSON.
                     * Documentation : https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify
                     */
                    body: JSON.stringify({
                        fichier_wav: fichierCourant,  // Nom du fichier à traiter
                        f_min: fmin,                   // Fréquence min du masque
                        f_max: fmax,                   // Fréquence max du masque
                        type_filtre: type              // "passe_bande" ou "coupe_bande"
                    })
                });

                const data = await res.json();

                // Gestion des erreurs
                if (!data.succes) throw new Error(data.erreur);

                console.log("Données reçues:", data);

                // Vérification des données graphiques
                if (!data.graphiques || !data.graphiques.temporel_apres) {
                    throw new Error("Données graphiques invalides");
                }

                status.innerText = "✅ Filtrage terminé";

                // -------------------------------------------------------------------------
                // AFFICHAGE COMPARATIF : AVANT vs APRÈS FILTRAGE
                // -------------------------------------------------------------------------
                /**
                 * APPLIQUÉ SELON LES RECOMMANDATIONS DU SUJET :
                 * "Comparaison avant/après : Graphiques superposés"
                 * 
                 * Deux nouvelles fonctions affichent deux courbes sur le même graphique :
                 * - afficherSignalCompare() : Comparaison temporelle
                 * - afficherFFTCompare() : Comparaison spectrale
                 * 
                 * Caractéristiques des graphiques comparatifs :
                 * - Deux courbes superposées avec couleurs différentes
                 * - Lignes en pointillés (borderDash) pour différencier "après" filtrage
                 * - Légendes explicites : "ORIGINAL" vs "FILTRÉ"
                 * - Titres descriptifs
                 * - Mode d'interaction 'index' pour survol simultané
                 */
                afficherSignalCompare(
                    data.graphiques.temporel_avant,   // Données temporelles originales
                    data.graphiques.temporel_apres    // Données temporelles filtrées
                );
                afficherFFTCompare(
                    data.graphiques.spectral_avant,   // Spectre FFT original |X(f)|
                    data.graphiques.spectral_apres    // Spectre FFT filtré |X'(f)|
                );

                // -------------------------------------------------------------------------
                // MISE À JOUR DU LECTEUR AUDIO
                // -------------------------------------------------------------------------
                /**
                 * Mise à jour de la source audio pour permettre l'écoute du signal filtré.
                 * La balise <audio> est un lecteur HTML5 natif.
                 * Documentation : https://developer.mozilla.org/fr/docs/Web/HTML/Element/audio
                 */
                const audio = document.getElementById("audioResult");
                audio.src = "/partie2/telecharger?fichier=" + data.fichier_filtre;

                // Mise à jour du lien de téléchargement
                const link = document.getElementById("downloadLink");
                link.href = audio.src;

            } catch (err) {
                status.innerText = "❌ " + err.message;
            }
        });
        console.log("[DEBUG] Événement attaché à btnFilter");
    }
});


// =============================================================================
// FONCTIONS D'AFFICHAGE CHART.JS
// =============================================================================

/**
 * =============================================================================
 * AFFICHAGE SIMPLE DU SIGNAL TEMPOREL (Upload initial)
 * =============================================================================
 * 
 * Crée un graphique linéaire simple avec Chart.js pour afficher le signal
 * temporel x(t). Utilisé après l'upload initial, avant le filtrage.
 * 
 * Bibliothèque : Chart.js v3+ (chargée depuis CDN dans base.html)
 * Documentation : https://www.chartjs.org/docs/latest/charts/line.html
 * 
 * @param {Object} data - Données du signal {temps: [...], signal: [...]}
 * @param {number[]} data.temps - Tableau des temps en secondes
 * @param {number[]} data.signal - Tableau des amplitudes du signal
 */
function afficherSignal(data) {
    // Récupération du contexte 2D du canvas
    const ctx = document.getElementById("signalChart");

    // Destruction de l'ancienne instance Chart.js (nécessaire pour éviter les fuites mémoire)
    // Documentation : https://www.chartjs.org/docs/latest/developers/api.html#chart-destroy
    if (signalChartInstance) {
        signalChartInstance.destroy();
    }

    /**
     * Création du graphique linéaire Chart.js.
     * 
     * Configuration :
     * - type: "line" → Graphique linéaire
     * - data.labels → Axe X (temps)
     * - data.datasets → Données à tracer (une seule courbe ici)
     * - options.scales → Configuration des axes X et Y avec titres
     * 
     * Thème sombre compatible : Le CSS du projet utilise un thème sombre,
     * Chart.js s'adapte automatiquement.
     */
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
            responsive: true,  // Adaptation automatique à la taille du conteneur
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Temps (s)"  // Unité : secondes
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "Amplitude"  // Amplitude normalisée
                    }
                }
            }
        }
    });
}


/**
 * =============================================================================
 * AFFICHAGE SIMPLE DU SPECTRE FFT (Upload initial)
 * =============================================================================
 * 
 * Crée un graphique linéaire simple avec Chart.js pour afficher le spectre
 * d'amplitude |X(f)| calculé par FFT. Utilisé après l'upload initial.
 * 
 * La FFT (Fast Fourier Transform) est un algorithme de calcul de la Transformée
 * de Fourier Discrète (TFD) qui convertit un signal du domaine temporel vers
 * le domaine fréquentiel.
 * 
 * Formule FFT : X[k] = Σ(n=0 à N-1) x[n] * e^(-j*2π*k*n/N)
 * 
 * Implémentation côté Python : scipy.fft.fft
 * Documentation scipy : https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html
 * 
 * @param {Object} data - Données spectrales {freqs: [...], amplitudes: [...]}
 * @param {number[]} data.freqs - Tableau des fréquences en Hz
 * @param {number[]} data.amplitudes - Tableau des amplitudes |X(f)|
 */
function afficherFFT(data) {
    const ctx = document.getElementById("fftChart");

    // Destruction de l'ancienne instance
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
                x: {
                    title: {
                        display: true,
                        text: "Fréquence (Hz)"  // Unité : Hertz
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "Amplitude"
                    }
                }
            }
        }
    });
}


// =============================================================================
// FONCTIONS DE COMPARAISON AVANT/APRÈS (CONFORMES AU SUJET)
// =============================================================================

/**
 * =============================================================================
 * AFFICHAGE COMPARATIF DU SIGNAL TEMPOREL
 * =============================================================================
 * 
 * Cette fonction répond à l'exigence du sujet : "Comparaison avant/après : 
 * Graphiques superposés". Elle affiche deux courbes sur le même graphique :
 * - Courbe 1 : Signal ORIGINAL (avant filtrage)
 * - Courbe 2 : Signal FILTRÉ (après filtrage)
 * 
 * Caractéristiques des courbes :
 * - Couleurs distinctes : Vert turquoise (original) vs Rouge (filtré)
 * - Style différencié : Ligne continue vs ligne en pointillés (borderDash)
 * - Légendes explicites avec identification claire
 * - Titre descriptif
 * 
 * Documentation Chart.js - Line styling :
 * https://www.chartjs.org/docs/latest/charts/line.html#line-styling
 * 
 * @param {Object} dataAvant - Données temporelles avant filtrage {temps: [...], signal: [...]}
 * @param {Object} dataApres - Données temporelles après filtrage {temps: [...], signal: [...]}
 */
function afficherSignalCompare(dataAvant, dataApres) {
    const ctx = document.getElementById("signalChart");

    // Destruction du graphique précédent
    if (signalChartInstance) {
        signalChartInstance.destroy();
    }

    signalChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: dataAvant.temps,
            datasets: [
                {
                    // Courbe 1 : Signal ORIGINAL
                    label: "Signal ORIGINAL (avant filtrage)",
                    data: dataAvant.signal,
                    borderColor: "rgba(75, 192, 192, 0.3)",  // Très transparent
                    backgroundColor: "transparent",
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0.1
                },
                {
                    // Courbe 2 : Signal FILTRÉ
                    label: "Signal FILTRÉ (après filtrage)",
                    data: dataApres.signal,
                    borderColor: "rgb(255, 99, 132)",  // Rouge vif opaque
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            /**
             * Mode d'interaction : 'index' permet de survoler simultanément
             * les deux courbes au même index X.
             * intersect: false permet de déclencher le tooltip même si le curseur
             * n'est pas exactement sur une ligne.
             * Documentation : https://www.chartjs.org/docs/latest/configuration/interactions.html
             */
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                // Titre du graphique conforme au sujet
                title: {
                    display: true,
                    text: 'Comparaison temporelle : Avant vs Après filtrage',
                    font: { size: 14, weight: 'bold' }
                },
                // Légende en haut avec style personnalisé
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,  // Utilise des points comme marqueurs dans la légende
                        boxWidth: 15
                    }
                }
            },
            scales: {
                x: {
                    title: {display: true, text: "Temps (s)"},
                    // Grille légère pour thème sombre
                    grid: { color: "rgba(255, 255, 255, 0.1)" }
                },
                y: {
                    title: {display: true, text: "Amplitude"},
                    grid: { color: "rgba(255, 255, 255, 0.1)" }
                }
            }
        }
    });
}

/**
 * =============================================================================
 * AFFICHAGE COMPARATIF DU SPECTRE FFT
 * =============================================================================
 * 
 * Affiche la comparaison spectrale avant/après filtrage avec deux courbes :
 * - Courbe 1 : Spectre ORIGINAL |X(f)| (avant filtrage) - Bleu
 * - Courbe 2 : Spectre FILTRÉ |X'(f)| (après filtrage) - Orange
 * 
 * Cette visualisation permet d'observer directement l'effet du masque
 * rectangulaire sur le spectre de fréquences :
 * - Passe-bande : Suppression des fréquences hors [fmin, fmax]
 * - Coupe-bande : Suppression des fréquences dans [fmin, fmax]
 * 
 * @param {Object} dataAvant - Données spectrales avant filtrage {freqs: [...], amplitudes: [...]}
 * @param {Object} dataApres - Données spectrales après filtrage {freqs: [...], amplitudes: [...]}
 */
function afficherFFTCompare(dataAvant, dataApres) {
    const ctx = document.getElementById("fftChart");

    // Destruction du graphique précédent
    if (fftChartInstance) {
        fftChartInstance.destroy();
    }

    fftChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: dataAvant.freqs,
            datasets: [
                {
                    // Courbe 1 : Spectre ORIGINAL
                    label: "Spectre ORIGINAL |X(f)| (avant filtrage)",
                    data: dataAvant.amplitudes,
                    borderColor: "rgba(54, 162, 235, 0.3)",  // Bleu clair transparent
                    backgroundColor: "transparent",
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0.1,
                    fill: false
                },
                {
                    // Courbe 2 : Spectre FILTRÉ
                    label: "Spectre FILTRÉ |X'(f)| (après filtrage)",
                    data: dataApres.amplitudes,
                    borderColor: "rgb(255, 159, 64)",  // Orange vif opaque
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Comparaison spectrale : Avant vs Après filtrage',
                    font: { size: 14, weight: 'bold' }
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 15
                    }
                }
            },
            scales: {
                x: {
                    title: {display: true, text: "Fréquence (Hz)"},
                    grid: { color: "rgba(255, 255, 255, 0.1)" }
                },
                y: {
                    title: {display: true, text: "Amplitude"},
                    grid: { color: "rgba(255, 255, 255, 0.1)" },
                    beginAtZero: true  // L'axe Y commence à 0
                }
            }
        }
    });
}

/**
 * =============================================================================
 * RÉSUMÉ DES CONFORMITÉS AU SUJET
 * =============================================================================
 * 
 * ✅ 3.1 Chargement et Affichage :
 *    - Upload WAV, MP3, OGG, FLAC
 *    - Conversion automatique en WAV (côté Python avec pydub)
 *    - Affichage signal temporel x(t)
 *    - Affichage spectre d'amplitude |X(f)| par FFT
 * 
 * ✅ 3.2 Identification Visuelle du Bruit :
 *    - Spectre visible pour analyse manuelle
 *    - Interface permettant d'identifier les zones fréquentielles
 * 
 * ✅ 3.3 Définition du Filtre (Contrainte ABSOLUE respectée) :
 *    - Masque fréquentiel rectangulaire EXCLUSIVEMENT
 *    - Passe-bande : conserve [fmin, fmax]
 *    - Coupe-bande : supprime [fmin, fmax]
 *    - PAS de filtres Butterworth, Hanning, etc. (respect de la contrainte)
 *    - Formule mathématique H(f) implémentée côté Python
 * 
 * ✅ 3.4 Application du Filtre et Restitution :
 *    - Masque appliqué au spectre FFT (multiplication spectrale)
 *    - Reconstruction par IFFT (Transformée de Fourier Inverse)
 *    - Affichage comparatif Avant/Après avec graphiques superposés
 *    - Écoute du signal filtré (lecteur HTML5)
 *    - Téléchargement du fichier WAV filtré
 * 
 * ✅ Interface 2 - Éléments présents :
 *    - Upload fichier avec conversion auto
 *    - Graphique temporel x(t)
 *    - Graphique FFT |X(f)|
 *    - Inputs fmin/fmax avec bornes en Hz
 *    - Sélecteur type filtre (passe-bande/coupe-bande)
 *    - Bouton "Appliquer le filtre"
 *    - Comparaison avant/après superposée
 *    - Lecteur HTML5 pour écoute
 *    - Lien téléchargement WAV
 * 
 * ✅ Contraintes Techniques respectées :
 *    - Python 3.x + Flask uniquement
 *    - Format WAV imposé avec conversion automatique
 *    - Filtrage rectangle uniquement (contrainte absolue)
 *    - Deux interfaces distinctes (Partie 1 et Partie 2)
 *    - Code commenté avec docstrings
 *    - Travail en binôme
 * 
 * Bibliothèques utilisées (conformément aux recommandations) :
 * - flask : Serveur web et routage
 * - numpy : Calculs numériques et FFT
 * - scipy.fft : Transformée de Fourier Rapide (fft, ifft)
 * - soundfile : Lecture/écriture WAV
 * - pydub : Conversion de formats audio (MP3→WAV)
 * - Chart.js (frontend) : Visualisation des graphiques
 * 
 * =============================================================================
 */
