# 🎬 Script de Démonstration Vidéo - SignaVox Partie 2

> **Projet** : Traitement Numérique du Signal - Analyse FFT & Filtrage  
> **Auteur** : Khadimou Rassoul Mbacké MBAYE  
> **Institution** : ESP/UCAD - DIC 2 (2025-2026)  

---

## 📋 STRUCTURE DE LA VIDÉO

Durée totale estimée : **3-4 minutes**  
Résolution recommandée : **1920x1080** (Full HD)  
Format : **MP4 H.264**

---

## 🎙️ SCRIPT AUDIO COMPLET (À LIRE POUR L'ENREGISTREMENT)

### INTRODUCTION (0:00 - 0:30)

**[MUSIQUE DOUCE - FOND TECHNOLOGIQUE]**

**Narrateur** :
> "Bonjour et bienvenue dans cette démonstration de SignaVox, application de traitement numérique du signal vocal.
> 
> Aujourd'hui, nous allons explorer la **Partie 2** du projet : l'analyse fréquentielle par FFT et le filtrage par masque rectangulaire.
> 
> Ce travail a été réalisé dans le cadre du module TNS à l'ESP-UCAD."

---

### CHAPITRE 1 : INTERFACE PRINCIPALE (0:30 - 0:50)

**Visuel** : Page d'accueil → Clic sur "Partie 2 : Filtrage"

**Narrateur** :
> "L'interface de la Partie 2 se présente en deux sections principales.
> À gauche, le chargement audio. À droite, les paramètres de filtrage fréquentiel.
> 
> Commençons par charger un fichier audio."

**Action** : Sélectionner un fichier MP3/WAV

---

### CHAPITRE 2 : UPLOAD ET ANALYSE FFT (0:50 - 1:30)

**Visuel** : Clic sur "Charger & Analyser" → Attente → Graphiques qui apparaissent

**Narrateur** :
> "Cliquons sur 'Charger et Analyser'. L'application convertit automatiquement le fichier en format WAV si nécessaire, puis calcule la Transformée de Fourier Rapide, ou FFT.
> 
> **Voici le signal temporel**, x de t, représentant l'amplitude en fonction du temps.
> 
> **Et voici le spectre fréquentiel**, module de X de f, obtenu par FFT. L'axe horizontal représente les fréquences en Hertz, l'axe vertical les amplitudes.
> 
> Nous pouvons observer les différentes composantes fréquentielles du signal."

---

### CHAPITRE 3 : ZOOM FFT - FONCTIONNALITÉ AVANCÉE (1:30 - 2:00)

**Visuel** : Défilement vers le graphique FFT → Modification de la valeur "Fréq. max"

**Narrateur** :
> "Une fonctionnalité pratique permet de zoomer sur une zone spécifique du spectre.
> 
> Ici, nous changeons la fréquence maximale affichée à **deux mille hertz** pour nous concentrer sur la bande vocale, typiquement entre trois cents et trois mille quatre cents hertz.
> 
> En cliquant sur 'Actualiser', le graphique se met à jour instantanément.
> Cela facilite l'analyse visuelle du bruit et des harmoniques principales."

**Action** : Remettre à 4000 Hz → Clic Actualiser

---

### CHAPITRE 4 : FILTRAGE FRÉQUENTIEL (2:00 - 2:45)

**Visuel** : Défilement vers le panneau de filtrage → Modification des valeurs

**Narrateur** :
> "Passons au filtrage. Définissons les paramètres : fréquence minimale **trois cents hertz**, fréquence maximale **trois mille hertz**.
> 
> Le type de filtre est un **passe-bande rectangulaire**. Conformément aux contraintes du sujet, nous utilisons exclusivement un masque fréquentiel rectangulaire, sans filtres récursifs comme Butterworth ou Hanning.
> 
> La formule mathématique est : H de f égale un si f min inférieur ou égal à module de f inférieur ou égal à f max, zéro sinon.
> 
> Dans le domaine spectral, nous multiplions le spectre FFT par ce masque, puis appliquons la transformée de Fourier inverse."

**Visuel** : Clic sur "Appliquer le filtre" → Chargement → Graphiques comparatifs

---

### CHAPITRE 5 : COMPARAISON AVANT/APRÈS (2:45 - 3:15)

**Visuel** : Les deux graphiques avec courbes superposées

