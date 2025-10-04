/**
 * MODULE: API Client
 * Toutes les requêtes vers le backend Flask
 */

export const API = {
    baseUrl: '',

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `Erreur HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`Erreur API [${endpoint}]:`, error);
            throw error;
        }
    },

    // Classes
    async getClasses() {
        return this.request('/api/classes');
    },

    async getClassesWithVariants() {
        return this.request('/api/classes_with_variants');
    },

    async createClass(className, students = []) {
        return this.request('/api/create_class', {
            method: 'POST',
            body: JSON.stringify({ class_name: className, students })
        });
    },

    async createVariant(baseClass, variantType) {
        return this.request('/api/create_variant', {
            method: 'POST',
            body: JSON.stringify({ base_class: baseClass, variant_type: variantType })
        });
    },

    async importClass(className, fileContent) {
        return this.request('/api/import_class', {
            method: 'POST',
            body: JSON.stringify({ class_name: className, file_content: fileContent })
        });
    },

    // Students
    async getStudents(className) {
        return this.request(`/api/students/${className}`);
    },

    // Draw & Scoring
    async recordDraw(className, studentName, date) {
        return this.request('/api/draw', {
            method: 'POST',
            body: JSON.stringify({ class_name: className, student_name: studentName, date })
        });
    },

    async updateScore(className, studentName, score, date) {
        return this.request('/api/score', {
            method: 'POST',
            body: JSON.stringify({ class_name: className, student_name: studentName, score, date })
        });
    },

    // Cycles
    async getCycleProgress(className) {
        return this.request(`/api/cycle_progress/${className}`);
    },

    async resetCycle(className) {
        return this.request(`/api/reset_cycle/${className}`, {
            method: 'POST'
        });
    },

    // Sessions
    async getSessions(className) {
        return this.request(`/api/sessions/${className}`);
    },

    // Config & System
    async getConfig() {
        return this.request('/api/config');
    },

    async shutdown() {
        return this.request('/api/shutdown', {
            method: 'POST'
        });
    }
};
