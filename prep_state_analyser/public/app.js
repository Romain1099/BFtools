let currentLevel = '';
let progressionData = [];

// Variables globales
let currentConfig = null;

// Charger les niveaux au démarrage
window.onload = () => {
    loadLevels();
    loadSummary();
    loadConfiguration();
};

async function loadLevels() {
    try {
        const response = await fetch('http://localhost:3000/api/levels');
        const levels = await response.json();

        const select = document.getElementById('levelSelect');
        select.innerHTML = '<option value="">-- Choisir un niveau --</option>';

        levels.forEach(level => {
            const option = document.createElement('option');
            option.value = level;
            option.textContent = formatLevelName(level);
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des niveaux:', error);
    }
}

function formatLevelName(level) {
    const names = {
        '6eme': '6ème',
        '2nde': '2nde',
        '1ere': '1ère',
        '1ere_spe': '1ère Spé',
        'Tle': 'Terminale'
    };
    return names[level] || level;
}

async function loadProgression() {
    const select = document.getElementById('levelSelect');
    currentLevel = select.value;

    if (!currentLevel) {
        document.getElementById('progressionTable').innerHTML =
            '<div class="no-data">Sélectionnez un niveau pour afficher la progression</div>';
        document.querySelector('.btn-save').style.display = 'none';
        return;
    }

    try {
        const response = await fetch(`http://localhost:3000/api/progression/${currentLevel}`);
        progressionData = await response.json();

        displayProgression();
        document.querySelector('.btn-save').style.display = 'block';
    } catch (error) {
        console.error('Erreur lors du chargement de la progression:', error);
    }
}

function displayProgression() {
    const table = document.getElementById('progressionTable');

    if (progressionData.length === 0) {
        table.innerHTML = `
            <div class="no-data">
                Aucun chapitre pour ce niveau.
                <button onclick="addChapter()" class="btn-inline">Ajouter le premier chapitre</button>
            </div>`;
        return;
    }

    if (!currentConfig) {
        table.innerHTML = '<div class="loading">Chargement de la configuration...</div>';
        return;
    }

    // Construire le tableau dynamique basé sur la configuration
    let html = buildDynamicTable();
    table.innerHTML = html;
}

function buildDynamicTable() {
    // Construction dynamique des en-têtes
    let headerRows = buildTableHeaders();

    // Construction des lignes de données
    let bodyRows = '';
    progressionData.forEach((chapter, index) => {
        bodyRows += buildTableRow(chapter, index);
    });

    return `
        <table>
            ${headerRows}
            <tbody>
                ${bodyRows}
            </tbody>
        </table>
    `;
}

function buildTableHeaders() {
    const prepColumns = currentConfig.columns.preparation;
    const classeColumns = currentConfig.columns.classe;
    const customColumns = currentConfig.columns.custom;

    let firstRow = `
        <thead>
            <tr>
                <th rowspan="2" width="3%">#</th>
                <th rowspan="2" width="20%">Chapitre</th>
                <th rowspan="2" width="12%">📁 Dossier</th>
    `;

    // En-têtes de sections
    if (prepColumns.length > 0) {
        firstRow += `<th colspan="${prepColumns.length + 1}" class="section-header prep-header">📝 Préparation des documents</th>`;
    }
    if (classeColumns.length > 0) {
        firstRow += `<th colspan="${classeColumns.length + 1}" class="section-header classe-header">🎓 Avancement en classe</th>`;
    }
    if (customColumns.length > 0) {
        firstRow += `<th colspan="${customColumns.length}" class="section-header custom-header">⚙️ Personnalisé</th>`;
    }

    firstRow += `<th rowspan="2" width="5%">Actions</th></tr>`;

    // Deuxième ligne d'en-têtes
    let secondRow = `<tr>`;

    // Colonnes de préparation
    prepColumns.forEach(col => {
        secondRow += `<th width="8%">${col.label}</th>`;
    });
    if (prepColumns.length > 0) {
        secondRow += `<th width="10%">Progression</th>`;
    }

    // Colonnes de classe
    classeColumns.forEach(col => {
        secondRow += `<th width="8%">${col.label}</th>`;
    });
    if (classeColumns.length > 0) {
        secondRow += `<th width="10%">Progression</th>`;
    }

    // Colonnes personnalisées
    customColumns.forEach(col => {
        secondRow += `<th width="8%">${col.label}</th>`;
    });

    secondRow += `</tr></thead>`;

    return firstRow + secondRow;
}

function buildTableRow(chapter, index) {
    let row = `
        <tr>
            <td>${index + 1}</td>
            <td>
                <input type="text" class="chapter-name" value="${escapeHtml(chapter.nom || '')}"
                       onchange="updateChapter(${index}, 'nom', this.value)">
            </td>
            <td>
                ${renderFolderCell(chapter, index)}
            </td>
    `;

    // Colonnes de préparation
    const prepColumns = currentConfig.columns.preparation;
    let prepChecked = [];
    prepColumns.forEach(col => {
        const isChecked = chapter[col.id] === 'oui' || chapter[col.id] === 'true';
        prepChecked.push(isChecked);
        row += `
            <td class="prep-section">
                ${renderColumnCell(col, chapter, index, isChecked)}
            </td>
        `;
    });

    // Barre de progression préparation
    if (prepColumns.length > 0) {
        const progressPrep = calculateProgressFromArray(prepChecked);
        const progressPrepClass = getProgressClass(progressPrep);
        row += `
            <td class="prep-section">
                <div class="progress-bar">
                    <div class="progress-fill ${progressPrepClass}" style="width: ${progressPrep}%"></div>
                    <span class="progress-text">${progressPrep}%</span>
                </div>
            </td>
        `;
    }

    // Colonnes de classe
    const classeColumns = currentConfig.columns.classe;
    let classeChecked = [];
    classeColumns.forEach(col => {
        const isChecked = chapter[col.id] === 'oui' || chapter[col.id] === 'true';
        classeChecked.push(isChecked);
        row += `
            <td class="classe-section">
                ${renderColumnCell(col, chapter, index, isChecked)}
            </td>
        `;
    });

    // Barre de progression classe
    if (classeColumns.length > 0) {
        const progressClasse = calculateProgressFromArray(classeChecked);
        const progressClasseClass = getProgressClass(progressClasse);
        row += `
            <td class="classe-section">
                <div class="progress-bar">
                    <div class="progress-fill ${progressClasseClass}" style="width: ${progressClasse}%"></div>
                    <span class="progress-text">${progressClasse}%</span>
                </div>
            </td>
        `;
    }

    // Colonnes personnalisées
    const customColumns = currentConfig.columns.custom;
    customColumns.forEach(col => {
        const isChecked = chapter[col.id] === 'oui' || chapter[col.id] === 'true';
        row += `
            <td class="custom-section">
                ${renderColumnCell(col, chapter, index, isChecked)}
            </td>
        `;
    });

    row += `
            <td>
                <button onclick="removeChapter(${index})" class="btn-remove">🗑️</button>
            </td>
        </tr>
    `;

    return row;
}

function renderColumnCell(column, chapter, index, isChecked) {
    if (column.type === 'checkbox') {
        return `
            <label class="checkbox">
                <input type="checkbox" ${isChecked ? 'checked' : ''}
                       onchange="updateChapter(${index}, '${column.id}', this.checked)">
                <span class="checkmark"></span>
            </label>
        `;
    } else if (column.type === 'text') {
        return `
            <input type="text" class="column-text-input" value="${escapeHtml(chapter[column.id] || '')}"
                   onchange="updateChapter(${index}, '${column.id}', this.value)">
        `;
    } else if (column.type === 'date') {
        return `
            <input type="date" class="column-date-input" value="${chapter[column.id] || ''}"
                   onchange="updateChapter(${index}, '${column.id}', this.value)">
        `;
    }
    return '';
}

function calculateProgressFromArray(checkedArray) {
    if (checkedArray.length === 0) return 0;
    const checked = checkedArray.filter(Boolean).length;
    return Math.round((checked / checkedArray.length) * 100);
}

function getProgressClass(progress) {
    return progress === 100 ? 'complete' :
           progress >= 66 ? 'good' :
           progress >= 33 ? 'medium' : 'low';
}

function calculateProgress(cours, exercices, evaluation) {
    const total = (cours ? 1 : 0) + (exercices ? 1 : 0) + (evaluation ? 1 : 0);
    return Math.round((total / 3) * 100);
}

function updateChapter(index, field, value) {
    if (!progressionData[index]) {
        progressionData[index] = {};
    }
    progressionData[index][field] = field === 'nom' ? value : (value ? 'oui' : 'non');
    displayProgression();
}

function calculateAvancement(chapter) {
    const cours = chapter.cours === 'oui' || chapter.cours === 'true';
    const exercices = chapter.exercices === 'oui' || chapter.exercices === 'true';
    const evaluation = chapter.evaluation === 'oui' || chapter.evaluation === 'true';

    if (evaluation) return 'terminé';
    if (exercices) return 'exercices';
    if (cours) return 'cours';
    return 'non commencé';
}

function addChapter() {
    if (!currentLevel) {
        alert('Veuillez d\'abord sélectionner un niveau');
        return;
    }

    if (!currentConfig) {
        alert('Configuration non chargée');
        return;
    }

    const newChapter = {
        nom: 'Nouveau chapitre',
        dossier_sequence: ''
    };

    // Ajouter toutes les colonnes configurées avec des valeurs par défaut
    [...currentConfig.columns.preparation, ...currentConfig.columns.classe, ...currentConfig.columns.custom].forEach(col => {
        if (col.type === 'checkbox') {
            newChapter[col.id] = 'non';
        } else {
            newChapter[col.id] = '';
        }
    });

    progressionData.push(newChapter);
    displayProgression();
}

function removeChapter(index) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce chapitre ?')) {
        progressionData.splice(index, 1);
        displayProgression();
    }
}

