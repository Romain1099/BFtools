import openai
import customtkinter as ctk
from threading import Thread
import re
import json
import time
import asyncio
from anthropic import AsyncAnthropic
from latexhighlighter.tex_highlighter import PdfViewer,LatexText
from latexhighlighter.latexcompiler import LaTeXCompiler
from qf_gen_config.cfg import read_api_key, read_claude_api_key, read_ai_provider, read_ai_model
from prompt_system_manager import PSManager
#from latexhighlighter.latex_modifier import LaTeXModifier

class QuestionGenerator:
    def __init__(self, api_key, widget_question, widget_answer_short, widget_answer_details,widget_theme):
        # Détection du provider AI
        self.ai_provider = read_ai_provider()
        self.ai_model = read_ai_model(self.ai_provider)

        # Configuration selon le provider
        self.claude_client = None
        if self.ai_provider == 'claude':
            self.claude_api_key = read_claude_api_key()
            if not self.claude_api_key:
                raise ValueError("Clé API Claude non trouvée dans qf_gen_config/api_key.txt")
            # Client initialisé de manière lazy
        else:  # openai
            openai.api_key = api_key

        self.widget_question = widget_question
        self.widget_answer_short = widget_answer_short
        self.widget_answer_details = widget_answer_details
        self.widget_theme = widget_theme
        self.prompts_dict=self.load_prompts()

    def _get_claude_client(self):
        """Initialisation lazy du client Claude pour éviter les erreurs au démarrage"""
        if self.claude_client is None:
            try:
                self.claude_client = AsyncAnthropic(api_key=self.claude_api_key.strip().strip('"'))
            except Exception as e:
                raise ValueError(f"Erreur lors de l'initialisation du client Claude: {e}")
        return self.claude_client

    def load_prompts(self):
        self.prompt_manager=PSManager()
        return self.prompt_manager.prompts_dict
    def generate_questions(self,classe, date, conditions, callback):
        #preprompt, prompt = self.create_prompt(classe, date, conditions)
        attempts = 0
        max_attempts = 1
        self.question_generated=False
        self.long_answer_generated=False
        self.short_answer_generated=False
        self.theme_generated=False

        while attempts < max_attempts:
            try:
                # Generate question code
                question_code = self.generate_question_code(conditions)

                # Generate long answer code
                if self.widget_answer_details:
                    long_answer_code = self.generate_long_answer_code(question_code)

                # Generate short answer code
                if self.widget_answer_short:
                    short_answer_code = self.generate_short_code(long_answer_code)

                if self.widget_theme:
                    short_theme=self.generate_short_theme(question_code)
                # Display the results in the widgets
                #self.display_response(question_code, long_answer_code, short_answer_code)
                break
            except Exception as e:
                attempts += 1
                error_msg = f"Error with {self.ai_provider}: {e}. Attempt {attempts}/{max_attempts}"
                self.update_result_text(callback, error_msg)
                time.sleep(2)
        if attempts == max_attempts:
            self.update_result_text(callback, "Failed to generate questions after several attempts. Please try again later.")

    def create_prompt(self, classe, date, conditions):
        conditions_text = "\n".join(conditions)
        preprompt = f"""
        Créez l'un des trois éléments pour mes questions de mathématiques pour la classe {classe}, à la date du {date}. Les questions doivent répondre aux conditions suivantes :

        {conditions_text}
        """
        prompt = """
        Si on demande une question sur les équations, il faudra réponse par exemple : "Résoudre l'\\textbf{équation} suivante : \\n\\[\\n2x-10=5x+1\\n\\]",
        Si on demande la réponse détaillée à la question ci-dessus, il faudra réponse par exemple : "\\begin{align*}\\n    2x-10&=5x+11\\\\\\n    2x - 10 + 10 &=5x+11+10\\\\\\n    2x-5x&=5x+21-5x\\\\\\n    -3x&=21\\\\\\n    x&=\\dfrac{21}{-3}=\\mathbf{-7}\\n\\end{align*}\\n\\nLa solution de l'équation est donc : $x=-7$"
        Si on demande une réponse très courte par rapport à l'équation précédente, il faudra réponse par exemple : "$x=-7$",
            
        """
        return preprompt, prompt

    def generate_question_code(self, prompt):
        """Méthode façade qui choisit l'implémentation selon le provider"""
        if self.ai_provider == 'claude':
            return asyncio.run(self._generate_question_code_claude(prompt))
        else:
            return self._generate_question_code_openai(prompt)

    def _generate_question_code_openai(self, prompt):
        """Implémentation OpenAI pour generate_question_code"""
        question_prompt= self.prompts_dict["question_prompt"]
        response = openai.ChatCompletion.create(
            model=self.ai_model,
            messages=[
                {"role": "system", "content": f"{question_prompt}"},
                {"role": "user", "content": f"{prompt}"}
            ],
            stream=True,
        )
        question_code = ""
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                question_code += chunk.choices[0].delta.content
                self.update_widget(self.widget_question, chunk.choices[0].delta.content)

        return question_code

    async def _generate_question_code_claude(self, prompt):
        """Implémentation Claude pour generate_question_code"""
        question_prompt = self.prompts_dict["question_prompt"]
        question_code = ""
        client = self._get_claude_client()

        # Convertir prompt en string si c'est une liste
        prompt_str = "\n".join(prompt) if isinstance(prompt, list) else str(prompt)

        async with client.messages.stream(
            model=self.ai_model,
            max_tokens=8000,
            system=question_prompt,
            messages=[{"role": "user", "content": prompt_str}]
        ) as stream:
            async for text_chunk in stream.text_stream:
                question_code += text_chunk
                self.update_widget(self.widget_question, text_chunk)

        return question_code
    def generate_one_question(self,prompt,widget):
        """Méthode façade qui choisit l'implémentation selon le provider"""
        if self.ai_provider == 'claude':
            return asyncio.run(self._generate_one_question_claude(prompt, widget))
        else:
            return self._generate_one_question_openai(prompt, widget)

    def _generate_one_question_openai(self, prompt, widget):
        """Implémentation OpenAI pour generate_one_question"""
        response = openai.ChatCompletion.create(
            model=self.ai_model,
            messages=[
                {"role": "system", "content": f"{self.prompts_dict['master_prompt']}"},
                {"role": "system", "content": f"{prompt}"}
            ],
            stream=True,
        )
        question_code = ""
        widget.delete("1.0", "end")
        widget.insert("1.0","Votre demande en cours de réalisation...")
        contents=[]
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                question_code += chunk.choices[0].delta.content
                contents.append(chunk.choices[0].delta.content)

        widget.delete("1.0", "end")
        widget.insert("1.0",''.join(contents))

        return question_code

    async def _generate_one_question_claude(self, prompt, widget):
        """Implémentation Claude pour generate_one_question"""
        question_code = ""
        widget.delete("1.0", "end")
        widget.insert("1.0","Votre demande en cours de réalisation...")
        contents = []

        # Convertir prompt en string si c'est une liste
        prompt_str = "\n".join(prompt) if isinstance(prompt, list) else str(prompt)

        client = self._get_claude_client()
        async with client.messages.stream(
            model=self.ai_model,
            max_tokens=8000,
            system=self.prompts_dict['master_prompt'],
            messages=[{"role": "user", "content": prompt_str}]
        ) as stream:
            async for text_chunk in stream.text_stream:
                question_code += text_chunk
                contents.append(text_chunk)

        widget.delete("1.0", "end")
        widget.insert("1.0",''.join(contents))

        return question_code
    def generate_long_answer_code(self, question_code):
        """Méthode façade qui choisit l'implémentation selon le provider"""
        if self.ai_provider == 'claude':
            return asyncio.run(self._generate_long_answer_code_claude(question_code))
        else:
            return self._generate_long_answer_code_openai(question_code)

    def _generate_long_answer_code_openai(self, question_code):
        """Implémentation OpenAI pour generate_long_answer_code"""
        long_answer_prompt=self.prompts_dict["long_answer_prompt"]

        response = openai.ChatCompletion.create(
            model=self.ai_model,
            messages=[
                {"role": "system", "content": f"{long_answer_prompt}"},
                {"role": "user", "content": f"{question_code}"}
            ],
            stream=True,
        )
        long_answer_code = ""
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                long_answer_code += chunk.choices[0].delta.content
                self.update_widget(self.widget_answer_details, chunk.choices[0].delta.content)

        return long_answer_code

    async def _generate_long_answer_code_claude(self, question_code):
        """Implémentation Claude pour generate_long_answer_code"""
        long_answer_prompt = self.prompts_dict["long_answer_prompt"]
        long_answer_code = ""

        client = self._get_claude_client()
        async with client.messages.stream(
            model=self.ai_model,
            max_tokens=8000,
            system=long_answer_prompt,
            messages=[{"role": "user", "content": question_code}]
        ) as stream:
            async for text_chunk in stream.text_stream:
                long_answer_code += text_chunk
                self.update_widget(self.widget_answer_details, text_chunk)

        return long_answer_code

    def generate_short_code(self, long_answer_code):
        """Méthode façade qui choisit l'implémentation selon le provider"""
        if self.ai_provider == 'claude':
            return asyncio.run(self._generate_short_code_claude(long_answer_code))
        else:
            return self._generate_short_code_openai(long_answer_code)

    def _generate_short_code_openai(self, long_answer_code):
        """Implémentation OpenAI pour generate_short_code"""
        short_answer_prompt=self.prompts_dict["short_answer_prompt"]

        response = openai.ChatCompletion.create(
            model=self.ai_model,
            messages=[
                {"role": "system", "content": f"{short_answer_prompt}"},
                {"role": "user", "content": f"{long_answer_code}"}
            ],
            stream=True,
        )
        short_answer_code = ""
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                short_answer_code += chunk.choices[0].delta.content
                self.update_widget(self.widget_answer_short, chunk.choices[0].delta.content)

        return short_answer_code

    async def _generate_short_code_claude(self, long_answer_code):
        """Implémentation Claude pour generate_short_code"""
        short_answer_prompt = self.prompts_dict["short_answer_prompt"]
        short_answer_code = ""

        client = self._get_claude_client()
        async with client.messages.stream(
            model=self.ai_model,
            max_tokens=8000,
            system=short_answer_prompt,
            messages=[{"role": "user", "content": long_answer_code}]
        ) as stream:
            async for text_chunk in stream.text_stream:
                short_answer_code += text_chunk
                self.update_widget(self.widget_answer_short, text_chunk)

        return short_answer_code
    def generate_short_theme(self, question_code):
        """Méthode façade qui choisit l'implémentation selon le provider"""
        if self.ai_provider == 'claude':
            return asyncio.run(self._generate_short_theme_claude(question_code))
        else:
            return self._generate_short_theme_openai(question_code)

    def _generate_short_theme_openai(self, question_code):
        """Implémentation OpenAI pour generate_short_theme"""
        short_theme_prompt=self.prompts_dict["short_theme_prompt"]
        response = openai.ChatCompletion.create(
            model=self.ai_model,
            messages=[
                {"role": "system", "content": f"{short_theme_prompt}"},
                {"role": "user", "content": f"{question_code}"}
            ],
            stream=True,
        )
        short_theme_code = ""
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                short_theme_code += chunk.choices[0].delta.content
                self.update_widget(self.widget_theme, chunk.choices[0].delta.content)

        return short_theme_code

    async def _generate_short_theme_claude(self, question_code):
        """Implémentation Claude pour generate_short_theme"""
        short_theme_prompt = self.prompts_dict["short_theme_prompt"]
        short_theme_code = ""

        client = self._get_claude_client()
        async with client.messages.stream(
            model=self.ai_model,
            max_tokens=8000,
            system=short_theme_prompt,
            messages=[{"role": "user", "content": question_code}]
        ) as stream:
            async for text_chunk in stream.text_stream:
                short_theme_code += text_chunk
                self.update_widget(self.widget_theme, text_chunk)

        return short_theme_code

    def update_widget(self, widget, content):
        try: 
            widget.insert_without_highlight("end", content)
            widget.update_idletasks()
        except:
            widget.insert("end", content)
            widget.update_idletasks()

    def update_result_text(self, callback, text):
        callback(text)

    def display_response(self, question_code, long_answer_code, short_answer_code,theme_code):
        self.widget_question.delete("1.0", "end")
        self.widget_question.insert("1.0", question_code)
        self.widget_answer_short.delete("1.0", "end")
        self.widget_answer_short.insert("1.0", short_answer_code)
        self.widget_answer_details.delete("1.0", "end")
        self.widget_answer_details.insert("1.0", long_answer_code)
        self.widget_theme.insert("1.0",theme_code)

