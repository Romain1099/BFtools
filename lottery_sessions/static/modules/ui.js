/**
 * MODULE: UI Management
 * Gestion de l'interface utilisateur et du DOM
 */

export const UI = {
    // Loading
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay?.classList.toggle('active', show);
    },

    // Errors & Notifications
    showError(message) {
        alert(message); // TODO: Implémenter une notification élégante
    },

    showNotification(message) {
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

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    // Sidebar
    toggleSidebar() {
        document.getElementById('sidebar')?.classList.toggle('open');
    },

    closeSidebar() {
        document.getElementById('sidebar')?.classList.remove('open');
    },

    openSidebar() {
        document.getElementById('sidebar')?.classList.add('open');
    },

    // Modals
    showModal(modalId) {
        document.getElementById(modalId)?.classList.add('active');
    },

    hideModal(modalId) {
        document.getElementById(modalId)?.classList.remove('active');
    },

    // Class Selector
    showClassSelector() {
        this.showModal('class-selector');
    },

    hideClassSelector() {
        this.hideModal('class-selector');
    },

    // Import Modal
    showImportModal() {
        this.hideClassSelector();
        this.showModal('import-modal');
        this.resetImportForm();
    },

    hideImportModal() {
        this.hideModal('import-modal');
    },

    resetImportForm() {
        document.getElementById('import-class-name').value = '';
        document.getElementById('import-file-path').value = '';
        document.getElementById('file-input').value = '';
        this.hideValidationMessage();
    },

    showValidationMessage(message, type) {
        const messageDiv = document.getElementById('import-validation-message');
        if (messageDiv) {
            messageDiv.textContent = message;
            messageDiv.className = `validation-message ${type}`;
            messageDiv.classList.remove('hidden');
        }
    },

    hideValidationMessage() {
        document.getElementById('import-validation-message')?.classList.add('hidden');
    },

    // Scoring Panel
    showScoringPanel(studentName) {
        document.getElementById('student-to-score').textContent = studentName;
        document.getElementById('scoring-panel')?.classList.add('visible');
    },

    hideScoringPanel() {
        document.getElementById('scoring-panel')?.classList.remove('visible');
    },

    // Stats
    updateSessionDate(dateStr) {
        const formatted = new Date(dateStr).toLocaleDateString('fr-FR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        const element = document.getElementById('session-date');
        if (element) element.textContent = formatted;
    },

    updateSessionStats(scoredCount, totalCount, avgScore) {
        const questionedEl = document.getElementById('students-questioned');
        const avgEl = document.getElementById('average-score');

        if (questionedEl) questionedEl.textContent = `${scoredCount}/${totalCount}`;
        if (avgEl) avgEl.textContent = avgScore !== null ? `${avgScore}/3` : '--/3';
    },

    // Cycle Progress
    updateCycleProgress(progress, total, remaining, isComplete, historyMode) {
        const progressPercent = total > 0 ? Math.round((progress / total) * 100) : 0;

        const fillEl = document.getElementById('progress-fill');
        const textEl = document.getElementById('progress-text');
        const remainingEl = document.getElementById('remaining-students');
        const resetBtn = document.getElementById('reset-cycle-btn');

        if (fillEl) fillEl.style.width = `${progressPercent}%`;
        if (textEl) textEl.textContent = `${progress}/${total} élèves`;
        if (remainingEl) remainingEl.textContent = remaining;

        if (resetBtn) {
            resetBtn.classList.toggle('hidden', !(isComplete && historyMode));
        }
    },

    // Draw Button
    updateDrawButton(enabled, text) {
        const button = document.getElementById('draw-button');
        if (button) {
            button.disabled = !enabled;
            button.textContent = text;
        }
    },

    // Current Class
    updateCurrentClassName(className) {
        const element = document.getElementById('current-class-name');
        if (element) element.textContent = className;
    }
};
