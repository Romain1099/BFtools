const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const csv = require('csv-parser');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const cors = require('cors');
const bodyParser = require('body-parser');
const { createReadStream } = require('fs');
const { exec } = require('child_process');

const app = express();
const PORT = 3000;

const BASE_PATH = 'chemin\vers\Cours';

app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Fonction pour lire un CSV
async function readCSV(filePath) {
    return new Promise((resolve, reject) => {
        const results = [];
        createReadStream(filePath)
            .pipe(csv({ separator: ';' }))
            .on('data', (data) => results.push(data))
            .on('end', () => resolve(results))
            .on('error', reject);
    });
}

// Fonction pour écrire un CSV
async function writeCSV(filePath, data) {
    if (!data || data.length === 0) return;

    const headers = Object.keys(data[0]).map(key => ({
        id: key,
        title: key
    }));

    const csvWriter = createCsvWriter({
        path: filePath,
        header: headers,
        fieldDelimiter: ';'
    });

    await csvWriter.writeRecords(data);
}

// Route pour obtenir la liste des niveaux
app.get('/api/levels', async (req, res) => {
    try {
        const entries = await fs.readdir(BASE_PATH, { withFileTypes: true });
        const levels = entries
            .filter(entry => entry.isDirectory())
            .map(entry => entry.name)
            .filter(name => !name.startsWith('Test') && !name.includes('Tuto'));

        res.json(levels);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Route pour obtenir la progression d'un niveau
app.get('/api/progression/:level', async (req, res) => {
    try {
        const { level } = req.params;
        const csvPath = path.join(BASE_PATH, level, 'progression.csv');

        // Vérifier si le fichier existe
        try {
            await fs.access(csvPath);
        } catch {
            // Créer un fichier vide si il n'existe pas
            const defaultData = [];
            await writeCSV(csvPath, defaultData);
            return res.json([]);
        }

        const data = await readCSV(csvPath);
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Route pour mettre à jour la progression
app.post('/api/progression/:level', async (req, res) => {
    try {
        const { level } = req.params;
        const data = req.body;
        const csvPath = path.join(BASE_PATH, level, 'progression.csv');

        await writeCSV(csvPath, data);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Route pour obtenir le bilan global
app.get('/api/summary', async (req, res) => {
    try {
        const entries = await fs.readdir(BASE_PATH, { withFileTypes: true });
        const levels = entries
            .filter(entry => entry.isDirectory())
            .map(entry => entry.name)
            .filter(name => !name.startsWith('Test') && !name.includes('Tuto'));

        const summary = {};

        for (const level of levels) {
            const csvPath = path.join(BASE_PATH, level, 'progression.csv');
            try {
                await fs.access(csvPath);
                const data = await readCSV(csvPath);

                // Ne pas inclure les niveaux sans données
                if (data.length === 0) continue;

                const stats = {
                    total: data.length,
                    // Préparation des documents
                    prepCoursComplete: data.filter(row => row.prep_cours === 'oui' || row.prep_cours === 'true').length,
                    prepExercicesComplete: data.filter(row => row.prep_exercices === 'oui' || row.prep_exercices === 'true').length,
                    prepEvaluationComplete: data.filter(row => row.prep_evaluation === 'oui' || row.prep_evaluation === 'true').length,
                    // Avancement en classe
                    classeCoursComplete: data.filter(row => row.classe_cours === 'oui' || row.classe_cours === 'true').length,
                    classeExercicesComplete: data.filter(row => row.classe_exercices === 'oui' || row.classe_exercices === 'true').length,
                    classeEvaluationComplete: data.filter(row => row.classe_evaluation === 'oui' || row.classe_evaluation === 'true').length,
                    chapters: data
                };

                summary[level] = stats;
            } catch {
                // Ne rien ajouter si le fichier n'existe pas
            }
        }

        res.json(summary);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Route pour obtenir les dossiers de séquences d'un niveau
app.get('/api/sequences/:level', async (req, res) => {
    try {
        const { level } = req.params;
        const sequencesPath = path.join(BASE_PATH, level, 'Séquences');

        // Vérifier si le dossier Séquences existe
        try {
            await fs.access(sequencesPath);
        } catch {
            // Essayer avec "Sequences" sans accent
            const altPath = path.join(BASE_PATH, level, 'Sequences');
            try {
                await fs.access(altPath);
                sequencesPath = altPath;
            } catch {
                return res.json([]);
            }
        }

        const entries = await fs.readdir(sequencesPath, { withFileTypes: true });
        const folders = entries
            .filter(entry => entry.isDirectory())
            .map(entry => ({
                name: entry.name,
                path: path.join(sequencesPath, entry.name)
            }));

        res.json(folders);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Route pour trouver les suggestions de dossiers pour un chapitre
app.post('/api/suggest-folder', async (req, res) => {
    try {
        const { level, chapterName } = req.body;
        const sequencesPath = path.join(BASE_PATH, level, 'Séquences');

        let actualPath = sequencesPath;
        try {
            await fs.access(sequencesPath);
        } catch {
            const altPath = path.join(BASE_PATH, level, 'Sequences');
            try {
                await fs.access(altPath);
                actualPath = altPath;
            } catch {
                return res.json({ suggestions: [] });
            }
        }

        const entries = await fs.readdir(actualPath, { withFileTypes: true });
        const folders = entries
            .filter(entry => entry.isDirectory())
            .map(entry => entry.name);

        // Algorithme de suggestion basé sur la similarité
        const suggestions = folders
            .map(folder => {
                const folderLower = folder.toLowerCase();
                const chapterLower = chapterName.toLowerCase();

                // Calculer un score de similarité simple
                let score = 0;

                // Correspondance exacte
                if (folderLower === chapterLower) score = 100;

                // Le dossier contient le nom du chapitre
                else if (folderLower.includes(chapterLower)) score = 80;

                // Le nom du chapitre contient le dossier
                else if (chapterLower.includes(folderLower)) score = 70;

                // Recherche de mots-clés communs
                else {
                    const chapterWords = chapterLower.split(/[\s_\-]+/);
                    const folderWords = folderLower.split(/[\s_\-]+/);
                    const commonWords = chapterWords.filter(word =>
                        word.length > 3 && folderWords.some(fw => fw.includes(word))
                    );
                    score = commonWords.length * 20;
                }

                return { name: folder, score, path: path.join(actualPath, folder) };
            })
            .filter(item => item.score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, 5); // Top 5 suggestions

        res.json({
            suggestions,
            allFolders: folders.map(f => ({
                name: f,
                path: path.join(actualPath, f)
            }))
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Route pour ouvrir un dossier dans l'explorateur
app.post('/api/open-folder', async (req, res) => {
    try {
        const { folderPath } = req.body;

        // Commande pour ouvrir l'explorateur Windows
        const command = `explorer "${folderPath.replace(/\//g, '\\')}"`;

        exec(command, (error) => {
            if (error) {
                console.error('Erreur:', error);
                return res.status(500).json({ error: 'Impossible d\'ouvrir le dossier' });
            }
            res.json({ success: true });
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Route pour sélectionner un dossier avec boîte de dialogue native
app.post('/api/select-folder', async (req, res) => {
    try {
        const { spawn } = require('child_process');

        // Utiliser PowerShell pour ouvrir une boîte de dialogue de sélection de dossier
        const psScript = `
Add-Type -AssemblyName System.Windows.Forms
$folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
$folderBrowser.Description = "Sélectionnez le dossier de séquence"
$folderBrowser.SelectedPath = ${BASE_PATH}
$folderBrowser.ShowNewFolderButton = $false

if ($folderBrowser.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $folderBrowser.SelectedPath
} else {
    Write-Output "CANCELLED"
}
        `;

        const ps = spawn('powershell', [
            '-ExecutionPolicy', 'Bypass',
            '-Command', psScript
        ]);

        let output = '';
        let error = '';

        ps.stdout.on('data', (data) => {
            output += data.toString();
        });

        ps.stderr.on('data', (data) => {
            error += data.toString();
        });

        ps.on('close', (code) => {
            if (code === 0) {
                const selectedPath = output.trim();
                if (selectedPath === 'CANCELLED' || selectedPath === '') {
                    res.json({ success: false, cancelled: true });
                } else {
                    res.json({ success: true, folderPath: selectedPath });
                }
            } else {
                console.error('PowerShell error:', error);
                res.status(500).json({ error: 'Erreur lors de l\'ouverture de la boîte de dialogue' });
            }
        });

    } catch (error) {
        console.error('Erreur:', error);
        res.status(500).json({ error: error.message });
    }
});

// Routes pour la configuration
app.get('/api/config', async (req, res) => {
    try {
        const configPath = path.join(__dirname, 'config.json');
        const configData = await fs.readFile(configPath, 'utf8');
        res.json(JSON.parse(configData));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/config', async (req, res) => {
    try {
        const configPath = path.join(__dirname, 'config.json');
        const newConfig = req.body;

        await fs.writeFile(configPath, JSON.stringify(newConfig, null, 2));
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/config/reset', async (req, res) => {
    try {
        const configPath = path.join(__dirname, 'config.json');

        // Configuration par défaut
        const defaultConfig = {
            "columns": {
                "fixed": [
                    {
                        "id": "nom",
                        "label": "Chapitre",
                        "type": "text",
                        "required": true,
                        "editable": true
                    },
                    {
                        "id": "dossier_sequence",
                        "label": "Dossier",
                        "type": "text",
                        "required": false,
                        "editable": true
                    }
                ],
                "preparation": [
                    {
                        "id": "prep_cours",
                        "label": "Cours",
                        "type": "checkbox",
                        "category": "preparation",
                        "required": false
                    },
                    {
                        "id": "prep_exercices",
                        "label": "Exercices",
                        "type": "checkbox",
                        "category": "preparation",
                        "required": false
                    },
                    {
                        "id": "prep_evaluation",
                        "label": "Évaluation",
                        "type": "checkbox",
                        "category": "preparation",
                        "required": false
                    }
                ],
                "classe": [
                    {
                        "id": "classe_cours",
                        "label": "Cours",
                        "type": "checkbox",
                        "category": "classe",
                        "required": false
                    },
                    {
                        "id": "classe_exercices",
                        "label": "Exercices",
                        "type": "checkbox",
                        "category": "classe",
                        "required": false
                    },
                    {
                        "id": "classe_evaluation",
                        "label": "Évaluation",
                        "type": "checkbox",
                        "category": "classe",
                        "required": false
                    }
                ],
                "custom": []
            },
            "categories": [
                {
                    "id": "preparation",
                    "label": "📝 Préparation des documents",
                    "color": "#667eea"
                },
                {
                    "id": "classe",
                    "label": "🎓 Avancement en classe",
                    "color": "#f093fb"
                }
            ],
            "settings": {
                "showProgressBars": true,
                "autoSave": false,
                "dateFormat": "DD/MM/YYYY"
            }
        };

        await fs.writeFile(configPath, JSON.stringify(defaultConfig, null, 2));
        res.json({ success: true, config: defaultConfig });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Serveur démarré sur http://localhost:${PORT}`);
});