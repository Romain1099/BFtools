
import os
import re
import json
class PSManager():
    """
    Un classe qui gère les prompts donnés aux IA pour permettre la souplesse d'utilisation.
    """
    def __init__(self):
        config_path= os.path.join(os.path.dirname(os.path.abspath(__file__)),"qf_gen_config/prompts.txt")
        content=""
        try:
            with open(config_path,'r',encoding='utf-8') as file:
                content=file.read()
        except:
            raise FileNotFoundError(f"Le fichier {config_path} n'a pas été trouvé")
        try:
            self.prompts_dict=self.get_prompts(content)
        except:
            raise ValueError(f"Contenu des prompts introuvables : {content}")
    
    def get_prompts(self, content)->dict:
        """
        Parse le contenu du fichier pour récupérer les prompts formatés comme :
        
        nom_variable = '''
        contenu du prompt sur plusieurs lignes
        '''
        """
        # Expression régulière pour extraire les noms de variable et leurs valeurs (contenu entre triples quotes)
        pattern = re.compile(r"(\w+)\s*=\s*'''(.*?)'''", re.DOTALL)

        # Recherche des correspondances et conversion en dictionnaire
        prompts = {match[0]: match[1].strip() for match in pattern.findall(content)}

        # Vérification : le fichier doit contenir au moins une variable
        if not prompts:
            raise ValueError("Aucune variable valide trouvée dans le fichier de prompts.")
        
        return prompts
    
if __name__=="__main__":
    ps=PSManager()
    print(ps.prompts_dict["short_answer_prompt"])