class QuestionJsonGenerator:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.ai_provider = read_ai_provider()
        self.ai_model = read_ai_model(self.ai_provider)

    def generate_questions(self, classe, date, conditions, callback):
        preprompt,prompt = self.create_prompt(classe, date, conditions)
        attempts = 0
        max_attempts = 1
        fake_demand="Une question de numération sur le vocabulaire 'doubles', triples, etc.. ; une autre de proportionnalité pour calculer une distance à partir de vitesses ; et enfin une sur les fractions et le repérage sur un axe gradué."
        example={"QF_05_06_2024": {
                "classe": "6ème",
                "date": "05/06/2024",
                "questions": {
                    "question1": {
                        "enonce": "Quel est le triple de $31{,}9$ ?",
                        "reponse": "$95{,}7$",
                        "details": "Le triple de $31{,}9$ est $3 \\times 31{,}9=95{,}7$",
                        "theme": "Numération"
                    },
                    "question2": {
                        "enonce": "Une voiture roule à une vitesse constante de $100$ km/h. \\\\\nCombien de kilomètres parcourt-elle en\\\\ $1$ h et $30$ min ?",
                        "reponse": "$150$ km",
                        "details": "$100\\times 1{,}5 = 150$ km",
                        "theme": "Proportionnalité - Durées"
                    },
                    "question3": {
                        "enonce": "Déterminer l'abscisse du point A situé ci-dessous :\\\\\\begin{tikzpicture}[baseline,scale = 0.5]\n\n    \\tikzset{\n      point/.style={\n        thick,\n        draw,\n        cross out,\n        inner sep=0pt,\n        minimum width=5pt,\n        minimum height=5pt,\n      },\n    }\n    \\clip (-1,-1) rectangle (14,1.5);\n    \t\\draw[color ={black},line width = 2,|->] (0,0)--(13.100000000000001,0);\n\t\\draw[color ={black},line width = 2] (0,-0.25)--(0,0.25);\n\t\\draw[color ={black},opacity = 0.8] (0.75,-0.16666666666666666)--(0.75,0.16666666666666666);\n\t\\draw[color ={black},opacity = 0.8] (1.5,-0.16666666666666666)--(1.5,0.16666666666666666);\n\t\\draw[color ={black},opacity = 0.8] (2.25,-0.16666666666666666)--(2.25,0.16666666666666666);\n\t\\draw[color ={black},line width = 2] (3,-0.25)--(3,0.25);\n\t\\draw[color ={black},opacity = 0.8] (3.75,-0.16666666666666666)--(3.75,0.16666666666666666);\n\t\\draw[color ={black},opacity = 0.8] (4.5,-0.16666666666666666)--(4.5,0.16666666666666666);\n\t\\draw[color ={black},opacity = 0.8] (5.25,-0.16666666666666666)--(5.25,0.16666666666666666);\n\t\\draw[color ={black},line width = 2] (6,-0.25)--(6,0.25);\n\t\\draw[color ={black},opacity = 0.8] (6.75,-0.16666666666666666)--(6.75,0.16666666666666666);\n\t\\draw[color ={black},opacity = 0.8] (7.5,-0.16666666666666666)--(7.5,0.16666666666666666);\n\t\\draw[color ={black},opacity = 0.8] (8.25,-0.16666666666666666)--(8.25,0.16666666666666666);\n\t\\draw[color ={black},line width = 2] (9,-0.25)--(9,0.25);\n\t\\draw[color ={black},opacity = 0.8] (9.75,-0.16666666666666666)--(9.75,0.16666666666666666);\n\t\\draw[color ={black},opacity = 0.8] (10.5,-0.16666666666666666)--(10.5,0.16666666666666666);\n\t\\draw[color ={black},opacity = 0.8] (11.25,-0.16666666666666666)--(11.25,0.16666666666666666);\n\t\\draw[color ={black},line width = 2] (12,-0.25)--(12,0.25);\n\t\\draw (0,-0.7) node[anchor = center] {\\footnotesize \\color{black}{$0$}};\n\t\\draw (3,-0.7) node[anchor = center] {\\footnotesize \\color{black}{$1$}};\n\t\\draw (6,-0.7) node[anchor = center] {\\footnotesize \\color{black}{$2$}};\n\t\\draw (9,-0.7) node[anchor = center] {\\footnotesize \\color{black}{$3$}};\n\t\\draw (12,-0.7) node[anchor = center] {\\footnotesize \\color{black}{$4$}};\n\t\\draw[color ={{blue}},line width = 1.25,opacity = 0.8] (4.25,0.25)--(4.75,-0.25);\\draw[color ={{blue}},line width = 1.25,opacity = 0.8] (4.25,-0.25)--(4.75,0.25);\n\t\\draw (4.5,0.8) node[anchor = center] {\\normalsize \\color{blue}{$A$}};\n\n\\end{tikzpicture}",
                        "reponse": "$\\dfrac{6}{4}$",
                        "details": "L'abscisse du point A est $\\dfrac{6}{4}$",
                        "theme": "Numération - Fractions"
                    }
                }
            }
        }
        
        while attempts < max_attempts:
            try:
                response = openai.ChatCompletion.create(
                    model=self.ai_model,
                    messages=[
                        {"role": "system", "content": f"Tu est le manager de ma base de données json qui gère du contenu LaTeX. Tu dois produire un json valide et répondant au maximum de demande de l'utilisateur.\n {preprompt}"},
                        #{"role":"user","content":fake_demand},
                        #{"role":"assistant","content":example},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={
                        "type": "json_object",
                    },
                    stream=True,
                )
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.get("content"):
                        full_response += chunk.choices[0].delta.content
                        self.update_result_text(callback, chunk.choices[0].delta.content)
                json_cleaner=JSONCleaner()
                json_content = json_cleaner.extract_and_clean_json(full_response)
                if json_content:
                    self.update_result_text(callback, f"\n\nExtracted JSON:\n{json_content}")
                    print(json_content)
                break
            except Exception as e:
                attempts += 1
                error_msg = f"Error with {self.ai_provider}: {e}. Attempt {attempts}/{max_attempts}"
                self.update_result_text(callback, error_msg)
                time.sleep(2)
        if attempts == max_attempts:
            self.update_result_text(callback, "Failed to generate questions after several attempts. Please try again later.")



    def create_prompt(self, classe, date, conditions):
        conditions_text = "\n".join(conditions)
        preprompt = f"""
        Créez une série de trois questions de mathématiques pour la classe {classe}, à la date du {date}. Les questions doivent répondre aux conditions suivantes :

        {conditions_text}
        """
        prompt = {
            f"QF_{date.replace('/', '_')}": {
                "classe": classe,
                "date": date,
                "questions": {
                    "question1": {
                        "enonce": "Résoudre l'\\textbf{équation} : \\n\\[\\n2x-10=5x+1\\n\\]",
                        "reponse": "$x=-7$",
                        "details": "\\begin{align*}\\n    2x-10&=5x+11\\\\\\n    2x - 10 + 10 &=5x+11+10\\\\\\n    2x-5x&=5x+21-5x\\\\\\n    -3x&=21\\\\\\n    x&=\\dfrac{21}{-3}=\\mathbf{-7}\\n\\end{align*}\\n\\nLa solution de l'équation est donc : $x=-7$",
                        "theme": "Equations"
                    },
                    "question2": {
                        "enonce": "En moto, j'ai fait $172{,}8$ km en $3$h $12$min, ma vitesse en km/h est de …",
                        "reponse": "$54\\text{km}/\\text{h}$",
                        "details": "$12$ minutes représentent $\\dfrac{12}{60}=0{,}2$h.\\\\\\nAinsi :  $3$h $12$min = $3{,}2$h. \\\\\nLa vitesse cherchée est donc de : \\n\\[\\n    \\dfrac{172{,}8}{3{,}2}=54\\text{km}/\\text{h}\\n\\]",
                        "theme": "Vitesses"
                    },
                    "question3": {
                        "enonce": "On considère la fonction $f:x \\mapsto -7x$. \\\\\\n\\textbf{a.} Calculer l'\\textbf{image} de 6 par la fonction $f$. \\\\\\n\\textbf{b.} Quelle est la nature de cette fonction ?",
                        "reponse": "\\textbf{a.} $f(6)=-42$ \\n\\textbf{b.} fonction \\textbf{linéaire}",
                        "details": "\\textbf{a.} On remplace $x$ par $6$ dans l'expression de la fonction : \\\\\\n$f(6)= -7\\times 6 = -42 $\\n\\n\\textbf{b.} L'expression de cette fonction est de la forme $x \\mapsto ax$.\\\\\\nC'est une fonction \\textbf{linéaire}",
                        "theme": "Fonctions"
                    }
                }
            }
        }
        return preprompt,json.dumps(prompt, ensure_ascii=False, indent=4)


    def update_result_text(self, callback, text):
        callback(text)
