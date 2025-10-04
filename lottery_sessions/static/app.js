/**
 * Application principale - Lottery Sessions
 * Gestion de l'interface et communication avec le backend Flask
 */

// Configuration globale
const CONFIG = {
    apiBaseUrl: '',  // Vide car on est sur le même domaine
    currentClass: null,
    currentDate: new Date().toISOString().split('T')[0],
    students: [],
    historyMode: true,
    drawMode: 'without_replacement',  // 'without_replacement' ou 'with_replacement'
    winnersToScore: []
};

// État de l'application
const state = {
    isDrawing: false,
    currentWinners: [],
    gameState: 'idle'  // idle, drawing, exhausted
};

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupWindowCloseHandler();
});

/**
 * Initialise l'application
 */
async function initializeApp() {
    showLoading(true);

    // Charger la liste des classes
    await loadClasses();

    // Configurer les event listeners
    setupEventListeners();

    // Mettre à jour la date
    document.getElementById('session-date').textContent = formatDate(CONFIG.currentDate);

    showLoading(false);
}

/**
 * Configure tous les event listeners
 */
function setupEventListeners() {
    // Sidebar
    document.getElementById('sidebar-toggle').addEventListener('click', toggleSidebar);
    document.getElementById('change-class-btn').addEventListener('click', showClassSelector);

    // Sélecteur de classe
    document.getElementById('create-class-btn').addEventListener('click', createNewClass);
    document.getElementById('import-class-btn').addEventListener('click', importClass);

    // Modal d'import
    document.getElementById('validate-import-btn').addEventListener('click', validateAndImportClass);
    document.getElementById('cancel-import-btn').addEventListener('click', cancelImport);
    document.getElementById('browse-file-btn').addEventListener('click', () => {
        document.getElementById('file-input').click();
    });
    document.getElementById('file-input').addEventListener('change', handleFileSelection);

    // Modes et paramètres
    document.getElementById('draw-mode-switch').addEventListener('change', handleDrawModeChange);
    document.getElementById('history-mode-switch').addEventListener('change', handleHistoryModeChange);
    document.getElementById('winners-count').addEventListener('input', handleWinnersCountChange);
    document.getElementById('confetti-switch').addEventListener('change', handleConfettiToggle);

    // Boutons de sélection
    document.getElementById('select-all').addEventListener('click', selectAllStudents);
    document.getElementById('deselect-all').addEventListener('click', deselectAllStudents);

    // Bouton de tirage
    document.getElementById('draw-button').addEventListener('click', performDraw);

    // Bouton reset cycle
    document.getElementById('reset-cycle-btn').addEventListener('click', resetCycle);

    // Bouton Quitter
    document.getElementById('quit-app-btn').addEventListener('click', quitApplication);

    // Panel de notation
    document.querySelectorAll('.score-btn').forEach(btn => {
        btn.addEventListener('click', (e) => handleScoring(e.currentTarget.dataset.score));
    });
    document.getElementById('skip-scoring').addEventListener('click', skipScoring);

    // Fermeture de la sidebar au clic extérieur
    document.addEventListener('click', (e) => {
        const sidebar = document.getElementById('sidebar');
        const toggle = document.getElementById('sidebar-toggle');
        if (!sidebar.contains(e.target) && !toggle.contains(e.target) && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
        }
    });
}

/**
 * Charge la liste des classes disponibles
 */
async function loadClasses() {
    try {
        const response = await fetch('/api/classes');
        const data = await response.json();

        if (data.success) {
            displayClasses(data.classes);

            // Si aucune classe, afficher le sélecteur
            if (data.classes.length === 0) {
                showClassSelector();
            } else if (data.classes.length === 1) {
                // Charger automatiquement s'il n'y a qu'une classe
                selectClass(data.classes[0]);
            } else {
                // Essayer de recharger la dernière classe sélectionnée
                const lastClass = localStorage.getItem('lastSelectedClass');
                if (lastClass && data.classes.includes(lastClass)) {
                    selectClass(lastClass);
                } else {
                    // Afficher le sélecteur pour choisir
                    showClassSelector();
                }
            }
        }
    } catch (error) {
        console.error('Erreur lors du chargement des classes:', error);
        showError('Impossible de charger les classes');
    }
}

