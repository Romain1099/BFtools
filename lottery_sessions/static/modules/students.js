/**
 * MODULE: Students Management
 * Logique de gestion des étudiants
 */

import { CONFIG, state } from './state.js';
import { API } from './api.js';
import { UI } from './ui.js';
import { hasBeenQuestionedInCycle, hasBeenQuestionedToday } from './utils.js';

export const Students = {
    async load(className) {
        if (!className) return;

        // Empêcher les chargements concurrents
        if (state.isLoading) {
            console.warn('Chargement déjà en cours, opération annulée');
            return;
        }

        state.isLoading = true;
        UI.showLoading(true);

        try {
            const data = await API.getStudents(className);

            if (data.success) {
                CONFIG.students = data.students;

                // Attendre que le DOM soit prêt avant d'afficher
                await new Promise(resolve => setTimeout(resolve, 50));

                this.display();
                this.updateStats();
            }
        } catch (error) {
            console.error('Erreur lors du chargement des étudiants:', error);
            UI.showError('Impossible de charger les étudiants');
        } finally {
            state.isLoading = false;
            UI.showLoading(false);
        }
    },

    display() {
        const peopleList = document.getElementById('people-list');
        if (!peopleList) return;

        // Vérifier que les étudiants sont chargés
        if (!CONFIG.students || !Array.isArray(CONFIG.students)) {
            console.warn('Students.display() appelé mais CONFIG.students non défini');
            peopleList.innerHTML = '<p style="padding: 1rem; text-align: center;">Chargement...</p>';
            return;
        }

        peopleList.innerHTML = '';

        CONFIG.students.forEach(student => {
            const studentRow = this.createStudentRow(student);
            peopleList.appendChild(studentRow);
        });
    },

    createStudentRow(student) {
        const row = document.createElement('div');
        row.className = 'student-row';

        // Vérifier si interrogé AUJOURD'HUI (chaque session est indépendante)
        const alreadyQuestionedToday = hasBeenQuestionedToday(student);

        if (alreadyQuestionedToday) {
            row.classList.add('already-questioned');
        }

        // Déterminer si la checkbox doit être cochée
        let isChecked = true;

        // En mode AVEC remise : TOUJOURS coché (ignore l'historique)
        // En mode SANS remise + historique ON : décoché si déjà interrogé AUJOURD'HUI
        if (CONFIG.drawMode === 'without_replacement' && CONFIG.historyMode && alreadyQuestionedToday) {
            isChecked = false;
        }

        const todayScore = student[CONFIG.currentDate];
        let scoreValue = '';
        let inputType = 'number';
        let minMaxAttrs = 'min="0" max="3"';

        if (todayScore !== null && todayScore !== undefined && todayScore !== '') {
            scoreValue = todayScore;
            // Si c'est "ABS", utiliser un input texte
            if (todayScore === 'ABS') {
                inputType = 'text';
                minMaxAttrs = 'readonly';
            }
        }

        row.innerHTML = `
            <label class="student-checkbox">
                <input type="checkbox" value="${student.full_name}" ${isChecked ? 'checked' : ''}>
                <span class="student-name">${student.full_name}</span>
            </label>
            <div class="score-input-container">
                <input type="${inputType}"
                       class="score-input ${todayScore === 'ABS' ? 'absent-score' : ''}"
                       ${minMaxAttrs}
                       value="${scoreValue}"
                       placeholder="-"
                       data-student="${student.full_name}"
                       title="Score: 0=Erreur, 1=Partiel, 2=Correct, 3=Excellent, ABS=Absent">
            </div>
        `;

        row.querySelector('input[type="checkbox"]').addEventListener('change', () => {
            this.onCheckChange();
        });

        row.querySelector('.score-input').addEventListener('change', (e) => {
            this.onScoreChange(e);
        });

        return row;
    },

    async onScoreChange(event) {
        const input = event.target;
        const studentName = input.dataset.student;
        const score = input.value;

        if (score !== '' && (isNaN(score) || score < 0 || score > 3)) {
            UI.showError('Le score doit être entre 0 et 3');
            input.value = '';
            return;
        }

        if (score === '') return;

        try {
            const result = await API.updateScore(
                CONFIG.currentClass,
                studentName,
                parseInt(score),
                CONFIG.currentDate
            );

            if (result.success) {
                const studentData = CONFIG.students.find(s => s.full_name === studentName);
                if (studentData) {
                    studentData[CONFIG.currentDate] = parseInt(score);
                }

                this.updateStats();
                this.display();

                // Import dynamique pour éviter les dépendances circulaires
                const { Cycles } = await import('./cycles.js');
                await Cycles.updateProgress();
            }
        } catch (error) {
            console.error('Erreur lors de la mise à jour du score:', error);
            UI.showError('Erreur réseau: impossible de contacter le serveur');
        }
    },

    onCheckChange() {
        // Géré par le module Draw
        window.dispatchEvent(new CustomEvent('students-checked-changed'));
    },

    updateStats() {
        // Vérifier que les étudiants sont chargés
        if (!CONFIG.students || !Array.isArray(CONFIG.students)) {
            console.warn('Students.updateStats() appelé mais CONFIG.students non défini');
            return;
        }

        let totalScore = 0;
        let scoredCount = 0; // Étudiants avec une vraie note (pas ABS)
        let questionedCount = 0; // Total interrogés (notes + absents)

        CONFIG.students.forEach(student => {
            const score = student[CONFIG.currentDate];
            if (score !== null && score !== undefined && score !== '') {
                questionedCount++; // Compter tous ceux qui ont une valeur

                // Compter seulement les notes numériques pour la moyenne (pas les ABS)
                if (score !== 'ABS') {
                    const numScore = parseInt(score);
                    if (!isNaN(numScore)) {
                        totalScore += numScore;
                        scoredCount++;
                    }
                }
            }
        });

        const avgScore = scoredCount > 0 ? (totalScore / scoredCount).toFixed(1) : null;
        // Afficher le nombre total interrogés (notes + absents)
        UI.updateSessionStats(questionedCount, CONFIG.students.length, avgScore);
    },

    getChecked() {
        return Array.from(document.querySelectorAll('#people-list input:checked'))
            .map(cb => cb.value);
    },

    selectAll() {
        document.querySelectorAll('#people-list input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
        });
        this.onCheckChange();
    },

    deselectAll() {
        document.querySelectorAll('#people-list input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        this.onCheckChange();
    }
};
