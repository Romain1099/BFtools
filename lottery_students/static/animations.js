/**
 * Animations pour Lottery Sessions
 * Reprend les animations existantes du projet original
 */

// Configuration des animations (par défaut, sera écrasée par la config serveur)
let ANIMATION_CONFIG = {
    shuffle: {
        maxShuffles: 8,
        angleIncrement: 25,
        angleOffset: 35,
        baseRadius: 12,
        radiusVariation: 8,
        radiusFrequency: 0.15,
        offsetMultiplier: 0.5,
        movementDuration: 500,
        delayMin: 300,
        delayVariation: 100,
        pulseProbability: 0.1,
        pulseDuration: 500
    },
    highlight: {
        maxRounds: 4,
        delayMin: 400,
        delayVariation: 200
    },
    general: {
        initialDisplayDelay: 50,
        transitionDisableDuration: 250
    }
};

// Charger la configuration d'animation depuis le serveur
async function loadAnimationConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();

        if (data.success && data.config && data.config.animation) {
            // Fusionner avec la config par défaut
            ANIMATION_CONFIG = { ...ANIMATION_CONFIG, ...data.config.animation };
            console.log('Configuration d\'animation chargée:', ANIMATION_CONFIG);
        }
    } catch (error) {
        console.error('Erreur lors du chargement de la configuration d\'animation:', error);
        // Utiliser la configuration par défaut
    }
}

// Variables pour les confettis
let confettiCanvas = null;
let ctx = null;
let confetti = [];
let animationId = null;

// Initialisation du canvas pour les confettis
document.addEventListener('DOMContentLoaded', async () => {
    // Charger la configuration d'animation
    await loadAnimationConfig();

    confettiCanvas = document.getElementById('confetti-canvas');
    if (confettiCanvas) {
        ctx = confettiCanvas.getContext('2d');
        setupCanvas();
        window.addEventListener('resize', setupCanvas);
    }
});

/**
 * Configure le canvas pour les confettis
 */
function setupCanvas() {
    if (!confettiCanvas) return;
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;
}

/**
 * Démarre l'animation de mélange
 */
function startShuffleAnimation(tags, callback) {
    let shuffleCount = 0;
    const cfg = ANIMATION_CONFIG.shuffle;

    function performShuffle() {
        shuffleCount++;

        tags.forEach((tag, index) => {
            tag.style.transition = 'none';
            tag.classList.add('shuffling');

            const angle = (shuffleCount * cfg.angleIncrement + index * cfg.angleOffset) % 360;
            const radius = cfg.baseRadius + Math.sin(shuffleCount * cfg.radiusFrequency) * cfg.radiusVariation;
            const position = getRandomPosition(tag);

            const offsetX = Math.cos(angle * Math.PI / 180) * radius * cfg.offsetMultiplier;
            const offsetY = Math.sin(angle * Math.PI / 180) * radius * cfg.offsetMultiplier;

            createSmoothMovement(tag, position.x + offsetX, position.y + offsetY, cfg.movementDuration);

            // Retirer les anciens highlights
            tag.classList.remove('highlight');

            // Ajouter un highlight orange aléatoire pendant le shuffle
            if (Math.random() < cfg.pulseProbability * 3) { // Plus de chance d'avoir un highlight
                tag.classList.add('highlight');
                setTimeout(() => {
                    if (tag.classList.contains('shuffling')) { // Seulement si encore en shuffle
                        tag.classList.remove('highlight');
                    }
                }, cfg.pulseDuration);
            }
        });

        if (shuffleCount < cfg.maxShuffles) {
            setTimeout(performShuffle, cfg.delayMin + Math.random() * cfg.delayVariation);
        } else {
            // Nettoyer tous les highlights avant la phase finale
            tags.forEach(tag => {
                tag.classList.remove('highlight', 'shuffling');
            });
            setTimeout(() => startHighlightPhase(tags, callback), 300);
        }
    }

    requestAnimationFrame(() => {
        performShuffle();
    });
}

/**
 * Phase de highlight avant la sélection finale
 */