/**
 * Affiche la liste des classes dans le sélecteur
 */
function displayClasses(classes) {
    const classList = document.getElementById('class-list');
    classList.innerHTML = '';

    if (classes.length === 0) {
        classList.innerHTML = '<p>Aucune classe disponible. Créez ou importez une classe.</p>';
        return;
    }

    classes.forEach(className => {
        const classItem = document.createElement('div');
        classItem.className = 'class-item';
        classItem.innerHTML = `
            <div class="class-info">
                <span class="class-name">${className}</span>
                <span class="class-stats">Cliquez pour sélectionner</span>
            </div>
        `;
        classItem.addEventListener('click', () => selectClass(className));
        classList.appendChild(classItem);
    });
}

/**
 * Sélectionne une classe et charge ses données
 */
async function selectClass(className) {
    CONFIG.currentClass = className;
    document.getElementById('current-class-name').textContent = className;

    // Sauvegarder dans localStorage pour recharger au reload
    localStorage.setItem('lastSelectedClass', className);

    // Masquer le sélecteur
    document.getElementById('class-selector').classList.remove('active');

    // Charger les étudiants
    await loadStudents();

    // Mettre à jour l'affichage
    updateDisplay();
    updateCycleProgress();
    checkDrawButtonState();
}

/**
 * Charge les étudiants de la classe courante
 */
async function loadStudents() {
    if (!CONFIG.currentClass) return;

    showLoading(true);

    try {
        const response = await fetch(`/api/students/${CONFIG.currentClass}`);
        const data = await response.json();

        if (data.success) {
            CONFIG.students = data.students;
            displayStudents();
            updateSessionStats();
        }
    } catch (error) {
        console.error('Erreur lors du chargement des étudiants:', error);
        showError('Impossible de charger les étudiants');
    } finally {
        showLoading(false);
    }
}

/**
 * Affiche la liste des étudiants dans la sidebar
 */
function displayStudents() {
    const peopleList = document.getElementById('people-list');
    peopleList.innerHTML = '';

    CONFIG.students.forEach(student => {
        const studentRow = document.createElement('div');
        studentRow.className = 'student-row';

        // Vérifier si l'étudiant a déjà été interrogé dans le cycle
        const alreadyQuestionedInCycle = hasBeenQuestionedInCycle(student);

        if (alreadyQuestionedInCycle) {
            studentRow.classList.add('already-questioned');
        }

        // Déterminer si la checkbox doit être cochée selon le mode historique
        let isChecked = true;
        if (CONFIG.historyMode && alreadyQuestionedInCycle) {
            isChecked = false;
        }

        // Récupérer le score du jour
        const todayScore = student[CONFIG.currentDate];
        let scoreValue = '';
        if (todayScore !== null && todayScore !== undefined) {
            scoreValue = todayScore;
        }

        studentRow.innerHTML = `
            <label class="student-checkbox">
                <input type="checkbox" value="${student.full_name}" ${isChecked ? 'checked' : ''}>
                <span class="student-name">${student.full_name}</span>
            </label>
            <div class="score-input-container">
                <input type="number"
                       class="score-input"
                       min="0" max="3"
                       value="${scoreValue}"
                       placeholder="-"
                       data-student="${student.full_name}"
                       title="Score: 0=Erreur, 1=Partiel, 2=Correct, 3=Excellent">
            </div>
        `;

        studentRow.querySelector('input[type="checkbox"]').addEventListener('change', handleStudentCheckChange);
        studentRow.querySelector('.score-input').addEventListener('change', handleScoreChange);
        peopleList.appendChild(studentRow);
    });
}

/**
 * Gère le changement de score d'un étudiant
 */