**Narrateur** :
> "Le filtrage est terminé. Observez la **comparaison avant-après**.
> 
> Sur le signal temporel, la courbe verte pointillée représente le signal original, la courbe rouge continue le signal filtré.
> 
> Sur le spectre, le spectre bleu est l'original, le spectre orange le résultat filtré. Nous constatons clairement l'atténuation des fréquences hors de la bande trois cents-trois mille hertz.
> 
> La légende interactive permet d'identifier précisément chaque courbe."

---

### CHAPITRE 6 : ÉCOUTE ET TÉLÉCHARGEMENT (3:15 - 3:40)

**Visuel** : Clic sur lecture audio → Son → Clic téléchargement

**Narrateur** :
> "Nous pouvons écouter le résultat directement dans le navigateur grâce au lecteur HTML5 intégré.
> 
> [SON DU SIGNAL FILTRÉ - QUELQUES SECONDES]
> 
> Enfin, le signal filtré peut être téléchargé au format WAV pour une utilisation ultérieure."

---

### CONCLUSION (3:40 - 3:50)

**Visuel** : Retour à la page d'accueil

**Narrateur** :
> "Cette démonstration illustre les fonctionnalités de la Partie 2 de SignaVox :
> analyse FFT, filtrage par masque rectangulaire, et visualisation comparative.
> 
> Merci de votre attention."

**[MUSIQUE OUTRO - FIN]**

---

## 📸 CAPTURES D'ÉCRAN REQUISES

### Capture 1 : Interface Partie 2
**Timestamp** : 0:30  
**Description** : Vue complète de l'interface avec panneaux Upload et Filtrage  
**Éléments visibles** : Titre, input file, formulaire fmin/fmax, boutons

### Capture 2 : Upload en cours
**Timestamp** : 0:55  
**Description** : Message "⏳ Upload en cours..."  
**Éléments** : Status message, spinner si disponible

### Capture 3 : Signal temporel
**Timestamp** : 1:05  
**Description** : Graphique x(t) affiché  
**Éléments** : Courbe verte, axes, titre

### Capture 4 : Spectre FFT complet
**Timestamp** : 1:15  
**Description** : Graphique |X(f)| avec toutes les fréquences  
**Éléments** : Courbe bleue, axe fréquences 0-8000+ Hz

### Capture 5 : Zoom FFT 2000 Hz
**Timestamp** : 1:40  
**Description** : Input "2000" saisi + graphique zoomé  
**Éléments** : Input value, bouton Actualiser, graphique tronqué

### Capture 6 : Paramètres de filtrage
**Timestamp** : 2:05  
**Description** : Valeurs fmin=300, fmax=3000, type=passe-bande  
**Éléments** : Formulaire rempli

### Capture 7 : Graphiques comparatifs
**Timestamp** : 2:50  
**Description** : Les deux graphiques avec légendes superposées  
**Éléments** : Vert/Rouge sur temporel, Bleu/Orange sur spectral

### Capture 8 : Lecteur audio actif
**Timestamp** : 3:20  
**Description** : Lecteur HTML5 en lecture  
**Éléments** : Bouton pause visible, barre de progression

---

## 📝 CHECKLIST AVANT ENREGISTREMENT

- [ ] Installer un logiciel de capture d'écran (OBS Studio, Camtasia, ou ShareX)
- [ ] Régler la résolution à 1920x1080
- [ ] Préparer un fichier audio test (MP3 ou WAV)
- [ ] Lancer l'application avec `docker-compose up`
- [ ] Vérifier le micro pour la narration
- [ ] Tester les niveaux audio

## 🎨 CONSEILS VISUELS

1. **Transitions fluides** : Utiliser des fondus ou déplacements de caméra doux
2. **Curseur visible** : Activer la surbrillance du curseur pour les clics
3. **Zoom tactique** : Zoomer sur les éléments importants (inputs, boutons)
4. **Cohérence temporelle** : Respecter les durées suggérées pour chaque section

---

## 🔧 OUTILS RECOMMANDÉS

| Étape | Outil | Utilisation |
|-------|-------|-------------|
| Capture | OBS Studio | Enregistrement écran + audio |
| Montage | DaVinci Resolve | Assemblage et corrections |
| Audio | Audacity | Nettoyage de la narration |
| Export | HandBrake | Compression finale MP4 |

---

**Date de création** : 10 Avril 2026  
**Version** : 1.0  
**Statut** : Prêt pour production vidéo
