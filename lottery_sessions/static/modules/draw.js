/**
 * MODULE: Draw Management
 * Logique du tirage au sort et affichage des étiquettes
 */

import { CONFIG, state } from './state.js';
import { API } from './api.js';
import { UI } from './ui.js';
import { getRandomPosition } from './utils.js';
import { Students } from './students.js';
import { Scoring } from './scoring.js';
import { Cycles } from './cycles.js';

export const Display = {
    updateTags() {
        const nameContainer = document.getElementById('name-container');
        if (!nameContainer) return;

        // Attendre que les étudiants soient chargés
        if (!CONFIG.students || CONFIG.students.length === 0) {
            nameContainer.innerHTML = '';
            return;
        }

        const checkedStudents = Students.getChecked();
        const existingTags = Array.from(nameContainer.children);
        const existingPeople = existingTags.map(tag => tag.textContent);

        // Supprimer les étiquettes décochées
        existingTags.forEach(tag => {
            if (!checkedStudents.includes(tag.textContent)) {
                tag.style.transition = 'all 0.3s ease-out';
                tag.style.opacity = '0';
                tag.style.transform = 'scale(0.8)';
                setTimeout(() => tag.remove(), 300);
            } else {
                // Nettoyer les classes CSS des badges qui restent (retirer styles de winner)
                tag.classList.remove('winner', 'fade-out', 'highlight', 'shuffling', 'spinning');
                tag.style.opacity = '1';
                tag.style.transform = 'scale(1)';
                tag.style.filter = '';
                tag.style.zIndex = '10';
                tag.style.background = '';
                tag.style.color = '';
            }
        });

        // Ajouter les nouvelles étiquettes
        checkedStudents.forEach(studentName => {
            if (!existingPeople.includes(studentName)) {
                const tag = document.createElement('div');
                tag.className = 'person-tag';
                tag.textContent = studentName;

                const position = getRandomPosition(tag);
                tag.style.left = `${position.x}px`;
                tag.style.top = `${position.y}px`;

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
    },

    checkDrawButton() {
        const checkedCount = Students.getChecked().length;
        const winnersCount = parseInt(document.getElementById('winners-count')?.value || 1);

        if (checkedCount < winnersCount) {
            UI.updateDrawButton(false, `🎲 Il faut au moins ${winnersCount} participant(s)`);
        } else {
            UI.updateDrawButton(true, '🎲 Tirage au sort');
        }
    }
};

export const Draw = {
    async perform() {
        // Empêcher le tirage pendant un chargement ou si déjà en cours
        if (state.isDrawing || state.isLoading) {
            if (state.isLoading) {
                UI.showError('Veuillez patienter, chargement en cours...');
            }
            return;
        }

        // Vérifier que les données sont chargées
        if (!CONFIG.students || CONFIG.students.length === 0) {
            UI.showError('Aucun étudiant chargé');
            return;
        }

        // Réinitialiser les tags
        const existingTags = document.querySelectorAll('.person-tag');
        existingTags.forEach(tag => {
            tag.classList.remove('winner', 'fade-out', 'highlight', 'shuffling', 'spinning');
            tag.style.opacity = '1';
            tag.style.transform = 'scale(1)';
            tag.style.filter = '';
            tag.style.zIndex = '10';
            tag.style.background = '';
            tag.style.color = '';
        });

        const checkedStudents = Students.getChecked();
        const winnersCount = parseInt(document.getElementById('winners-count')?.value || 1);

        if (checkedStudents.length < winnersCount) {
            UI.showError(`Il faut au moins ${winnersCount} participant(s)`);
            return;
        }

        state.isDrawing = true;
        state.gameState = 'drawing';
        UI.updateDrawButton(false, '🎲 Tirage en cours...');
        UI.closeSidebar();

        // Lancer l'animation (définie dans animations.js)
        const tags = Array.from(document.querySelectorAll('.person-tag'));
        if (typeof startShuffleAnimation === 'function') {
            startShuffleAnimation(tags, () => {
                this.selectWinners(checkedStudents, winnersCount);
            });
        } else {
            // Fallback si animations.js n'est pas chargé
            this.selectWinners(checkedStudents, winnersCount);
        }
    },

    async selectWinners(candidates, count) {
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

        // Animer les gagnants (défini dans animations.js)
        if (typeof animateWinners === 'function') {
            animateWinners(winners);
        }

        // NE PAS décocher automatiquement les gagnants
        // Ils seront décochés seulement si on leur met une note (via Scoring)

        // Enregistrer le tirage (endpoint vide, juste pour tracking)
        for (const winner of winners) {
            await API.recordDraw(CONFIG.currentClass, winner, CONFIG.currentDate);
        }

        // La progression sera mise à jour après la notation

        // Afficher le panel de notation
        setTimeout(() => {
            Scoring.showPanel();
            state.isDrawing = false;
            Display.checkDrawButton();
        }, 2000);
    }
};

// Event listener pour la mise à jour de l'affichage
window.addEventListener('students-checked-changed', () => {
    Display.updateTags();
    Display.checkDrawButton();
});

window.addEventListener('class-selected', () => {
    Display.updateTags();
    Display.checkDrawButton();
});
