import json

class ColorManager:
    def __init__(self, config_path,widget,fontsize=12):
        """
        Initialise le gestionnaire de couleurs.

        Args:
            config_path (str): Chemin vers le fichier JSON contenant les configurations.
            widget: Le widget (ex. Text) à configurer.
        """
        self.colors = {}          # Dictionnaire pour les tags (couleurs et styles)
        self.global_config = {}   # Dictionnaire pour les contraintes globales
        self.fontsize = fontsize
        self.widget=widget
        self._load_config(config_path)


    def _load_config(self, config_path):
        """Charge les configurations (globales et tags) depuis le fichier JSON."""
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                config = json.load(file)
                self.global_config = config.get("global", {})
                self.colors = config.get("tags", {})
                self.fontsize = self.global_config.get("fontsize", 12)
        except FileNotFoundError:
            raise FileNotFoundError(f"Erreur : Le fichier de configuration '{config_path}' est introuvable.")

    def init_widget(self):
        """
        Initialise les paramètres globaux du widget (fond, curseur, sélection, etc.).

        
        """
        self.widget.configure(
            undo=self.global_config.get("undo", True),
            wrap=self.global_config.get("wrap", "word"),
            background=self.global_config.get("background", "#2e2e2e"),
            foreground=self.global_config.get("foreground", "#ffffff"),
            insertbackground=self.global_config.get("insertbackground", "#ffffff"),
            selectbackground=self.global_config.get("selectbackground", "#4a4a4a"),
            selectforeground=self.global_config.get("selectforeground", "#ffffff")
        )

    def apply_tag_colors(self):
        """
        Applique uniquement les couleurs et styles pour le texte via les tags.


        """
        for tag_name, config in self.colors.items():
            self.widget.tag_configure(
                tag_name,
                foreground=config.get("foreground", "#FFFFFF"),
                font=("Fira Code", self.fontsize, config.get("style", "normal"))
            )

    def update_fontsize(self, new_size):
        """
        Met à jour dynamiquement la taille de police pour les tags et reconfigure.

        Args:
            new_size (int): Nouvelle taille de police.
        """
        self.fontsize = new_size
        self.apply_tag_colors(self.widget)
