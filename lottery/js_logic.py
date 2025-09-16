def get_javascript_logic():
    """
    Retourne la logique JavaScript complète de l'application.
    
    Returns:
        str: Code JavaScript
    """
    from config_loader import load_animation_config, generate_config_js
    
    # Charger la configuration
    config = load_animation_config()
    config_js = generate_config_js(config)
    
    return config_js + """
    const nameContainer = document.getElementById('name-container');
    const drawButton = document.getElementById('draw-button');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const peopleList = document.getElementById('people-list');
    const selectAllButton = document.getElementById('select-all');
    const deselectAllButton = document.getElementById('deselect-all');
    const drawModeSwitch = document.getElementById('draw-mode-switch');
    const winnersCountInput = document.getElementById('winners-count');
    const winnersCountDisplay = document.getElementById('winners-count-display');
    const confettiSwitch = document.getElementById('confetti-switch');

    let isDrawing = false;
    let shuffleInterval = null;
    let highlightInterval = null;
    let isInitialLoad = true;
    let gameState = 'idle'; // idle, drawing, exhausted
    let currentWinners = [];
    
    // Canvas confetti variables
    const confettiCanvas = document.getElementById('confetti-canvas');
    const ctx = confettiCanvas.getContext('2d');
    let confetti = [];
    let animationId = null;

    // Update switch labels based on state
    function updateSwitchLabels() {
        const withoutReplacement = document.getElementById('without-replacement');
        const withReplacement = document.getElementById('with-replacement');
        
        if (drawModeSwitch.checked) {
            withoutReplacement.classList.add('active');
            withoutReplacement.classList.remove('inactive');
            withReplacement.classList.add('inactive');
            withReplacement.classList.remove('active');
        } else {
            withReplacement.classList.add('active');
            withReplacement.classList.remove('inactive');
            withoutReplacement.classList.add('inactive');
            withoutReplacement.classList.remove('active');
        }
    }

    drawModeSwitch.addEventListener('change', updateSwitchLabels);

    winnersCountInput.addEventListener('input', () => {
        winnersCountDisplay.textContent = winnersCountInput.value;
        checkDrawButtonState();
    });

    function checkDrawButtonState() {
        if (gameState === 'exhausted') {
            drawButton.disabled = true;
            return;
        }
        
        const checkedCount = peopleList.querySelectorAll('input:checked').length;
        const winnersCount = parseInt(winnersCountInput.value, 10);
        const shouldDisable = checkedCount < winnersCount;
        
        drawButton.disabled = shouldDisable;
        
        if (!isDrawing) {
            if (shouldDisable) {
                drawButton.textContent = `🎲 Il faut au moins ${winnersCount} participant${winnersCount > 1 ? 's' : ''}`;
            } else {
                drawButton.textContent = '🎲 Tirage au sort';
            }
        }
    }

    function getRandomPosition(element, avoidOverlap = true) {
        const margin = 60;
        const containerWidth = window.innerWidth;
        const containerHeight = window.innerHeight;
        const elementRect = element.getBoundingClientRect();
        
        let attempts = 0;
        let x, y;
        
        do {
            x = margin + Math.random() * (containerWidth - elementRect.width - 2 * margin);
            y = margin + Math.random() * (containerHeight - elementRect.height - 2 * margin - 120);
            attempts++;
        } while (attempts < 20 && avoidOverlap && isPositionOccupied(x, y, element));
        
        return { x, y };
    }

    function getResponsivePosition(element) {
        const containerWidth = window.innerWidth;
        const containerHeight = window.innerHeight;
        const margin = Math.min(60, containerWidth * 0.05);
        const elementRect = element.getBoundingClientRect();
        
        const x = margin + Math.random() * (containerWidth - elementRect.width - 2 * margin);
        const y = margin + Math.random() * (containerHeight - elementRect.height - 2 * margin - 120);
        
        return { 
            x, 
            y,
            xPercent: (x / containerWidth) * 100,
            yPercent: (y / containerHeight) * 100
        };
    }

    function isPositionOccupied(x, y, currentElement) {
        const tags = Array.from(nameContainer.children);
        const threshold = 100;
        
        return tags.some(tag => {
            if (tag === currentElement) return false;
            const rect = tag.getBoundingClientRect();
            const tagX = parseFloat(tag.style.left);
            const tagY = parseFloat(tag.style.top);
            
            return Math.abs(x - tagX) < threshold && Math.abs(y - tagY) < threshold;
        });
    }

    function createSmoothMovement(element, targetX, targetY, duration = 600) {
        const startX = parseFloat(element.style.left) || 0;
        const startY = parseFloat(element.style.top) || 0;
        const startTime = performance.now();

        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Use easeOutCubic for smooth deceleration
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

    function initialDisplay() {
        nameContainer.innerHTML = '';
        const checkedPeople = Array.from(peopleList.querySelectorAll('input:checked')).map(cb => cb.value);

        checkedPeople.forEach((person, index) => {
            const tag = document.createElement('div');
            tag.classList.add('person-tag');
            tag.textContent = person;
            nameContainer.appendChild(tag);
            
            // Animation d'entrée depuis le haut de l'écran
            const finalPosition = getResponsivePosition(tag);
            const startY = -100 - Math.random() * 200;
            
            // Stocker la position en pourcentages pour le responsive
            tag.dataset.xPercent = finalPosition.xPercent;
            tag.dataset.yPercent = finalPosition.yPercent;
            
            // Position initiale
            tag.style.left = `${finalPosition.x}px`;
            tag.style.top = `${startY}px`;
            tag.style.opacity = '0';
            tag.style.transform = 'scale(0.8) rotate(-10deg)';
            
            // Animation vers la position finale avec délai
            setTimeout(() => {
                tag.style.transition = 'all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)';
                tag.style.top = `${finalPosition.y}px`;
                tag.style.opacity = '1';
                tag.style.transform = 'scale(1) rotate(0deg)';
                
                // Effet de rebond à l'arrivée
                setTimeout(() => {
                    tag.style.transform = 'scale(1.1) rotate(2deg)';
                    setTimeout(() => {
                        tag.style.transform = 'scale(1) rotate(0deg)';
                        tag.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                    }, 150);
                }, 300);
            }, index * 100 + Math.random() * 200);
        });
        
        isInitialLoad = false;
        checkDrawButtonState();
    }

    function updateDisplay() {
        const checkedPeople = Array.from(peopleList.querySelectorAll('input:checked')).map(cb => cb.value);
        const existingTags = Array.from(nameContainer.children);
        const existingPeople = existingTags.map(tag => tag.textContent);
        
        // Supprimer les étiquettes qui ne sont plus cochées
        existingTags.forEach(tag => {
            if (!checkedPeople.includes(tag.textContent)) {
                tag.style.transition = 'all 0.3s ease-out';
                tag.style.opacity = '0';
                tag.style.transform = 'scale(0.8)';
                setTimeout(() => tag.remove(), 300);
            }
        });
        
        // Ajouter les nouvelles étiquettes
        checkedPeople.forEach((person, index) => {
            if (!existingPeople.includes(person)) {
                const tag = document.createElement('div');
                tag.classList.add('person-tag');
                tag.textContent = person;
                nameContainer.appendChild(tag);
                
                // Animation d'entrée depuis le haut pour les nouvelles
                const finalPosition = getResponsivePosition(tag);
                const startY = -100;
                
                tag.dataset.xPercent = finalPosition.xPercent;
                tag.dataset.yPercent = finalPosition.yPercent;
                
                tag.style.left = `${finalPosition.x}px`;
                tag.style.top = `${startY}px`;
                tag.style.opacity = '0';
                tag.style.transform = 'scale(0.8)';
                
                setTimeout(() => {
                    tag.style.transition = 'all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
                    tag.style.top = `${finalPosition.y}px`;
                    tag.style.opacity = '1';
                    tag.style.transform = 'scale(1)';
                }, 100);
            }
        });
        
        checkDrawButtonState();
    }

    function displayPeople() {
        if (isInitialLoad) {
            initialDisplay();
        } else {
            updateDisplay();
        }
    }

    function startEnhancedShuffle(tags) {
        let shuffleCount = 0;
        const cfg = ANIMATION_CONFIG.shuffle;
        
        // Force layout recalculation before starting animations
        forceReflow();
        
        function performShuffle() {
            shuffleCount++;
            
            tags.forEach((tag, index) => {
                // Remove any lingering transitions
                tag.style.transition = 'none';
                
                // Add shuffling class for enhanced animation
                tag.classList.add('shuffling');
                
                // Create movement patterns using config
                const angle = (shuffleCount * cfg.angleIncrement + index * cfg.angleOffset) % 360;
                const radius = cfg.baseRadius + Math.sin(shuffleCount * cfg.radiusFrequency) * cfg.radiusVariation;
                const { x: baseX, y: baseY } = getRandomPosition(tag, false);
                
                // Apply offset multiplier for smoothness control
                const offsetX = Math.cos(angle * Math.PI / 180) * radius * cfg.offsetMultiplier;
                const offsetY = Math.sin(angle * Math.PI / 180) * radius * cfg.offsetMultiplier;
                
                createSmoothMovement(tag, baseX + offsetX, baseY + offsetY, cfg.movementDuration);
                
                // Apply pulse effect with configurable probability
                if (Math.random() < cfg.pulseProbability) {
                    tag.classList.add('pulse-effect');
                    setTimeout(() => tag.classList.remove('pulse-effect'), cfg.pulseDuration);
                }
            });
            
            if (shuffleCount < cfg.maxShuffles) {
                setTimeout(performShuffle, cfg.delayMin + Math.random() * cfg.delayVariation);
            } else {
                // Start highlight phase
                setTimeout(() => startHighlightPhase(tags), 300);
            }
        }
        
        // Start shuffle with a small delay to ensure proper initialization
        requestAnimationFrame(() => {
            performShuffle();
        });
    }

    function startHighlightPhase(tags) {
        let highlightRounds = 0;
        const cfg = ANIMATION_CONFIG.highlight;
        const winnersCount = parseInt(winnersCountInput.value, 10);
        
        function performHighlight() {
            // Remove previous highlights
            tags.forEach(tag => {
                tag.classList.remove('highlight', 'spinning');
            });
            
            // Randomly highlight some tags
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
                selectFinalWinners(tags);
            }
        }
        
        performHighlight();
    }

    // Canvas setup and resize handler
    function setupCanvas() {
        confettiCanvas.width = window.innerWidth;
        confettiCanvas.height = window.innerHeight;
    }
    
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
    
    function createConfettiExplosion(x, y) {
        if (!confettiSwitch || !confettiSwitch.checked) return;
        
        setupCanvas();
        
        // Create confetti particles
        for (let i = 0; i < 50; i++) {
            confetti.push(createConfettiParticle(x, y));
        }
        
        if (!animationId) {
            animateConfetti();
        }
    }
    
    function animateConfetti() {
        ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
        
        confetti.forEach((particle, index) => {
            particle.x += particle.dx;
            particle.y += particle.dy;
            particle.dy += 0.2; // gravity
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

    function selectFinalWinners(tags) {
        // Clear all animation classes
        tags.forEach(tag => {
            tag.classList.remove('shuffling', 'highlight', 'spinning', 'pulse-effect');
        });

        let drawablePeople = Array.from(peopleList.querySelectorAll('input:checked')).map(cb => cb.value);
        const winnersCount = parseInt(winnersCountInput.value, 10);

        if (drawablePeople.length < winnersCount) {
            alert("Pas assez de personnes sélectionnées pour le nombre de gagnants choisi.");
            isDrawing = false;
            gameState = 'idle';
            checkDrawButtonState();
            return;
        }

        const winners = [];
        for (let i = 0; i < winnersCount; i++) {
            const winnerIndex = Math.floor(Math.random() * drawablePeople.length);
            winners.push(drawablePeople[winnerIndex]);
            if (drawModeSwitch.checked) {
                drawablePeople.splice(winnerIndex, 1);
            }
        }

        const winnerTags = winners.map(winner => tags.find(tag => tag.textContent === winner));
        currentWinners = winnerTags;

        // Enhanced fade out for non-winners
        tags.forEach(tag => {
            if (!winnerTags.includes(tag)) {
                setTimeout(() => {
                    tag.classList.add('fade-out');
                    tag.style.opacity = '0.5';
                }, Math.random() * 500);
            }
        });

        // Apply winner styles and create confetti
        setTimeout(() => {
            winnerTags.forEach((tag, index) => {
                if (tag) {
                    setTimeout(() => {
                        tag.classList.add('winner');
                        
                        // Créer explosion de confettis depuis la position du gagnant
                        const rect = tag.getBoundingClientRect();
                        const centerX = rect.left + rect.width / 2;
                        const centerY = rect.top + rect.height / 2;
                        createConfettiExplosion(centerX, centerY);
                    }, index * 300);
                }
            });

            // Update checkboxes if drawing without replacement
            if (drawModeSwitch.checked) {
                winners.forEach(winner => {
                    const checkbox = peopleList.querySelector(`input[value="${winner}"]`);
                    if (checkbox) {
                        checkbox.checked = false;
                    }
                });
                
                // Vérifier si le mode sans remise est épuisé
                const remainingChecked = peopleList.querySelectorAll('input:checked').length;
                const nextWinnersCount = parseInt(winnersCountInput.value, 10);
                
                if (remainingChecked < nextWinnersCount) {
                    gameState = 'exhausted';
                    drawButton.textContent = '🎯 Plus de participants disponibles';
                    drawButton.disabled = true;
                }
            }

            setTimeout(() => {
                isDrawing = false;
                if (gameState !== 'exhausted') {
                    gameState = 'idle';
                }
                checkDrawButtonState();
            }, 1500 + (winnerTags.length * 300));

        }, 800);
    }

    function prepareForNextDraw() {
        // Gérer les gagnants précédents selon le mode
        if (drawModeSwitch.checked) {
            // Mode sans remise : les gagnants précédents ont déjà été décochés
            currentWinners.forEach(tag => {
                if (tag) {
                    tag.style.transition = 'all 0.5s ease-out';
                    tag.style.opacity = '0';
                    tag.style.transform = 'scale(0.8)';
                    setTimeout(() => tag.remove(), 500);
                }
            });
        } else {
            // Mode avec remise : réinitialiser le style des gagnants
            currentWinners.forEach(tag => {
                if (tag) {
                    tag.classList.remove('winner', 'fade-out');
                    tag.style.transform = 'scale(1)';
                    tag.style.opacity = '1';
                }
            });
        }
        
        // Réinitialiser les étiquettes en fade-out
        const fadedTags = nameContainer.querySelectorAll('.fade-out');
        fadedTags.forEach(tag => {
            tag.classList.remove('fade-out');
            tag.style.opacity = '1';
            tag.style.transform = 'scale(1)';
        });
        
        currentWinners = [];
    }

    function animateAndDraw() {
        if (isDrawing || gameState === 'exhausted') return;

        if (sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
        }

        gameState = 'drawing';

        // Préparer pour le prochain tirage
        if (!isInitialLoad) {
            prepareForNextDraw();
        }

        setTimeout(() => {
            const tags = Array.from(nameContainer.children);
            if (tags.length === 0) {
                alert("Veuillez sélectionner au moins une personne.");
                gameState = 'idle';
                return;
            }

            isDrawing = true;
            drawButton.disabled = true;
            drawButton.textContent = '🎲 Tirage en cours...';

            // Start the enhanced shuffle animation
            startEnhancedShuffle(tags);

        }, isInitialLoad ? 300 : 800);
    }

    function handleResize() {
        if (isDrawing) return;
        
        const tags = Array.from(nameContainer.children);
        tags.forEach(tag => {
            if (tag.dataset.xPercent && tag.dataset.yPercent) {
                const containerWidth = window.innerWidth;
                const containerHeight = window.innerHeight;
                const newX = (parseFloat(tag.dataset.xPercent) / 100) * containerWidth;
                const newY = (parseFloat(tag.dataset.yPercent) / 100) * containerHeight;
                
                tag.style.transition = 'all 0.3s ease-out';
                tag.style.left = `${newX}px`;
                tag.style.top = `${newY}px`;
            }
        });
    }

    let resizeTimeout;
    function debounceResize() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 250);
    }

    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    drawButton.addEventListener('click', animateAndDraw);

    peopleList.addEventListener('change', () => {
        if (!isDrawing) {
            displayPeople();
        }
    });

    winnersCountInput.addEventListener('input', checkDrawButtonState);

    selectAllButton.addEventListener('click', () => {
        const checkboxes = peopleList.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = true);
        displayPeople();
    });

    deselectAllButton.addEventListener('click', () => {
        const checkboxes = peopleList.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);
        displayPeople();
    });

    window.addEventListener('resize', () => {
        debounceResize();
        setupCanvas();
    });

    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target) && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
        }
    });

    // Gérer le changement de mode tirage
    drawModeSwitch.addEventListener('change', () => {
        updateSwitchLabels();
        
        // Si on passe en mode sans remise et qu'il y a déjà eu un tirage,
        // vérifier si il reste assez de participants
        if (drawModeSwitch.checked && currentWinners.length > 0) {
            const remainingChecked = peopleList.querySelectorAll('input:checked').length;
            const nextWinnersCount = parseInt(winnersCountInput.value, 10);
            
            if (remainingChecked < nextWinnersCount) {
                gameState = 'exhausted';
                drawButton.textContent = '🎯 Plus de participants disponibles';
                drawButton.disabled = true;
            }
        } else if (!drawModeSwitch.checked && gameState === 'exhausted') {
            // Si on repasse en mode avec remise, réactiver le bouton
            gameState = 'idle';
            drawButton.textContent = '🎲 Tirage au sort';
            checkDrawButtonState();
        }
    });

    // Initialize switch labels and canvas on load
    setupCanvas();
    updateSwitchLabels();
    
    // Function to force browser reflow/repaint
    function forceReflow() {
        // Force a reflow by reading offsetHeight
        document.body.offsetHeight;
        // Force style recalculation
        window.getComputedStyle(document.body).height;
    }
    
    // Ensure proper initialization after DOM is fully loaded
    function initializeApp() {
        // Disable transitions temporarily
        const style = document.createElement('style');
        style.textContent = '* { transition: none !important; }';
        document.head.appendChild(style);
        
        // Force reflow
        forceReflow();
        
        // Display people
        displayPeople();
        
        // Re-enable transitions after a short delay
        setTimeout(() => {
            style.remove();
            forceReflow();
        }, ANIMATION_CONFIG.general.transitionDisableDuration);
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(initializeApp, ANIMATION_CONFIG.general.initialDisplayDelay);
        });
    } else {
        setTimeout(initializeApp, ANIMATION_CONFIG.general.initialDisplayDelay);
    }
"""