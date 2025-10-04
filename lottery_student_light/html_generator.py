from css_styles import get_css_styles
from js_logic import get_javascript_logic

def generate_html_structure(people_checkboxes):
    """
    Génère la structure HTML complète de l'application.
    
    Args:
        people_checkboxes (str): HTML des checkboxes pour les personnes
        
    Returns:
        str: HTML complet
    """
    css_styles = get_css_styles()
    javascript_logic = get_javascript_logic()
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tirage au sort</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        {css_styles}
    </style>
</head>
<body>

<button id="sidebar-toggle">&#9776;</button>

<div id="sidebar">
    <h3>Paramètres</h3>
    
    <div class="setting-row">
        <span id="without-replacement">Sans remise</span>
        <label class="switch">
            <input type="checkbox" id="draw-mode-switch" checked>
            <span class="slider"></span>
        </label>
        <span id="with-replacement">Avec remise</span>
    </div>
    
    <hr>
    
    <div class="range-container">
        <div class="range-label">
            <span>Nombre de choix/tirage</span>
            <span id="winners-count-display">1</span>
        </div>
        <div class="range-slider-container">
            <span>1</span>
            <input type="range" id="winners-count" value="1" min="1" max="4" step="1">
            <span>4</span>
        </div>
    </div>
    
    <hr>
    
    <div class="confetti-container-toggle">
        <div class="confetti-label">
            <span>Confettis 🎉</span>
            <label class="switch">
                <input type="checkbox" id="confetti-switch" checked>
                <span class="slider"></span>
            </label>
        </div>
    </div>
    
    <hr>
    
    <div style="display:flex;justify-content: space-between;align-items: center;margin-bottom:10px;">
    <h4>Liste</h4>
    <div class="button-group">
        <button id="select-all" title="Tout cocher">
            <svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 509 512.123" width="20" height="20" fill="currentColor"><path fill-rule="nonzero" d="M62.282 0h323.575c34.292 0 62.283 27.991 62.283 62.283v322.76c0 34.292-27.991 62.282-62.283 62.282H62.282C27.99 447.325 0 419.335 0 385.043V62.283C0 27.991 27.99 0 62.282 0zm56.183 246.083c-8.285-10.729-6.304-26.144 4.425-34.43 10.729-8.286 26.144-6.305 34.43 4.424l26.972 34.79L292.84 142.07c9.56-9.613 25.105-9.656 34.718-.096 9.614 9.56 9.657 25.105.096 34.719L199.386 305.255a24.983 24.983 0 01-2.405 2.116c-10.729 8.286-26.144 6.305-34.43-4.424l-44.086-56.864zm353.177-164.28a103.085 103.085 0 017.464 6.765C497.551 107.013 509 132.47 509 160.487v249.824c0 56.03-45.781 101.812-101.812 101.812H162.671c-28.016 0-53.474-11.449-71.918-29.894a103.041 103.041 0 01-6.764-7.462h323.199c34.81 0 63.6-28.117 64.438-62.901h.016v-1.141l.003-.414V160.487l-.003-.414v-78.27zm-85.785-44.448H62.282c-13.674 0-24.927 11.254-24.927 24.928v322.76c0 13.674 11.253 24.928 24.927 24.928h323.575c13.674 0 24.928-11.254 24.928-24.928V62.283c0-13.674-11.254-24.928-24.928-24.928z"/></svg>        
        </button>
        <button id="deselect-all" title="Tout décocher">
             <svg xmlns="http://www.w3.org/2000/svg"
                   shape-rendering="geometricPrecision"
                   text-rendering="geometricPrecision"
                   image-rendering="optimizeQuality"
                   fill-rule="evenodd"
                   clip-rule="evenodd"
                   viewBox="0 0 509 512.123"
                   width="20" height="20" fill="currentColor">
                <path fill-rule="nonzero"
                      d="M62.283 0h323.575c34.292 0 62.282 27.991 62.282 62.283v322.76c0 34.292-27.99 62.282-62.282 62.282H62.283C27.991 447.325 0 419.335 0 385.043V62.283C0 27.991 27.991 0 62.283 0zm409.36 81.803a103.296 103.296 0 017.464 6.765C497.551 107.013 509 132.47 509 160.487v249.824c0 56.03-45.781 101.812-101.812 101.812H162.671c-28.016 0-53.473-11.449-71.918-29.894a102.796 102.796 0 01-6.763-7.462h323.198c34.81 0 63.6-28.117 64.438-62.901h.017v-1.141l.002-.414V160.487l-.002-.414v-78.27zm-85.785-44.448H62.283c-13.674 0-24.928 11.254-24.928 24.928v322.76c0 13.674 11.254 24.928 24.928 24.928h323.575c13.674 0 24.927-11.254 24.927-24.928V62.283c0-13.674-11.253-24.928-24.927-24.928z"/>
              </svg>         
        </button>
    </div>
    </div>
    <div id="people-list">
        {people_checkboxes}
    </div>
</div>

<div id="name-container"></div>
<canvas id="confetti-canvas"></canvas>
<button id="draw-button">🎲 Tirage au sort</button>

<script>
{javascript_logic}
</script>

</body>
</html>
"""
    return html_content

def save_html_file(html_content, filename='index.html'):
    """
    Sauvegarde le contenu HTML dans un fichier.
    
    Args:
        html_content (str): Contenu HTML à sauvegarder
        filename (str): Nom du fichier de sortie
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Le fichier {filename} a été généré avec succès.")