async function handleScoreChange(event) {
    const input = event.target;
    const studentName = input.dataset.student;
    const score = input.value;

    // Valider le score (0-3 ou vide)
    if (score !== '' && (isNaN(score) || score < 0 || score > 3)) {
        showError('Le score doit être entre 0 et 3');
        input.value = '';
        return;
    }

    try {
        if (score === '') {
            // Score vide = pas encore interrogé, on ne fait rien
            return;
        }

        // Mettre à jour via l'API
        const response = await fetch('/api/score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                class_name: CONFIG.currentClass,
                student_name: studentName,
                score: parseInt(score),
                date: CONFIG.currentDate
            })
        });

        const result = await response.json();
        if (!result.success) {
            // Afficher l'erreur détaillée du serveur
            showError(result.error || 'Erreur lors de la sauvegarde du score');
            return;
        }

        // Mettre à jour les données locales
        const studentData = CONFIG.students.find(s => s.full_name === studentName);
        if (studentData) {
            studentData[CONFIG.currentDate] = parseInt(score);
        }

        // Mettre à jour les statistiques
        updateSessionStats();
        await updateCycleProgress();

        // Réafficher la liste pour mettre à jour le statut
        displayStudents();
        updateDisplay(); // Mettre à jour les badges si nécessaire

    } catch (error) {
        console.error('Erreur lors de la mise à jour du score:', error);
        showError('Erreur réseau: impossible de contacter le serveur');
    }
}

/**
 * Gère le changement d'état d'une checkbox étudiant
 */
function handleStudentCheckChange() {
    updateDisplay();
    checkDrawButtonState();
}

/**
 * Met à jour l'affichage des étiquettes
 */
function updateDisplay() {
    const nameContainer = document.getElementById('name-container');
    const checkedStudents = getCheckedStudents();
    const existingTags = Array.from(nameContainer.children);
    const existingPeople = existingTags.map(tag => tag.textContent);

    // Supprimer les étiquettes qui ne sont plus cochées
    existingTags.forEach(tag => {
        if (!checkedStudents.includes(tag.textContent)) {
            tag.style.transition = 'all 0.3s ease-out';
            tag.style.opacity = '0';
            tag.style.transform = 'scale(0.8)';
            setTimeout(() => tag.remove(), 300);
        }
    });

    // Ajouter les nouvelles étiquettes
    checkedStudents.forEach((studentName, index) => {
        if (!existingPeople.includes(studentName)) {
            const tag = document.createElement('div');
            tag.className = 'person-tag';
            tag.textContent = studentName;

            // Position aléatoire
            const position = getRandomPosition(tag);
            tag.style.left = `${position.x}px`;
            tag.style.top = `${position.y}px`;

            // Animation d'entrée
            tag.style.opacity = '0';
            tag.style.transform = 'scale(0.8)';
            nameContainer.appendChild(tag);

            setTimeout(() => {
                tag.style.transition = 'all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
                tag.style.opacity = '1';
                tag.style.transform = 'scale(1)';
            }, 100);
        }
    });
}

/**
 * Effectue le tirage au sort
 */
async function performDraw() {
    if (state.isDrawing || state.gameState === 'exhausted') return;

    // Réinitialiser les classes des tags avant le nouveau tirage
    const existingTags = document.querySelectorAll('.person-tag');
    existingTags.forEach(tag => {
        tag.classList.remove('winner', 'fade-out', 'highlight', 'shuffling', 'spinning');
        tag.style.opacity = '1';
        tag.style.transform = 'scale(1)';
        tag.style.filter = '';
        tag.style.zIndex = '10';
        // Réinitialiser les styles CSS (laisser les classes CSS gérer l'apparence)
        tag.style.background = '';
        tag.style.color = '';
    });

    const checkedStudents = getCheckedStudents();
    const winnersCount = parseInt(document.getElementById('winners-count').value);

    if (checkedStudents.length < winnersCount) {
        showError(`Il faut au moins ${winnersCount} participant(s)`);
        return;
    }

    state.isDrawing = true;
    state.gameState = 'drawing';
    document.getElementById('draw-button').disabled = true;
    document.getElementById('draw-button').textContent = '🎲 Tirage en cours...';

    // Fermer la sidebar
    document.getElementById('sidebar').classList.remove('open');

    // Lancer l'animation
    const tags = Array.from(document.querySelectorAll('.person-tag'));
    startShuffleAnimation(tags, () => {
        selectWinners(checkedStudents, winnersCount);
    });
}