function startHighlightPhase(tags, callback) {
    let highlightRounds = 0;
    const cfg = ANIMATION_CONFIG.highlight;
    const winnersCount = parseInt(document.getElementById('winners-count').value, 10);

    function performHighlight() {
        tags.forEach(tag => {
            tag.classList.remove('highlight', 'spinning');
        });

        const shuffledTags = [...tags].sort(() => Math.random() - 0.5);
        const highlightCount = Math.min(winnersCount + Math.floor(Math.random() * 3), tags.length);

        for (let i = 0; i < highlightCount; i++) {
            shuffledTags[i].classList.add('highlight');
            if (Math.random() < 0.5) {
                shuffledTags[i].classList.add('spinning');
            }
        }

        highlightRounds++;

        if (highlightRounds < cfg.maxRounds) {
            setTimeout(performHighlight, cfg.delayMin + Math.random() * cfg.delayVariation);
        } else {
            // Nettoyer les classes d'animation
            tags.forEach(tag => {
                tag.classList.remove('shuffling', 'highlight', 'spinning', 'pulse-effect');
            });

            if (callback) callback();
        }
    }

    performHighlight();
}

/**
 * Anime les gagnants sélectionnés
 */
function animateWinners(winners) {
    const tags = Array.from(document.querySelectorAll('.person-tag'));

    // Faire disparaître les non-gagnants
    tags.forEach(tag => {
        if (!winners.includes(tag.textContent)) {
            tag.classList.add('fade-out');
        }
    });

    // Animer les gagnants
    winners.forEach((winner, index) => {
        const tag = tags.find(t => t.textContent === winner);
        if (tag) {
            setTimeout(() => {
                tag.classList.add('winner');

                // Créer des confettis si activé
                if (document.getElementById('confetti-switch').checked) {
                    const rect = tag.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;
                    createConfettiExplosion(centerX, centerY);
                }
            }, index * 300);
        }
    });
}

/**
 * Crée un mouvement fluide pour un élément
 */
function createSmoothMovement(element, targetX, targetY, duration = 600) {
    const startX = parseFloat(element.style.left) || 0;
    const startY = parseFloat(element.style.top) || 0;
    const startTime = performance.now();

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing cubic-out
        const easeProgress = 1 - Math.pow(1 - progress, 3);

        const currentX = startX + (targetX - startX) * easeProgress;
        const currentY = startY + (targetY - startY) * easeProgress;

        element.style.left = `${currentX}px`;
        element.style.top = `${currentY}px`;

        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }

    requestAnimationFrame(animate);
}

/**
 * Crée une explosion de confettis
 */
function createConfettiExplosion(x, y) {
    if (!ctx || !document.getElementById('confetti-switch').checked) return;

    setupCanvas();

    // Créer les particules
    for (let i = 0; i < 50; i++) {
        confetti.push(createConfettiParticle(x, y));
    }

    if (!animationId) {
        animateConfetti();
    }
}

/**
 * Crée une particule de confetti
 */
function createConfettiParticle(x, y) {
    return {
        x: x,
        y: y,
        dx: (Math.random() - 0.5) * 6,
        dy: -Math.random() * 4 - 2,
        width: Math.random() * 8 + 4,
        height: Math.random() * 8 + 4,
        angle: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.3,
        color: `hsl(${Math.random() * 360}, 70%, 60%)`,
        alpha: 1
    };
}

/**
 * Anime les confettis
 */
function animateConfetti() {
    if (!ctx) return;

    ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);

    confetti.forEach((particle, index) => {
        particle.x += particle.dx;
        particle.y += particle.dy;
        particle.dy += 0.2; // gravité
        particle.angle += particle.rotationSpeed;
        particle.alpha -= 0.008;

        ctx.save();
        ctx.globalAlpha = particle.alpha;
        ctx.translate(particle.x, particle.y);
        ctx.rotate(particle.angle);
        ctx.fillStyle = particle.color;
        ctx.fillRect(-particle.width / 2, -particle.height / 2, particle.width, particle.height);
        ctx.restore();

        if (particle.alpha <= 0 || particle.y > confettiCanvas.height) {
            confetti.splice(index, 1);
        }
    });

    if (confetti.length > 0) {
        animationId = requestAnimationFrame(animateConfetti);
    } else {
        animationId = null;
    }
}

/**
 * Obtient une position aléatoire pour un élément
 */
function getRandomPosition(element) {
    const margin = 60;
    const containerWidth = window.innerWidth;
    const containerHeight = window.innerHeight;
    const elementRect = element.getBoundingClientRect();

    const x = margin + Math.random() * (containerWidth - elementRect.width - 2 * margin);
    const y = margin + Math.random() * (containerHeight - elementRect.height - 2 * margin - 120);

    return { x, y };
}

// Effets CSS supplémentaires
const style = document.createElement('style');
style.textContent = `
    .pulse-effect {
        animation: pulse 0.5s ease-in-out;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }

    .spinning {
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(style);