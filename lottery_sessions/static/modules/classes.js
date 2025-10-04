/**
 * MODULE: Classes Management
 * Logique de gestion des classes
 */

import { CONFIG, Storage, state } from './state.js';
import { API } from './api.js';
import { UI } from './ui.js';
import { Students } from './students.js';
import { Cycles } from './cycles.js';

export const Classes = {
    async load() {
        try {
            const data = await API.getClassesWithVariants();

            if (data.success) {
                this.display(data.grouped);

                // Vérifier s'il y a des classes
                const totalClasses = Object.keys(data.grouped).length;

                if (totalClasses === 0) {
                    UI.showClassSelector();
                } else {
                    const lastClass = Storage.getLastClass();
                    // Vérifier si la dernière classe existe encore
                    const allClassNames = this.getAllClassNames(data.grouped);
                    if (lastClass && allClassNames.includes(lastClass)) {
                        await this.select(lastClass);
                    } else {
                        UI.showClassSelector();
                    }
                }
            }
        } catch (error) {
            console.error('Erreur lors du chargement des classes:', error);
            UI.showError('Impossible de charger les classes');
        }
    },

    getAllClassNames(grouped) {
        const names = [];
        for (const baseClass in grouped) {
            const group = grouped[baseClass];
            names.push(group.base);
            names.push(...group.variants);
        }
        return names;
    },

    display(grouped) {
        const classList = document.getElementById('class-list');
        if (!classList) return;

        classList.innerHTML = '';

        if (Object.keys(grouped).length === 0) {
            classList.innerHTML = '<p>Aucune classe disponible. Créez ou importez une classe.</p>';
            return;
        }

        // Afficher chaque groupe de classes
        for (const baseClass in grouped) {
            const group = grouped[baseClass];
            const groupElement = this.createClassGroup(baseClass, group);
            classList.appendChild(groupElement);
        }
    },

    createClassGroup(baseClass, group) {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'class-group';

        // Classe de base
        const baseItem = document.createElement('div');
        baseItem.className = 'class-item class-item-base';
        baseItem.innerHTML = `
            <div class="class-info">
                <span class="class-name">📘 ${group.base}</span>
                <span class="class-stats">Classe de base</span>
            </div>
            <button class="create-variant-btn" data-base="${group.base}" title="Créer une variante">
                ➕
            </button>
        `;
        baseItem.querySelector('.class-info').addEventListener('click', () => this.select(group.base));
        baseItem.querySelector('.create-variant-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.showCreateVariantModal(group.base);
        });
        groupDiv.appendChild(baseItem);

        // Variantes
        if (group.variants.length > 0) {
            const variantsContainer = document.createElement('div');
            variantsContainer.className = 'variants-container';

            group.variants.forEach(variant => {
                const variantType = variant.replace(`${group.base}_`, '');
                const variantItem = document.createElement('div');
                variantItem.className = 'class-item class-item-variant';
                variantItem.innerHTML = `
                    <div class="class-info">
                        <span class="class-name">└─ ${variantType}</span>
                        <span class="class-stats">Variante</span>
                    </div>
                `;
                variantItem.addEventListener('click', () => this.select(variant));
                variantsContainer.appendChild(variantItem);
            });

            groupDiv.appendChild(variantsContainer);
        }

        return groupDiv;
    },

    async select(className) {
        // Empêcher les sélections concurrentes
        if (state.isLoading) {
            console.warn('Chargement déjà en cours, sélection annulée');
            return;
        }

        CONFIG.currentClass = className;
        UI.updateCurrentClassName(className);
        Storage.saveLastClass(className);

        UI.hideClassSelector();

        // Charger les étudiants et la progression
        await Students.load(className);
        await Cycles.updateProgress();

        // Attendre un peu pour que le DOM soit complètement rendu
        await new Promise(resolve => setTimeout(resolve, 100));

        // Notifier le changement (maintenant que tout est chargé)
        window.dispatchEvent(new CustomEvent('class-selected'));
    },

    async create() {
        const className = prompt('Nom de la nouvelle classe:');
        if (!className) return;

        const studentsText = prompt('Entrez les étudiants (format: Nom Prénom, un par ligne):');
        if (!studentsText) return;

        const students = studentsText.split('\n')
            .filter(line => line.trim())
            .map(line => {
                const parts = line.trim().split(' ');
                return {
                    nom: parts[0] || '',
                    prenom: parts.slice(1).join(' ') || ''
                };
            });

        try {
            const result = await API.createClass(className, students);
            if (result.success) {
                await this.load();
                await this.select(className);
            }
        } catch (error) {
            UI.showError('Erreur lors de la création de la classe');
        }
    },

    showImportModal() {
        UI.showImportModal();
        CONFIG.selectedFile = null;
    },

    handleFileSelection(event) {
        const file = event.target.files[0];
        if (file) {
            document.getElementById('import-file-path').value = file.name;
            CONFIG.selectedFile = file;
        }
    },

    async import() {
        let className = document.getElementById('import-class-name')?.value.trim();
        const file = CONFIG.selectedFile;

        if (!className) {
            UI.showValidationMessage('Veuillez entrer un nom de classe', 'error');
            return;
        }

        if (!file) {
            UI.showValidationMessage('Veuillez sélectionner un fichier CSV', 'error');
            return;
        }

        if (!className.startsWith('classe_')) {
            className = 'classe_' + className;
        }

        const importBtn = document.getElementById('validate-import-btn');
        importBtn.disabled = true;
        importBtn.textContent = '⏳ Import en cours...';

        try {
            const fileContent = await file.text();
            const result = await API.importClass(className, fileContent);

            if (result.success) {
                UI.showValidationMessage(
                    result.message || 'Import réussi ! Classe créée avec succès.',
                    'success'
                );

                setTimeout(async () => {
                    UI.hideImportModal();
                    await this.load();
                    await this.select(className);
                }, 2000);
            }
        } catch (error) {
            console.error('Erreur lors de l\'import:', error);
            UI.showValidationMessage(
                error.message || 'Erreur réseau : impossible de contacter le serveur',
                'error'
            );
            importBtn.disabled = false;
            importBtn.textContent = '✓ Valider et importer';
        }
    },

    cancelImport() {
        UI.hideImportModal();
        UI.showClassSelector();
    },

    showCreateVariantModal(baseClass) {
        const variantType = prompt(`Créer une variante de "${baseClass}"\n\nNom de la variante (ex: groupe1, TD1, etc.):`);
        if (!variantType || !variantType.trim()) return;

        this.createVariant(baseClass, variantType.trim());
    },

    async createVariant(baseClass, variantType) {
        try {
            const result = await API.createVariant(baseClass, variantType);

            if (result.success) {
                UI.showNotification(result.message || 'Variante créée avec succès');
                await this.load();
                await this.select(result.variant_name);
            }
        } catch (error) {
            console.error('Erreur lors de la création de la variante:', error);
            UI.showError(error.message || 'Erreur lors de la création de la variante');
        }
    }
};