/**
 * Sélectionne les gagnants
 */
async function selectWinners(candidates, count) {
    const winners = [];
    const availableCandidates = [...candidates];

    for (let i = 0; i < count; i++) {
        const winnerIndex = Math.floor(Math.random() * availableCandidates.length);
        winners.push(availableCandidates[winnerIndex]);

        if (CONFIG.drawMode === 'without_replacement') {
            availableCandidates.splice(winnerIndex, 1);
        }
    }

    state.currentWinners = winners;
    CONFIG.winnersToScore = [...winners];

    // Animer les gagnants
    animateWinners(winners);

    // Si mode sans remise et avec historique, décocher les gagnants
    if (CONFIG.drawMode === 'without_replacement' && CONFIG.historyMode) {
        winners.forEach(winner => {
            const checkbox = document.querySelector(`#people-list input[value="${winner}"]`);
            if (checkbox) {
                checkbox.checked = false;
            }
        });
    }

    // Enregistrer le tirage
    for (const winner of winners) {
        await recordDraw(winner);
    }

    // Mettre à jour la progression du cycle après enregistrement
    await updateCycleProgress();

    // Afficher le panel de notation après l'animation
    setTimeout(() => {
        showScoringPanel();
        state.isDrawing = false;
        checkDrawButtonState();
    }, 2000);
}

/**
 * Enregistre un tirage au sort
 */
async function recordDraw(studentName) {
    try {
        await fetch('/api/draw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                class_name: CONFIG.currentClass,
                student_name: studentName,
                date: CONFIG.currentDate
            })
        });
    } catch (error) {
        console.error('Erreur lors de l\'enregistrement du tirage:', error);
    }
}

/**
 * Affiche le panel de notation
 */
function showScoringPanel() {
    if (CONFIG.winnersToScore.length === 0) {
        hideScoringPanel();
        return;
    }

    const student = CONFIG.winnersToScore[0];
    document.getElementById('student-to-score').textContent = student;
    document.getElementById('scoring-panel').classList.add('visible');
}

/**
 * Gère la notation d'un étudiant
 */
async function handleScoring(score) {
    const student = CONFIG.winnersToScore.shift();

    try {
        await fetch('/api/score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                class_name: CONFIG.currentClass,
                student_name: student,
                score: parseInt(score),
                date: CONFIG.currentDate
            })
        });

        // Mettre à jour l'affichage local
        const studentData = CONFIG.students.find(s => s.full_name === student);
        if (studentData) {
            studentData[CONFIG.currentDate] = score;
        }

        // Passer au suivant ou fermer
        if (CONFIG.winnersToScore.length > 0) {
            showScoringPanel();
        } else {
            hideScoringPanel();
            await loadStudents();  // Recharger pour mettre à jour
            updateDisplay(); // Mettre à jour l'affichage des badges
            await updateCycleProgress(); // Mettre à jour la progression
        }
    } catch (error) {
        console.error('Erreur lors de la notation:', error);
        showError('Erreur lors de l\'enregistrement de la note');
    }
}

/**
 * Passe la notation d'un étudiant
 */
function skipScoring() {
    CONFIG.winnersToScore.shift();

    if (CONFIG.winnersToScore.length > 0) {
        showScoringPanel();
    } else {
        hideScoringPanel();
    }
}

/**
 * Cache le panel de notation
 */
function hideScoringPanel() {
    document.getElementById('scoring-panel').classList.remove('visible');

    // Mettre à jour l'affichage si mode sans remise pour supprimer les badges des gagnants
    if (CONFIG.drawMode === 'without_replacement' && CONFIG.historyMode) {
        updateDisplay();
    }
}

/**
 * Met à jour les statistiques de session
 */