class JSONCleaner:
    def extract_and_clean_json(self, response_text):
        match = re.search(r"```json(.*?)```", response_text, re.DOTALL)
        if not match:
            match = re.search(r"```json(.*)", response_text, re.DOTALL)
        
        if match:
            json_content = match.group(1).strip(' ')
            json_content.replace("\\n    \{\\n        ","")
            json_content = self.replace_special_json_characters(json_content)

            json_content = self.replace_special_characters(json_content)
            # json_content = self.make_entries_oneline(json_content) # à implémenter si nécessaire
            print(fr"{json_content}")
            # Tentative de parsing initial
            try:
                parsed_json = json.loads(json_content)
                return parsed_json
            except json.JSONDecodeError as e:
                print(f"Erreur lors du parsing du JSON : {e}")
                return None
        return None

    def replace_special_json_characters(self, json_content):
        replacements = {
            "\\": "\\\\",
            "\n": "\\n",
        }
        
        for old, new in replacements.items():
            json_content = json_content.replace(old, new)
        return json_content
    def make_entries_oneline(self, json_content):
        # Utiliser une expression régulière pour capturer le contenu entre les accolades du dictionnaire
        pattern = r'({.*?})'
        matches = re.findall(pattern, json_content, re.DOTALL)

        # Remplacer les sauts de ligne par \n dans chaque match
        for match in matches:
            oneline_entry = match.replace('\n', '\\n').replace('\r', '\\n')
            json_content = json_content.replace(match, oneline_entry)
        
        return json_content
    
    def replace_special_characters(self, text):
        replacements = {
            '€': '\\euro{}'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def repair_json(self, json_content, error):
        error_msg = str(error)
        match = re.search(r"line (\d+) column (\d+)", error_msg)
        if not match:
            return "Error: Failed to parse JSON content and couldn't locate the issue."

        line, column = int(match.group(1)), int(match.group(2))

        # Tentative de couper le contenu JSON jusqu'à la position de l'erreur
        lines = json_content.split(' ')
        if line > len(lines):
            return "Error: Line number out of range."
        lines = lines[:line]
        json_content = ' '.join(lines)

        try:
            parsed_json = json.loads(json_content)
            return json.dumps(parsed_json, indent=4)
        except json.JSONDecodeError:
            return "Error: Failed to parse JSON content after attempted repair."
class MultiQuestionGeneratorUI(ctk.CTk):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.generator = QuestionGenerator(api_key, None, None, None)
        
        self.title("Générateur de Questions")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Frame gauche pour les entrées
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.pack(side="left", fill="y", padx=20, pady=20)

        self.classe_label = ctk.CTkLabel(self.left_frame, text="Classe:")
        self.classe_label.pack(pady=10)
        self.classe_entry = ctk.CTkEntry(self.left_frame)
        self.classe_entry.insert(0,"6ème")
        self.classe_entry.pack(pady=10)

        self.date_label = ctk.CTkLabel(self.left_frame, text="Date:")
        self.date_label.pack(pady=10)
        self.date_entry = ctk.CTkEntry(self.left_frame)
        self.date_entry.insert(0,"07/06/2024")
        self.date_entry.pack(pady=10)

        self.conditions_label = ctk.CTkLabel(self.left_frame, text="Conditions:")
        self.conditions_label.pack(pady=10)
        self.conditions_text = ctk.CTkTextbox(self.left_frame, height=200)
        self.conditions_text.insert("0.0", "Un problème de proportionnalité, une question pour classer des fractions dans l'ordre croissant, une question sur les multiples et diviseurs")
        self.conditions_text.pack(pady=10)

        self.generate_button = ctk.CTkButton(self.left_frame, text="Générer Questions", command=self.start_generation)
        self.generate_button.pack(pady=10)

        # Frame droite pour les résultats
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.question_textbox = ctk.CTkTextbox(self.right_frame, height=200)
        self.question_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.answer_short_textbox = ctk.CTkTextbox(self.right_frame, height=100)
        self.answer_short_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.answer_details_textbox = ctk.CTkTextbox(self.right_frame, height=200)
        self.answer_details_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.generator.widget_question = self.question_textbox
        self.generator.widget_answer_short = self.answer_short_textbox
        self.generator.widget_answer_details = self.answer_details_textbox

    def start_generation(self):
        classe = self.classe_entry.get()
        date = self.date_entry.get()
        conditions = self.conditions_text.get("1.0", "end-1c").split("\n")

        self.question_textbox.delete("1.0", "end")
        self.answer_short_textbox.delete("1.0", "end")
        self.answer_details_textbox.delete("1.0", "end")

        thread = Thread(target=self.generator.generate_questions, args=(classe, date, conditions, self.update_result_text))
        thread.start()

    def update_result_text(self, text):
        self.question_textbox.insert("end", text)
        self.question_textbox.update_idletasks()
#import logging

#logging.basicConfig(level=logging.DEBUG)
class MonoQuestionGeneratorUI(ctk.CTkToplevel):
    def __init__(self, api_key,prompt_example=None,content=None,initial_widget=None,classe="6ème"):
        super().__init__()
        self.initial_widget=initial_widget
        self.api_key = api_key
        self.generator = QuestionGenerator(api_key, None, None, None,None)
        self.classe=classe
        if content:
            self.content=content
        else:
            self.content=""
        if prompt_example:
            self.prompt=prompt_example
        else:
            self.prompt="Un problème de proportionnalité, une question pour classer des fractions dans l'ordre croissant, une question sur les multiples et diviseurs"
        self.title("Générateur de Questions")
        self.geometry("1800x790")
        self.geometry("-10+0")  # Positionner en haut à gauche de l'écran
        self.fullscreen_state = False  # Initialiser l'état plein écran
        self.bind("<F11>", self.toggle_fullscreen)  # Lier la touche F11 pour le plein écran
        self.bind("<Escape>", self.end_fullscreen)  # Lier la touche Échap pour quitter le plein écran
        self.attributes("-topmost", True)  # Assurez-vous que la fenêtre est toujours au-dessus

        self.update_id = None
        self.check_dpi_id = None
        self.closed=False

        self.schedule_updates()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        

    def toggle_fullscreen(self, event=None):
        """Active ou désactive le mode plein écran."""
        self.fullscreen_state = not self.fullscreen_state
        self.attributes("-fullscreen", self.fullscreen_state)
        return "break"

    def end_fullscreen(self, event=None):
        """Désactive le mode plein écran."""
        self.fullscreen_state = False
        self.attributes("-fullscreen", False)
        return "break"
    def schedule_updates(self):
        if not self.closed:
            self.update_id = self.after(1000, self.update)
            self.check_dpi_id = self.after(2000, self.check_dpi_scaling)

    def update(self):
        if not self.closed:
            #logging.debug("Update function called")
            self.update_id = self.after(1000, self.update)

    def check_dpi_scaling(self):
        if not self.closed:
            #logging.debug("check_dpi_scaling function called")
            self.check_dpi_id = self.after(2000, self.check_dpi_scaling)

    def on_closing(self):
        #logging.debug("Application closing")
        if self.initial_widget:
            content=self.question_textbox.get("1.0", "end-1c")
            if content != "":
                self.initial_widget.delete("0.0","end")
                self.initial_widget.insert("0.0",content)
                self.initial_widget.highlight_syntax()
        self.closed = True
        if self.update_id is not None:
            self.after_cancel(self.update_id)
            self.update_id = None
        if self.check_dpi_id is not None:
            self.after_cancel(self.check_dpi_id)
            self.check_dpi_id = None
        self.destroy()
        #logging.debug("Application closed")


    def create_widgets(self):
        self.fancy_page_parameters=f"""
        \\chapitre[$\\mathbf{{6^{{\\text{{ème}}}}}}$]{{
        Environnement de Tests %Environnement de cours
        }}{{
        Boum %Collège
        }}{{
        Factory %Les Jacobins
        }}{{
        %Reste du contenu à afficher au début du document.
        }}{{
        Aide via l'assistant IA %Presentation
        }}
        """

        #frames declaration
        
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.pack(side="bottom", fill="both", expand=True, padx=20, pady=20)
        
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.pack(side="left", fill="y", padx=20, pady=20)


        # Frame droite pour les résultats
        
        self.pdf_viewer = PdfViewer(self.bottom_frame)
        self.pdf_viewer.pack(fill="both", expand=True, padx=10, pady=10)

        self.latex_compiler = LaTeXCompiler("temp_assistant_tools/temp_assistant.tex")

        self.question_textbox = LatexText(self.right_frame,compiler=self.latex_compiler, pdf_viewer=self.pdf_viewer,fancy_page_parameters=self.fancy_page_parameters, height=200,empty_document="temp_assistant_tools/empty_document.tex",header_filepath="temp_assistant_tools/entete.tex",final_document="temp_assistant_tools/temp_assistant.tex",output_directory="temp_assistant_tools",master_widget = self,topmost_option=True)
        self.question_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        if self.content:
            self.question_textbox.insert("0.0",self.content)
        self.generator.widget_question = self.question_textbox

        # Frame en bas pour le PDF viewer
        
        # Frame gauche pour les entrées
        
        
        self.conditions_label = ctk.CTkLabel(self.left_frame, text="Actions:")
        self.conditions_label.pack(pady=10)
        self.conditions_text = LatexText(self.bottom_frame, compiler=self.latex_compiler, pdf_viewer=self.pdf_viewer,fancy_page_parameters=self.fancy_page_parameters, width=80, height=20,empty_document="temp_assistant_tools/empty_document.tex",header_filepath="temp_assistant_tools/entete.tex",final_document="temp_assistant_tools/temp_assistant.tex",master_widget = self,topmost_option=True)

        #self.conditions_text = LatexText(self.left_frame, height=200,width=200)
        self.conditions_text.insert("0.0", self.prompt)
        self.conditions_text.pack(pady=10)

        self.generate_button = ctk.CTkButton(self.left_frame, text="Générer Questions", command=self.start_generation)
        self.generate_button.pack(pady=10)  
        self.generate_button = ctk.CTkButton(self.left_frame, text="Compiler", command=self.start_compiling)
        self.generate_button.pack(pady=10) 

        environnement="Environnement de cours"
        content_type="Presentation"
        etab="Collège"
        etab_name="Les Jacobins"
        supplement="%Reste du contenu à afficher au début du document."

        

    def start_compiling(self):
        self.question_textbox.auto_compile()

    def start_generation(self):

        conditions = self.conditions_text.get("1.0", "end-1c").split("\n")
        current_content = self.question_textbox.get("1.0", "end-1c").split("\n")
        if current_content != "":
            client_message= f"{conditions}\n{current_content}"
            print(f"On a envoyé : \n {client_message}")
        else:
            client_message= f"{conditions}"
        self.question_textbox.delete("1.0", "end")
        classe=self.classe
        date="01/01/24"

        thread = Thread(target=self.generator.generate_one_question, args=(client_message,self.question_textbox))
        thread.start()

    def update_result_text(self, text):
        self.question_textbox.insert("end", text)
        self.question_textbox.update_idletasks()

    

        

    

    

def use_case_test():
    # Exemple de réponse texte simulée
    response_text = r"""
    Voici une série de trois questions de mathématiques pour la classe de 6ème à la date du 07/06/2024, incluant un problème de proportionnalité, une question de classement de fractions, et une question sur les multiples et diviseurs :

    ```json
    {
        "QF_07_06_2024": {
            "classe": "6ème",
            "date": "07/06/2024",
            "questions": {
                "question1": {
                    "enonce": "Un sachet de $5$kg de pommes coûte $12{,}50$€. Combien coûte un kg de pommes ?",
                    "reponse": "$2{,}50$€",
                    "details": "\[
        \text{Prix par kg} = \dfrac{12{,}50\text{€}}{5 \text{kg}} = 2{,}50\text{€/kg}
    \]",
                    "theme": "Proportionnalité"
                },
                "question2": {
                    "enonce": "Classer les fractions suivantes dans l'ordre croissant : $\dfrac{2}{3}$, $\dfrac{1}{2}$, $\dfrac{3}{4}$.",
                    "reponse": "$\dfrac{1}{2} < \dfrac{2}{3} < \dfrac{3}{4}$",
                    "details": "\begin{align*}
        \dfrac{1}{2} &= 0{,}5 \\
        \dfrac{2}{3} &= 0{,}666\ldots \\
        \dfrac{3}{4} &= 0{,}75 \\
    \end{align*}
    \[
        \dfrac{1}{2} < \dfrac{2}{3} < \dfrac{3}{4}
    \]",
                    "theme": "Fractions"
                },
                "question3": {
                    "enonce": "Parmi les nombres $12$, $18$, $24$ et $30$, lesquels sont des multiples de $6$? Lesquels sont des diviseurs de $72$?",
                    "reponse": "Multiples de $6$: $12$, $18$, $24$, $30$\\
    Diviseurs de $72$: $12$, $18$, $24$",
                    "details": "\begin{align*}
        \text{Multiples de 6} : & \text{un nombre est multiple de 6 s'il est divisible par 6}\\
        12 &= 6 \times 2 \\
        18 &= 6 \times 3 \\
        24 &= 6 \times 4 \\
        30 &= 6 \times 5 \\
        \text{Diviseurs de 72} : & \text{un nombre est un diviseur de 72 si 72 est divisible par ce nombre}\\
        72 \div 12 &= 6 \\
        72 \div 18 &= 4 \\
        72 \div 24 &= 3 \\
        72 \div 30 &= 2{,}4 \quad(\text{n'est pas un entier})
    \end{align*}
    Les multiples de $6$ sont donc : $12$, $18$, $24$, $30$.\\
    Les diviseurs de $72$ sont : $12$, $18$, $24$.",
                    "theme": "Nombres et calculs"
                }
            }
        }
    }
    """
    cleaner = JSONCleaner()
    result = cleaner.extract_and_clean_json(response_text)
    #print(result)

def use_case_normal():
    api_key = read_api_key().strip().strip('"')
    app = MultiQuestionGeneratorUI(api_key)
    app.mainloop()

if __name__ == "__main__":
    #use_case_test()
    api_key = read_api_key().strip().strip('"')
    #api_key = api_key
    #generator = QuestionGenerator(api_key, None, None, None)
    use_case_normal()
