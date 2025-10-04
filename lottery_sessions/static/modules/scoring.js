/**
 * MODULE: Scoring Management
 * Logique de notation des étudiants après le tirage
 */

import { CONFIG } from './state.js';
import { API } from './api.js';
import { UI } from './ui.js';

export const Scoring = {
    async handleScore(score) {
        if (CONFIG.winnersToScore.length === 0) return;

        const student = CONFIG.winnersToScore.shift();

        try {
            await API.updateScore(
                CONFIG.currentClass,
                student,
                parseInt(score),
                CONFIG.currentDate
            );

            const studentData = CONFIG.students.find(s => s.full_name === student);
            if (studentData) {
                studentData[CONFIG.currentDate] = parseInt(score);
            }

            // Mettre à jour l'affichage selon le mode
            const { Display } = await import('./draw.js');

            if (CONFIG.drawMode === 'without_replacement' && CONFIG.historyMode) {
                // Mode SANS remise : décocher l'étudiant noté
                const checkbox = document.querySelector(`#people-list input[value="${student}"]`);
                if (checkbox) {
                    checkbox.checked = false;
                }
                // Mettre à jour les badges (le badge sera supprimé car décoché)
                Display.updateTags();
            } else {
                // Mode AVEC remise : garder l'étudiant coché mais nettoyer le style winner
                Display.updateTags();
            }

            if (CONFIG.winnersToScore.length > 0) {
                this.showPanel();
            } else {
                this.hidePanel();

                const { Students } = await import('./students.js');
                await Students.load(CONFIG.currentClass);

                const { Display } = await import('./draw.js');
                Display.updateTags();

                const { Cycles } = await import('./cycles.js');
                await Cycles.updateProgress();
            }
        } catch (error) {
            console.error('Erreur lors de la notation:', error);
            UI.showError('Erreur lors de l\'enregistrement de la note');
        }
    },

    async skip() {
        CONFIG.winnersToScore.shift();

        // Nettoyer le style winner du badge (mais ne pas décocher - l'étudiant reste disponible)
        const { Display } = await import('./draw.js');
        Display.updateTags();

        if (CONFIG.winnersToScore.length > 0) {
            this.showPanel();
        } else {
            this.hidePanel();
        }
    },

    async markAbsent() {
        if (CONFIG.winnersToScore.length === 0) return;

        const student = CONFIG.winnersToScore.shift();

        try {
            // Enregistrer "ABS" comme valeur dans le CSV
            const response = await fetch('/api/score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    class_name: CONFIG.currentClass,
                    student_name: student,
                    score: 'ABS',
                    date: CONFIG.currentDate
                })
            });

            const result = await response.json();
            if (!result.success) {
                UI.showError(result.error || 'Erreur lors de la sauvegarde de l\'absence');
                return;
            }

            const studentData = CONFIG.students.find(s => s.full_name === student);
            if (studentData) {
                studentData[CONFIG.currentDate] = 'ABS';
            }

            // TOUJOURS décocher l'étudiant absent (peu importe le mode)
            const checkbox = document.querySelector(`#people-list input[value="${student}"]`);
            if (checkbox) {
                checkbox.checked = false;
            }

            // Mettre à jour les badges
            const { Display } = await import('./draw.js');
            Display.updateTags();

            if (CONFIG.winnersToScore.length > 0) {
                this.showPanel();
            } else {
                this.hidePanel();

                const { Students } = await import('./students.js');
                await Students.load(CONFIG.currentClass);

                const { Cycles } = await import('./cycles.js');
                await Cycles.updateProgress();
            }
        } catch (error) {
            console.error('Erreur lors du marquage d\'absence:', error);
            UI.showError('Erreur lors de l\'enregistrement de l\'absence');
        }
    },

    showPanel() {
        if (CONFIG.winnersToScore.length === 0) {
            this.hidePanel();
            return;
        }

        const student = CONFIG.winnersToScore[0];
        UI.showScoringPanel(student);
    },

    hidePanel() {
        UI.hideScoringPanel();

        // Mettre à jour l'affichage si mode sans remise
        if (CONFIG.drawMode === 'without_replacement' && CONFIG.historyMode) {
            const { Display } = import('./draw.js').then(module => {
                module.Display.updateTags();
            });
        }
    }
};