function updateSessionStats() {
    let totalScore = 0;
    let scoredCount = 0; // Seulement ceux qui ont une note aujourd'hui

    CONFIG.students.forEach(student => {
        const score = student[CONFIG.currentDate];
        // Compter seulement les étudiants qui ont une vraie note aujourd'hui
        if (score !== null && score !== undefined && score !== '') {
            const numScore = parseInt(score);
            if (!isNaN(numScore)) {
                totalScore += numScore;
                scoredCount++;
            }
        }
    });

    // Afficher le nombre d'élèves notés aujourd'hui sur le total
    document.getElementById('students-questioned').textContent = `${scoredCount}/${CONFIG.students.length}`;

    // Calculer la moyenne seulement sur les élèves qui ont une note
    if (scoredCount > 0) {
        const average = (totalScore / scoredCount).toFixed(1);
        document.getElementById('average-score').textContent = `${average}/3`;
    } else {
        document.getElementById('average-score').textContent = '--/3';
    }
}

// Fonctions utilitaires

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

function showClassSelector() {
    document.getElementById('class-selector').classList.add('active');
}

function getCheckedStudents() {
    return Array.from(document.querySelectorAll('#people-list input:checked'))
        .map(cb => cb.value);
}

function getRandomPosition(element) {
    const margin = 60;
    const containerWidth = window.innerWidth;
    const containerHeight = window.innerHeight;

    const x = margin + Math.random() * (containerWidth - 2 * margin - 200);
    const y = margin + Math.random() * (containerHeight - 2 * margin - 200);

    return { x, y };
}

function checkDrawButtonState() {
    const checkedCount = getCheckedStudents().length;
    const winnersCount = parseInt(document.getElementById('winners-count').value);
    const drawButton = document.getElementById('draw-button');

    if (checkedCount < winnersCount) {
        drawButton.disabled = true;
        drawButton.textContent = `🎲 Il faut au moins ${winnersCount} participant(s)`;
    } else {
        drawButton.disabled = false;
        drawButton.textContent = '🎲 Tirage au sort';
    }
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.toggle('active', show);
}

function showError(message) {
    // TODO: Implémenter une notification d'erreur plus élégante
    alert(message);
}

/**
 * Arrête le serveur quand la fenêtre se ferme
 */
function setupWindowCloseHandler() {
    window.addEventListener('beforeunload', () => {
        // Envoyer une requête synchrone pour arrêter le serveur
        // Note: on utilise sendBeacon qui est fait pour ça
        navigator.sendBeacon('/api/shutdown');
    });
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Gestionnaires d'événements pour les modes

function handleDrawModeChange() {
    CONFIG.drawMode = document.getElementById('draw-mode-switch').checked ?
        'without_replacement' : 'with_replacement';
}

function handleHistoryModeChange() {
    CONFIG.historyMode = document.getElementById('history-mode-switch').checked;
    displayStudents();  // Rafraîchir l'affichage
    updateDisplay();
}

function handleWinnersCountChange() {
    document.getElementById('winners-count-display').textContent =
        document.getElementById('winners-count').value;
    checkDrawButtonState();
}

function handleConfettiToggle() {
    // La gestion des confettis est dans animations.js
}

function selectAllStudents() {
    document.querySelectorAll('#people-list input[type="checkbox"]').forEach(cb => {
        cb.checked = true;
    });
    updateDisplay();
    checkDrawButtonState();
}

function deselectAllStudents() {
    document.querySelectorAll('#people-list input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    updateDisplay();
    checkDrawButtonState();
}

// Fonctions pour créer/importer des classes

async function createNewClass() {
    const className = prompt('Nom de la nouvelle classe:');
    if (!className) return;

    const studentsText = prompt('Entrez les étudiants (format: Nom Prénom, un par ligne):');
    if (!studentsText) return;

    const students = studentsText.split('\n')
        .filter(line => line.trim())
        .map(line => {
            const parts = line.trim().split(' ');
            return {
                nom: parts[0] || '',
                prenom: parts.slice(1).join(' ') || ''
            };
        });

    try {
        const response = await fetch('/api/create_class', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ class_name: className, students })
        });

        if (response.ok) {
            await loadClasses();
            selectClass(className);
        }
    } catch (error) {
        showError('Erreur lors de la création de la classe');
    }
}

/**
 * Gère la sélection d'un fichier via l'explorateur
 */
function handleFileSelection(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('import-file-path').value = file.name;
        // Stocker le fichier pour l'upload
        CONFIG.selectedFile = file;
    }
}

