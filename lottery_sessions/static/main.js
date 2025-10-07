/**
 * APPLICATION PRINCIPALE - Lottery Sessions
 * Point d'entrée orchestrant tous les modules
 */

import { CONFIG, Storage } from './modules/state.js';
import { UI } from './modules/ui.js';
import { Classes } from './modules/classes.js';
import { Students } from './modules/students.js';
import { Draw, Display } from './modules/draw.js';
import { Scoring } from './modules/scoring.js';
import { Cycles } from './modules/cycles.js';

/**
 * Initialise l'application
 */
async function initializeApp() {
    UI.showLoading(true);

    // Restaurer les préférences depuis localStorage
    restorePreferences();

    // Charger la liste des classes
    await Classes.load();

    // Configurer les event listeners
    setupEventListeners();

    // Mettre à jour la date
    UI.updateSessionDate(CONFIG.currentDate);

    UI.showLoading(false);
}

/**
 * Restaure les préférences utilisateur depuis localStorage
 */
function restorePreferences() {
    // Mode historique
    const historyMode = Storage.getHistoryMode();
    CONFIG.historyMode = historyMode;
    const historySwitch = document.getElementById('history-mode-switch');
    if (historySwitch) historySwitch.checked = historyMode;

    // Mode tirage (par défaut sans remise)
    const drawMode = Storage.get(Storage.keys.DRAW_MODE) || 'without_replacement';
    CONFIG.drawMode = drawMode;
    const drawSwitch = document.getElementById('draw-mode-switch');
    if (drawSwitch) {
        // Inverser : checked = avec remise, unchecked = sans remise
        drawSwitch.checked = drawMode === 'with_replacement';
        // Initialiser l'affichage visuel
        handleDrawModeChange({ target: drawSwitch });
    }
}

/**
 * Configure tous les event listeners de l'application
 */
function setupEventListeners() {
    // === SIDEBAR ===
    document.getElementById('sidebar-toggle')?.addEventListener('click', () => UI.toggleSidebar());
    document.getElementById('change-class-btn')?.addEventListener('click', () => UI.showClassSelector());

    // === CLASS SELECTOR ===
    document.getElementById('create-class-btn')?.addEventListener('click', () => Classes.create());
    document.getElementById('import-class-btn')?.addEventListener('click', () => Classes.showImportModal());

    // === IMPORT MODAL ===
    document.getElementById('validate-import-btn')?.addEventListener('click', () => Classes.import());
    document.getElementById('cancel-import-btn')?.addEventListener('click', () => Classes.cancelImport());
    document.getElementById('browse-file-btn')?.addEventListener('click', () => {
        document.getElementById('file-input')?.click();
    });
    document.getElementById('file-input')?.addEventListener('change', (e) => Classes.handleFileSelection(e));

    // === MODES & SETTINGS ===
    document.getElementById('draw-mode-switch')?.addEventListener('change', handleDrawModeChange);
    document.getElementById('history-mode-switch')?.addEventListener('change', handleHistoryModeChange);
    document.getElementById('winners-count')?.addEventListener('input', handleWinnersCountChange);
    document.getElementById('confetti-switch')?.addEventListener('change', handleConfettiToggle);

    // === STUDENT SELECTION ===
    document.getElementById('select-all')?.addEventListener('click', () => {
        Students.selectAll();
        Display.updateTags();
        Display.checkDrawButton();
    });

    document.getElementById('deselect-all')?.addEventListener('click', () => {
        Students.deselectAll();
        Display.updateTags();
        Display.checkDrawButton();
    });

    // === DRAW BUTTON ===
    document.getElementById('draw-button')?.addEventListener('click', () => Draw.perform());

    // === CYCLE RESET ===
    document.getElementById('reset-cycle-btn')?.addEventListener('click', () => Cycles.reset());

    // === QUIT APPLICATION ===
    document.getElementById('quit-app-btn')?.addEventListener('click', quitApplication);

    // === SCORING PANEL ===
    document.querySelectorAll('.score-btn').forEach(btn => {
        btn.addEventListener('click', (e) => Scoring.handleScore(e.currentTarget.dataset.score));
    });
    document.getElementById('skip-scoring')?.addEventListener('click', () => Scoring.skip());
    document.getElementById('absent-btn')?.addEventListener('click', () => Scoring.markAbsent());

    // === SIDEBAR AUTO-CLOSE ===
    document.addEventListener('click', (e) => {
        const sidebar = document.getElementById('sidebar');
        const toggle = document.getElementById('sidebar-toggle');
        if (sidebar && toggle && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });

    // === WINDOW CLOSE ===
    // beforeunload : fermeture d'onglet
    window.addEventListener('beforeunload', () => {
        navigator.sendBeacon('/api/shutdown');
    });

    // pagehide : plus fiable pour la fermeture complète du navigateur
    window.addEventListener('pagehide', () => {
        navigator.sendBeacon('/api/shutdown');
    });
}

// === EVENT HANDLERS ===

function handleDrawModeChange(e) {
    // Inverser la logique : checked (droite) = avec remise, unchecked (gauche) = sans remise
    const isWithReplacement = e.target.checked;
    CONFIG.drawMode = isWithReplacement ? 'with_replacement' : 'without_replacement';
    Storage.set(Storage.keys.DRAW_MODE, CONFIG.drawMode);

    // Mettre à jour visuellement les labels
    const withLabel = document.getElementById('with-replacement-label');
    const withoutLabel = document.getElementById('without-replacement-label');
    const description = document.getElementById('draw-mode-description');

    if (isWithReplacement) {
        // Switch à droite = Avec remise actif
        withLabel?.classList.add('active');
        withoutLabel?.classList.remove('active');
        withLabel.textContent = 'Avec remise ✓';
        withoutLabel.textContent = 'Sans remise';
        if (description) {
            description.textContent = 'Mode actif : Avec remise (un élève peut être tiré plusieurs fois)';
        }
    } else {
        // Switch à gauche = Sans remise actif
        withLabel?.classList.remove('active');
        withoutLabel?.classList.add('active');
        withoutLabel.textContent = 'Sans remise ✓';
        withLabel.textContent = 'Avec remise';
        if (description) {
            description.textContent = 'Mode actif : Sans remise (chaque élève tiré une seule fois par cycle)';
        }
    }

    // Resynchroniser les checkboxes et badges selon le nouveau mode
    Students.display(); // Recalcule les checkboxes selon le mode
    Display.updateTags(); // Met à jour les badges
}

async function handleHistoryModeChange(e) {
    CONFIG.historyMode = e.target.checked;
    Storage.saveHistoryMode(CONFIG.historyMode);
    Students.display();
    Display.updateTags();
    await Cycles.updateProgress();
}

function handleWinnersCountChange(e) {
    const count = e.target.value;
    const display = document.getElementById('winners-count-display');
    if (display) display.textContent = count;
    Display.checkDrawButton();
}

function handleConfettiToggle(e) {
    Storage.set(Storage.keys.CONFETTI_ENABLED, e.target.checked);
}

async function quitApplication() {
    const confirmed = window.confirm(
        'Voulez-vous vraiment quitter l\'application ?\n\n' +
        'Le serveur sera arrêté et l\'application se fermera.'
    );

    if (!confirmed) return;

    try {
        await fetch('/api/shutdown', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

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
        UI.showError('Impossible d\'arrêter le serveur');
    }
}

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', initializeApp);