async function saveProgression() {
    if (!currentLevel) return;

    try {
        const response = await fetch(`http://localhost:3000/api/progression/${currentLevel}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(progressionData)
        });

        if (response.ok) {
            showNotification('✅ Progression sauvegardée avec succès');
            loadSummary(); // Recharger le tableau de bord
        } else {
            showNotification('❌ Erreur lors de la sauvegarde', 'error');
        }
    } catch (error) {
        console.error('Erreur lors de la sauvegarde:', error);
        showNotification('❌ Erreur lors de la sauvegarde', 'error');
    }
}

async function loadSummary() {
    try {
        const response = await fetch('http://localhost:3000/api/summary');
        const summary = await response.json();

        displaySummary(summary);
    } catch (error) {
        console.error('Erreur lors du chargement du résumé:', error);
    }
}

function displaySummary(summary) {
    const container = document.getElementById('summaryTable');

    // Si aucun niveau n'a de progression
    if (Object.keys(summary).length === 0) {
        container.innerHTML = `
            <div class="no-data">
                <p>Aucun niveau avec des données de progression.</p>
                <p>Sélectionnez un niveau dans l'onglet "Gestion des Progressions" pour commencer.</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="summary-grid">
    `;

    for (const [level, stats] of Object.entries(summary)) {
        // Calcul des progressions séparées
        const progressPrep = Math.round(((stats.prepCoursComplete + stats.prepExercicesComplete + stats.prepEvaluationComplete) / (stats.total * 3)) * 100);
        const progressClasse = Math.round(((stats.classeCoursComplete + stats.classeExercicesComplete + stats.classeEvaluationComplete) / (stats.total * 3)) * 100);

        const prepClass = progressPrep === 100 ? 'complete' :
                         progressPrep >= 66 ? 'good' :
                         progressPrep >= 33 ? 'medium' : 'low';

        const classeClass = progressClasse === 100 ? 'complete' :
                           progressClasse >= 66 ? 'good' :
                           progressClasse >= 33 ? 'medium' : 'low';

        html += `
            <div class="level-card">
                <h3>${formatLevelName(level)}</h3>
                <div class="stats">
                    <div class="stat-header">
                        <span class="chapter-count">${stats.total} chapitres</span>
                    </div>

                    <div class="progress-section">
                        <div class="progress-label">
                            <span>📝 Préparation</span>
                            <span class="progress-detail">${stats.prepCoursComplete + stats.prepExercicesComplete + stats.prepEvaluationComplete}/${stats.total * 3}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill ${prepClass}" style="width: ${progressPrep}%"></div>
                            <span class="progress-text">${progressPrep}%</span>
                        </div>
                    </div>

                    <div class="progress-section">
                        <div class="progress-label">
                            <span>🎓 En classe</span>
                            <span class="progress-detail">${stats.classeCoursComplete + stats.classeExercicesComplete + stats.classeEvaluationComplete}/${stats.total * 3}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill ${classeClass}" style="width: ${progressClasse}%"></div>
                            <span class="progress-text">${progressClasse}%</span>
                        </div>
                    </div>
                </div>
                <button onclick="selectLevelAndShowProgression('${level}')" class="btn-view">
                    👁️ Voir les détails
                </button>
            </div>
        `;
    }

    html += '</div>';
    container.innerHTML = html;
}

function selectLevelAndShowProgression(level) {
    document.getElementById('levelSelect').value = level;
    loadProgression();
    showTab('progression');
}

function showTab(tabName) {
    // Masquer tous les contenus
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Masquer tous les boutons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Afficher le contenu sélectionné
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Activer le bouton correspondant
    event.target.classList.add('active');

    // Recharger les données si nécessaire
    if (tabName === 'dashboard') {
        loadSummary();
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Notifications plus longues pour les infos importantes
    const duration = type === 'info' ? 8000 : 3000;

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, duration);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderFolderCell(chapter, index) {
    const folder = chapter.dossier_sequence || '';

    if (folder && folder !== 'non' && folder !== '') {
        // Extraire juste le nom du dossier pour l'affichage
        const folderName = folder.includes('\\') ? folder.split('\\').pop() : folder;

        return `
            <div class="folder-cell">
                <span class="folder-name" title="${escapeHtml(folder)}">${escapeHtml(folderName)}</span>
                <div class="folder-actions">
                    <button class="btn-folder-open" onclick="openFolder('${folder.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}')" title="Ouvrir le dossier">📂</button>
                    <button class="btn-folder-link" onclick="showFolderSelector(${index})" title="Changer le dossier">🔗</button>
                </div>
            </div>
        `;
    } else {
        return `
            <div class="folder-cell no-folder">
                <button class="btn-folder-link" onclick="showFolderSelector(${index})">🔗 Lier un dossier</button>
            </div>
        `;
    }
}

// Rendre les fonctions globales pour les événements onclick
window.showFolderSelector = function(chapterIndex) {
    const chapter = progressionData[chapterIndex];

    // Créer une modal simple pour confirmation
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Sélectionner le dossier de séquence</h3>
            <p>Chapitre : <strong>${escapeHtml(chapter.nom)}</strong></p>

            <div class="folder-input-section">
                <p>Chemin du dossier :</p>
                <input type="text" id="folderPathInput" class="folder-path-input"
                       value="${chapter.dossier_sequence || ''}"
                       placeholder="Tapez ou collez le chemin du dossier...">

                ${chapter.dossier_sequence ? `
                    <div class="folder-buttons">
                        <button onclick="clearFolder(${chapterIndex})" class="btn-clear">
                            🗑️ Supprimer le lien
                        </button>
                    </div>
                ` : ''}
            </div>

            <div class="modal-actions">
                <button onclick="saveFolderPath(${chapterIndex})" class="btn-confirm">✅ Valider</button>
                <button onclick="closeModal()" class="btn-cancel">❌ Annuler</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

// Fonction pour sélectionner un dossier avec boîte de dialogue native Windows
window.browseFolderManual = async function() {
    try {
        showNotification('📂 Ouverture de la boîte de dialogue...', 'info');

        // Appeler le serveur pour ouvrir la boîte de dialogue native
        const response = await fetch('http://localhost:3000/api/select-folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const result = await response.json();

        if (result.success && result.folderPath) {
            // Mettre à jour le champ de texte avec le chemin sélectionné
            document.getElementById('folderPathInput').value = result.folderPath;
            showNotification('✅ Dossier sélectionné : ' + result.folderPath.split('\\').pop(), 'success');
        } else if (result.cancelled) {
            showNotification('❌ Sélection annulée', 'error');
        } else {
            showNotification('❌ Aucun dossier sélectionné', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('❌ Erreur lors de l\'ouverture de la boîte de dialogue', 'error');
    }
}

// Fonction pour sauvegarder le chemin du dossier
window.saveFolderPath = function(chapterIndex) {
    const folderPath = document.getElementById('folderPathInput').value.trim();
    // Stocker le chemin directement, pas "oui"/"non"
    progressionData[chapterIndex].dossier_sequence = folderPath;

    if (folderPath) {
        showNotification('📁 Dossier lié avec succès');
    } else {
        showNotification('📁 Lien supprimé');
    }
    closeModal();
    displayProgression();
}

// Fonction pour supprimer le lien du dossier
window.clearFolder = function(chapterIndex) {
    document.getElementById('folderPathInput').value = '';
}

window.selectFolder = function(chapterIndex, folderPath) {
    if (folderPath) {
        updateChapter(chapterIndex, 'dossier_sequence', folderPath);
    }
    closeModal();
}

window.closeModal = function() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

window.openFolder = async function(folderPath) {
    if (!folderPath) return;

    try {
        await fetch('http://localhost:3000/api/open-folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ folderPath })
        });
    } catch (error) {
        console.error('Erreur lors de l\'ouverture du dossier:', error);
    }
}

// Fonctions de configuration
async function loadConfiguration() {
    try {
        const response = await fetch('http://localhost:3000/api/config');
        currentConfig = await response.json();
        displayConfiguration();
    } catch (error) {
        console.error('Erreur lors du chargement de la configuration:', error);
    }
}

function displayConfiguration() {
    if (!currentConfig) return;

    // Afficher les colonnes de préparation
    const prepContainer = document.getElementById('prepColumns');
    if (prepContainer) {
        prepContainer.innerHTML = '';
        currentConfig.columns.preparation.forEach((col, index) => {
            prepContainer.appendChild(createColumnItem(col, 'preparation', index));
        });
    }

    // Afficher les colonnes de classe
    const classeContainer = document.getElementById('classeColumns');
    if (classeContainer) {
        classeContainer.innerHTML = '';
        currentConfig.columns.classe.forEach((col, index) => {
            classeContainer.appendChild(createColumnItem(col, 'classe', index));
        });
    }

    // Afficher les colonnes personnalisées
    const customContainer = document.getElementById('customColumns');
    if (customContainer) {
        customContainer.innerHTML = '';
        currentConfig.columns.custom.forEach((col, index) => {
            customContainer.appendChild(createColumnItem(col, 'custom', index));
        });
    }
}

function createColumnItem(column, category, index) {
    const div = document.createElement('div');
    div.className = 'column-item';
    div.innerHTML = `
        <div class="column-info">
            <input type="text" value="${column.label}" onchange="updateColumnLabel('${category}', ${index}, this.value)" class="column-label-input">
            <span class="column-type">(${column.type})</span>
        </div>
        <div class="column-actions">
            ${!column.required ? `<button onclick="removeColumn('${category}', ${index})" class="btn-remove-column">🗑️</button>` : ''}
        </div>
    `;
    return div;
}

window.addCustomColumn = function(category) {
    const columnName = prompt('Nom de la nouvelle colonne :');
    if (!columnName) return;

    const columnType = prompt('Type de colonne (checkbox/text/date):', 'checkbox');
    if (!columnType) return;

    const newColumn = {
        id: columnName.toLowerCase().replace(/\s+/g, '_'),
        label: columnName,
        type: columnType,
        category: category,
        required: false
    };

    if (category === 'custom') {
        currentConfig.columns.custom.push(newColumn);
    } else {
        currentConfig.columns[category].push(newColumn);
    }

    displayConfiguration();
    showNotification('✅ Colonne ajoutée');
}

window.removeColumn = function(category, index) {
    if (confirm('Supprimer cette colonne ?')) {
        currentConfig.columns[category].splice(index, 1);
        displayConfiguration();
        showNotification('✅ Colonne supprimée');
    }
}

function updateColumnLabel(category, index, newLabel) {
    currentConfig.columns[category][index].label = newLabel;
}

window.saveConfiguration = async function() {
    try {
        const response = await fetch('http://localhost:3000/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentConfig)
        });

        if (response.ok) {
            showNotification('✅ Configuration sauvegardée avec succès');
        } else {
            showNotification('❌ Erreur lors de la sauvegarde', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('❌ Erreur lors de la sauvegarde', 'error');
    }
}

window.resetConfiguration = async function() {
    if (confirm('Réinitialiser la configuration aux valeurs par défaut ?')) {
        try {
            const response = await fetch('http://localhost:3000/api/config/reset', {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                currentConfig = result.config;
                displayConfiguration();
                showNotification('✅ Configuration réinitialisée');
            } else {
                showNotification('❌ Erreur lors de la réinitialisation', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            showNotification('❌ Erreur lors de la réinitialisation', 'error');
        }
    }
}