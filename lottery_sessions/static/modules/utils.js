/**
 * MODULE: Utilities
 * Fonctions utilitaires réutilisables
 */

export function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

export function getRandomPosition(element) {
    const margin = 60;
    const containerWidth = window.innerWidth;
    const containerHeight = window.innerHeight;

    const x = margin + Math.random() * (containerWidth - 2 * margin - 200);
    const y = margin + Math.random() * (containerHeight - 2 * margin - 200);

    return { x, y };
}

export function isDateField(field) {
    try {
        const date = new Date(field);
        return !isNaN(date.getTime()) && field.match(/^\d{4}-\d{2}-\d{2}$/);
    } catch {
        return false;
    }
}

export function getCurrentCycleFields(student) {
    // Simplement retourner toutes les dates (plus de logique NEW_CYCLE)
    const allFields = Object.keys(student);
    return allFields.filter(f => isDateField(f));
}

export function hasBeenQuestionedInCycle(student) {
    const cycleFields = getCurrentCycleFields(student);

    for (const field of cycleFields) {
        const value = student[field];
        // Considéré comme interrogé si: a un SCORE réel (0-3), PAS "ABS"
        if (value !== null && value !== undefined && value !== '' && value !== 'ABS') {
            return true;
        }
    }
    return false;
}

export function hasBeenQuestionedToday(student) {
    const today = new Date().toISOString().split('T')[0];
    const value = student[today];
    // Considéré comme interrogé aujourd'hui si: a une valeur (score 0-3 ou "ABS")
    return value !== null && value !== undefined && value !== '';
}