async function importClass() {
    // Afficher le modal d'import
    document.getElementById('class-selector').classList.remove('active');
    document.getElementById('import-modal').classList.add('active');

    // Réinitialiser le formulaire
    document.getElementById('import-class-name').value = '';
    document.getElementById('import-file-path').value = '';
    document.getElementById('file-input').value = '';
    CONFIG.selectedFile = null;
    hideValidationMessage();
}

/**
 * Valide et importe une classe depuis un CSV
 */
async function validateAndImportClass() {
    let className = document.getElementById('import-class-name').value.trim();
    const file = CONFIG.selectedFile;

    // Validation basique côté client
    if (!className) {
        showValidationMessage('Veuillez entrer un nom de classe', 'error');
        return;
    }

    if (!file) {
        showValidationMessage('Veuillez sélectionner un fichier CSV', 'error');
        return;
    }

    // Normaliser le nom de classe : ajouter "classe_" si absent
    if (!className.startsWith('classe_')) {
        className = 'classe_' + className;
    }

    // Désactiver le bouton pendant l'import
    const importBtn = document.getElementById('validate-import-btn');
    importBtn.disabled = true;
    importBtn.textContent = '⏳ Import en cours...';

    try {
        // Lire le contenu du fichier
        const fileContent = await file.text();

        // Envoyer le contenu au serveur
        const response = await fetch('/api/import_class', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                class_name: className,
                file_content: fileContent
            })
        });

        const result = await response.json();

        if (result.success) {
            showValidationMessage(
                result.message || 'Import réussi ! Classe créée avec succès.',
                'success'
            );

            // Attendre 2 secondes puis recharger les classes
            setTimeout(async () => {
                document.getElementById('import-modal').classList.remove('active');
                await loadClasses();
                selectClass(className);
            }, 2000);
        } else {
            // Afficher l'erreur détaillée du serveur
            showValidationMessage(result.error, 'error');
            importBtn.disabled = false;
            importBtn.textContent = '✓ Valider et importer';
        }
    } catch (error) {
        console.error('Erreur lors de l\'import:', error);
        showValidationMessage(
            'Erreur réseau : impossible de contacter le serveur',
            'error'
        );
        importBtn.disabled = false;
        importBtn.textContent = '✓ Valider et importer';
    }
}

/**
 * Affiche un message de validation
 */
function showValidationMessage(message, type) {
    const messageDiv = document.getElementById('import-validation-message');
    messageDiv.textContent = message;
    messageDiv.className = `validation-message ${type}`;
    messageDiv.classList.remove('hidden');
}

/**
 * Cache le message de validation
 */
function hideValidationMessage() {
    const messageDiv = document.getElementById('import-validation-message');
    messageDiv.classList.add('hidden');
}

/**
 * Annule l'import et ferme le modal
 */
function cancelImport() {
    document.getElementById('import-modal').classList.remove('active');
    document.getElementById('class-selector').classList.add('active');
}

// Fonctions pour la gestion des cycles

/**
 * Obtient les champs de date du cycle actuel (après le dernier NEW_CYCLE)
 */
function getCurrentCycleFields(student) {
    const allFields = Object.keys(student);

    // Trouver tous les marqueurs NEW_CYCLE (exactement "NEW_CYCLE")
    const newCycleIndices = [];
    allFields.forEach((field, index) => {
        if (field === 'NEW_CYCLE') {
            newCycleIndices.push(index);
        }
    });

    // Si pas de NEW_CYCLE, retourner toutes les dates
    if (newCycleIndices.length === 0) {
        return allFields.filter(f => isDateField(f));
    }

    // Sinon, retourner les dates après le dernier NEW_CYCLE
    const lastCycleIndex = Math.max(...newCycleIndices);
    const dateFields = [];
    allFields.forEach((field, index) => {
        if (index > lastCycleIndex && isDateField(field)) {
            dateFields.push(field);
        }
    });

    return dateFields;
}

/**
 * Vérifie si un étudiant a été interrogé dans le cycle actuel
 */
function hasBeenQuestionedInCycle(student) {
    const cycleFields = getCurrentCycleFields(student);

    for (const field of cycleFields) {
        if (student[field] !== null && student[field] !== undefined && student[field] !== '') {
            return true;
        }
    }
    return false;
}

