/**
 * MODULE: State Management
 * Gestion centralisée de l'état de l'application
 */

export const CONFIG = {
    apiBaseUrl: '',
    currentClass: null,
    currentDate: new Date().toISOString().split('T')[0],
    students: [],
    historyMode: true,
    drawMode: 'without_replacement',
    winnersToScore: []
};

export const state = {
    isDrawing: false,
    isLoading: false,  // Flag pour éviter les race conditions pendant les chargements
    currentWinners: [],
    gameState: 'idle'
};

// LocalStorage management
export const Storage = {
    keys: {
        LAST_CLASS: 'lastSelectedClass',
        HISTORY_MODE: 'historyMode',
        DRAW_MODE: 'drawMode',
        CONFETTI_ENABLED: 'confettiEnabled'
    },

    get(key) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : null;
        } catch {
            return localStorage.getItem(key);
        }
    },

    set(key, value) {
        try {
            localStorage.setItem(key, typeof value === 'string' ? value : JSON.stringify(value));
        } catch (e) {
            console.error('Erreur localStorage:', e);
        }
    },

    remove(key) {
        localStorage.removeItem(key);
    },

    // Méthodes spécifiques
    saveLastClass(className) {
        this.set(this.keys.LAST_CLASS, className);
    },

    getLastClass() {
        return this.get(this.keys.LAST_CLASS);
    },

    saveHistoryMode(enabled) {
        this.set(this.keys.HISTORY_MODE, enabled);
    },

    getHistoryMode() {
        const value = this.get(this.keys.HISTORY_MODE);
        return value !== null ? value : true; // true par défaut
    }
};
