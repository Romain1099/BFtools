import os
import requests

def main():
    # Récupération de la clé API depuis la variable d'environnement
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Erreur : La variable d'environnement OPENAI_API_KEY n'est pas définie.")
        return

    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Appel à l'API OpenAI
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur lors de l'appel API (code {response.status_code}) :")
        print(response.text)
        return

    data = response.json()
    models = data.get("data", [])

    # Création d'une sortie Markdown avec un tableau
    markdown_output = "# Liste des modèles OpenAI\n\n"
    markdown_output += f"Nombre total de modèles : **{len(models)}**\n\n"
    markdown_output += "| ID du modèle | Propriétaire |\n"
    markdown_output += "|--------------|--------------|\n"

    for model in models:
        model_id = model.get("id", "N/A")
        owned_by = model.get("owned_by", "N/A")
        markdown_output += f"| {model_id} | {owned_by} |\n"

    print(markdown_output)

if __name__ == "__main__":
    main()
