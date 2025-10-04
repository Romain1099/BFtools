/**
 * MODULE: Cycles Management
 * Logique de gestion des cycles d'interrogation
 */

import { CONFIG, state } from './state.js';
import { API } from './api.js';
import { UI } from './ui.js';

export const Cycles = {
    async updateProgress() {
        if (!CONFIG.currentClass) {
            console.warn('Cycles.updateProgress() appelé mais aucune classe sélectionnée');
            return;
        }

        // Ne pas faire d'appel API si un chargement est en cours
        if (state.isLoading) {
            console.log('Cycles.updateProgress() différé - chargement en cours');
            return;
        }

        try {
            const data = await API.getCycleProgress(CONFIG.currentClass);

            if (data.success) {
                const progress = data.progress;
                UI.updateCycleProgress(
                    progress.questioned,
                    progress.total,
                    progress.remaining,
                    data.is_complete,
                    CONFIG.historyMode
                );
            }
        } catch (error) {
            console.error('Erreur lors de la mise à jour de la progression:', error);
        }
    },

    async reset() {
        if (!CONFIG.currentClass) return;

        const confirmed = window.confirm(
            'Démarrer un nouveau cycle ?\n\n' +
            'Tous les élèves redeviendront disponibles pour un nouveau cycle d\'interrogations.\n' +
            'L\'historique sera conservé.'
        );

        if (!confirmed) return;

        try {
            const data = await API.resetCycle(CONFIG.currentClass);

            if (data.success) {
                // Nettoyer les badges existants
                const nameContainer = document.getElementById('name-container');
                if (nameContainer) nameContainer.innerHTML = '';

                // Recharger les données
                const { Students } = await import('./students.js');
                await Students.load(CONFIG.currentClass);

                // Recréer l'affichage
                const { Display } = await import('./draw.js');
                Display.updateTags();

                await this.updateProgress();

                UI.showNotification(data.message || 'Nouveau cycle démarré ! Tous les élèves sont à nouveau disponibles.');
            } else {
                UI.showError(data.error || 'Erreur lors du reset du cycle');
            }
        } catch (error) {
            console.error('Erreur lors du reset du cycle:', error);
            UI.showError('Erreur lors du reset du cycle');
        }
    }
};
