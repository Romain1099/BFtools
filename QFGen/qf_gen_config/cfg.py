import os

def read_api_key():
    """Lit la clé API OpenAI depuis api_key.txt"""
    api_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_key.txt")
    if os.path.exists(api_key_file):
        with open(api_key_file, 'r') as file:
            for line in file:
                if line.startswith('OPENAI_API_KEY='):
                    # Extraire la valeur entre guillemets
                    return line.split('=', 1)[1].strip()
    return None

def read_tcl_path():
    """Lit le chemin TCL_LIBRARY depuis tcl_path.txt"""
    tcl_path_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tcl_path.txt")
    if os.path.exists(tcl_path_file):
        with open(tcl_path_file, 'r') as file:
            return file.read().strip()
    return None

def write_tcl_path(tcl_path):
    """Écrit le chemin TCL_LIBRARY dans tcl_path.txt"""
    tcl_path_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tcl_path.txt")
    with open(tcl_path_file, 'w') as file:
        file.write(tcl_path)

def read_claude_api_key():
    """Lit la clé API Claude/Anthropic depuis api_key.txt"""
    api_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_key.txt")
    if os.path.exists(api_key_file):
        with open(api_key_file, 'r') as file:
            for line in file:
                if line.startswith('ANTHROPIC_API_KEY='):
                    # Extraire la valeur entre guillemets
                    return line.split('=', 1)[1].strip()
    return None

def read_ai_provider():
    """Lit le provider AI à utiliser (openai ou claude). Par défaut: claude"""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_provider.txt")
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            for line in file:
                if line.startswith('PROVIDER='):
                    provider = line.split('=', 1)[1].strip().lower()
                    if provider in ['openai', 'claude']:
                        return provider
    return 'claude'  # Par défaut

def read_ai_model(provider=None):
    """Lit le modèle AI à utiliser selon le provider.

    Args:
        provider: 'claude' ou 'openai'. Si None, détecte automatiquement.

    Returns:
        Le nom du modèle configuré ou le modèle par défaut.
    """
    if provider is None:
        provider = read_ai_provider()

    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_provider.txt")

    # Modèles par défaut
    default_models = {
        'claude': 'claude-sonnet-4-5-20250929',
        'openai': 'gpt-5-2025-08-07'
    }

    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            for line in file:
                if provider == 'claude' and line.startswith('CLAUDE_MODEL='):
                    return line.split('=', 1)[1].strip()
                elif provider == 'openai' and line.startswith('OPENAI_MODEL='):
                    return line.split('=', 1)[1].strip()

    return default_models.get(provider, default_models['claude'])

def write_ai_provider(provider):
    """Écrit le provider AI à utiliser (openai ou claude)"""
    if provider.lower() not in ['openai', 'claude']:
        raise ValueError("Provider doit être 'openai' ou 'claude'")
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_provider.txt")
    with open(config_file, 'w') as file:
        file.write(provider.lower())

if __name__=="__main__":
    APIKEY=read_api_key()