/**
 * Vérifie si un champ est une date
 */
function isDateField(field) {
    try {
        const date = new Date(field);
        return !isNaN(date.getTime()) && field.match(/^\d{4}-\d{2}-\d{2}$/);
    } catch {
        return false;
    }
}

/**
 * Met à jour la progression du cycle
 */
async function updateCycleProgress() {
    if (!CONFIG.currentClass) return;

    try {
        const response = await fetch(`/api/cycle_progress/${CONFIG.currentClass}`);
        const data = await response.json();

        if (data.success) {
            const progress = data.progress;

            // Mettre à jour la barre de progression
            document.getElementById('progress-fill').style.width = `${progress.progress_percent}%`;
            document.getElementById('progress-text').textContent = `${progress.questioned}/${progress.total} élèves`;
            document.getElementById('remaining-students').textContent = progress.remaining;

            // Afficher le bouton de reset si le cycle est complet
            const resetBtn = document.getElementById('reset-cycle-btn');
            if (data.is_complete && CONFIG.historyMode) {
                resetBtn.classList.remove('hidden');
            } else {
                resetBtn.classList.add('hidden');
            }
        }
    } catch (error) {
        console.error('Erreur lors de la mise à jour de la progression:', error);
    }
}

/**
 * Remet à zéro le cycle (nouveau cycle)
 */
async function resetCycle() {
    if (!CONFIG.currentClass) return;

    const confirm = window.confirm(
        'Démarrer un nouveau cycle ?\n\n' +
        'Tous les élèves redeviendront disponibles pour un nouveau cycle d\'interrogations.\n' +
        'L\'historique sera conservé.'
    );

    if (!confirm) return;

    try {
        const response = await fetch(`/api/reset_cycle/${CONFIG.currentClass}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            // Nettoyer TOUS les badges existants avant de recharger
            const nameContainer = document.getElementById('name-container');
            nameContainer.innerHTML = '';

            // Recharger COMPLETEMENT les données et l'affichage
            await loadStudents();

            // Recréer les badges visuels en fonction des checkboxes
            updateDisplay();

            // Mettre à jour la progression
            await updateCycleProgress();

            // Vérifier l'état du bouton
            checkDrawButtonState();

            // Message de confirmation
            showNotification(data.message || 'Nouveau cycle démarré ! Tous les élèves sont à nouveau disponibles.');
        } else {
            showError(data.error || 'Erreur lors du reset du cycle');
        }
    } catch (error) {
        console.error('Erreur lors du reset du cycle:', error);
        showError('Erreur lors du reset du cycle');
    }
}

/**
 * Affiche une notification temporaire
 */
function showNotification(message) {
    // Créer une notification temporaire
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--primary-color);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-lg);
        z-index: 10001;
        transition: all 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Supprimer après 3 secondes
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Quitte l'application en arrêtant le serveur
 */
async function quitApplication() {
    const confirm = window.confirm(
        'Voulez-vous vraiment quitter l\'application ?\n\n' +
        'Le serveur sera arrêté et l\'application se fermera.'
    );

    if (!confirm) return;

    try {
        // Arrêter le serveur
        await fetch('/api/shutdown', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        // Afficher un message de fermeture
        document.body.innerHTML = `
            <div style="display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div style="text-align: center; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);">
                    <h1 style="color: #1e293b; margin-bottom: 1rem;">🚪 Application fermée</h1>
                    <p style="color: #64748b;">Le serveur a été arrêté avec succès.</p>
                    <p style="color: #64748b; font-size: 0.9rem; margin-top: 1rem;">Vous pouvez maintenant fermer cette page.</p>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Erreur lors de l\'arrêt du serveur:', error);
        showError('Impossible d\'arrêter le serveur');
    }
}

// Mettre à jour l'affichage quand on change le mode historique
function handleHistoryModeChange() {
    CONFIG.historyMode = document.getElementById('history-mode-switch').checked;
    displayStudents();  // Rafraîchir l'affichage
    updateDisplay();
    updateCycleProgress();
}