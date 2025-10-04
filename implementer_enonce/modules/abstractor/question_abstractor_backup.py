import re
import string
from typing import Callable, List,Tuple
import openai
from abstractor.cfg import read_api_key
from threading import Thread
import re
import json
import time
import customtkinter as ctk
import asyncio
import tracemalloc
tracemalloc.start()
class ExoAbstractor:
    def __init__(self,texte:str=""):
        self.original_text=texte
        self.modified_text=texte
        self.modified_list=[]
        self.api_key = read_api_key().strip().strip('"')
        openai.api_key = self.api_key
        self.abstract_prompt=self.abstract_prompt()

    def abstract_prompt(self):
        return r"""
<?xml version="1.0" encoding="UTF-8"?>
<latex_abstraction_agent_prompt>
    <system_role>
        Tu es un assistant expert en retranscription et abstraction LaTeX pour les cours de mathématiques.
        Tu maîtrises parfaitement la création d'exercices paramétrables et réutilisables.
    </system_role>

    <primary_task>
        <description>
            Retranscrire le code LaTeX fourni en identifiant et abstrayant les variables didactiques 
            (nombres utiles à la résolution de l'énoncé) pour créer des exercices paramétrables.
        </description>
        <key_concept>
            Les variables didactiques sont les valeurs numériques qui participent à la résolution.
            Les paramètres de mise en forme (ex: 3.4cm pour un espace réponse) ne sont PAS abstraits.
        </key_concept>
    </primary_task>

    <abstraction_example>
        <input>$2 + (-3) = \repsim[3.4cm]{-1}$</input>
        <variables_identification>
            <variable>2</variable>
            <variable>-3</variable>
            <non_variable>3.4cm (paramètre de mise en forme)</non_variable>
        </variables_identification>
        <output>
            <![CDATA[
\def\numa{2} \def\numb{-3} %% 
\acc{Calculer} $\affiche{\numa} + \affiche{\numb}$ %%
$\affiche{\numa} + \affiche{\numb} = \affiche{\fpeval{\numa + \numb}}$ %%
\begin{enumerate}
    \item $\affiche{\fpeval{\numa + \numb +1}}$
    \item $\affiche{\fpeval{\numa + \numb -10}}$
    \item $\affiche{\fpeval{\numa + \numb-1}}$
    \item $\affiche{\fpeval{\numa + \numb}}$
\end{enumerate} %%
$\affiche{\fpeval{\numa + \numb}}$ %%
Relatifs
            ]]>
        </output>
    </abstraction_example>

    <technical_requirements>
        <packages>
            <package>xfp (pour les calculs avec fpeval)</package>
            <package>profCollege (pour les solutions)</package>
        </packages>
        <display_command>
            <syntax>\affiche[options]{nombre}</syntax>
            <purpose>Gère l'affichage des nombres (parenthèses pour négatifs, virgules décimales)</purpose>
        </display_command>
    </technical_requirements>

    <abstraction_rules>
        <rule id="variables_definition">
            <title>Définition des variables</title>
            <description>
                Privilégier plusieurs variables simples (entiers ou flottants) 
                plutôt que des expressions complexes
            </description>
            <example>
                <case>Fraction 5/7</case>
                <abstraction>
                    \def\numa{5}
                    \def\numb{7}
                    \def\fraction{\dfrac{\numa}{\numb}}
                </abstraction>
            </example>
            <special_case>
                <description>Variables avec valeurs dans une liste</description>
                <syntax>\def\nomvariable{[val1, val2, ...]}</syntax>
            </special_case>
        </rule>

        <rule id="operations">
            <title>Règle pour les opérations</title>
            <description>
                Les opérations numériques doivent être dans \fpeval{} 
                pour afficher le résultat du calcul
            </description>
            <warning>Sans fpeval, génération d'erreurs LaTeX</warning>
        </rule>

        <rule id="mathematical_accuracy">
            <title>Règle de professionnalisme</title>
            <description>
                Les mathématiques doivent être parfaitement justes.
                Point essentiel car les erreurs nécessitent des corrections coûteuses.
            </description>
        </rule>

        <rule id="conciseness">
            <title>Règle de concision</title>
            <description>
                Contenu destiné aux enfants : compréhensible et court,
                allant directement à l'essentiel.
            </description>
        </rule>

        <rule id="response_format">
            <title>Règle de format de réponse</title>
            <description>
                Produire uniquement le code LaTeX demandé, 
                sans texte additionnel (insertion directe dans document).
            </description>
        </rule>
    </abstraction_rules>

    <output_structure>
        <separator>%%</separator>
        <sections_order>
            <section order="1">Définitions des variables</section>
            <section order="2">Énoncé avec calcul originel</section>
            <section order="3">Solution détaillée de l'énoncé</section>
            <section order="4">Version QCM</section>
            <section order="5">Solution courte pour affichage restreint</section>
            <section order="6">Thème en un mot</section>
            <section order="7">JSON de structure</section>
        </sections_order>
        <note>
            Le séparateur %% est utilisé pour permettre au programme 
            de splitter la réponse en sections distinctes
        </note>
    </output_structure>

    <json_structure>
        <description>
            Structure JSON finale décrivant l'exercice avec solutions minimales
            pour faciliter la correction future
        </description>
        <schema>
            <![CDATA[
{
    "instructions": "Consigne rappelée",
    "latex": [
        "consigne avec l'espace réponse \\tcfillcrep{}",
        "Une autre ligne si nécessaire avec espace réponse \\tcfillcrep{}"
    ],
    "points": 1,
    "correction": [
        "\\(solution de l'espace 1\\)",
        "\\(solution de l'espace 2\\)"
    ]
}
            ]]>
        </schema>
        <example>
            <![CDATA[
{
    "instructions": "Trouver la puissance de 10 correspondant aux préfixes suivants.",
    "latex": [
        "kilo \\tcfillcrep{}",
        "téra \\tcfillcrep{}"
    ],
    "points": 1,
    "correction": [
        "\\(10^3\\)",
        "\\(10^{12}\\)"
    ]
}
            ]]>
        </example>
    </json_structure>

    <solutions_handling>
        <case type="absent">
            <action>Écrire le code LaTeX de résolution complète</action>
        </case>
        <case type="present">
            <action>
                Veiller à bien séparer les différentes parties 
                pour analyse correcte par le programme
            </action>
        </case>
    </solutions_handling>

    <critical_reminders>
        <reminder>Toujours utiliser \affiche{} pour l'affichage des nombres</reminder>
        <reminder>Utiliser \fpeval{} pour tous les calculs</reminder>
        <reminder>Respecter strictement l'ordre des sections avec %%</reminder>
        <reminder>Vérifier la justesse mathématique de toutes les expressions</reminder>
        <reminder>Produire un JSON valide et minimal en dernière section</reminder>
    </critical_reminders>
</latex_abstraction_agent_prompt>
"""
    
    async def generate_questions(self,text:str)->str:
        #preprompt, prompt = self.create_prompt(classe, date, conditions)
        attempts = 0
        max_attempts = 1
        code="Pas d'aperçu disponible"
        while attempts < max_attempts:
            try:
                # Generate question code
                code = await self.abstract_AI(text)
                #time.sleep(2)
            except openai.error.OpenAIError as e:
                print(f"Error: {e}. Attempt {attempts}/{max_attempts}")
                time.sleep(2)
            finally:
                attempts += 1
        if attempts > max_attempts:
            print("Failed to generate questions after several attempts. Please try again later.")

        #print(code)
        return code

    async def abstract_AI(self,text,stream_wanted=True):
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": f"{self.abstract_prompt}"},
                {"role": "user", "content": f"{text}"}
            ],
            stream=stream_wanted,
        )
        #print( response)
        tex_code = []
        if stream_wanted:
            for chunk in response:
                if chunk.choices[0].delta.get("content"):
                    tex_code.append(chunk.choices[0].delta.content)
        #print(''.join(tex_code))
        return ''.join(tex_code)

    def abstract_pipe(self, functions_to_apply: List[Tuple[Callable[[str], str], str]], single_text=""):
        self.modified_list = []
        xdef_map = {}  # Dictionnaire pour stocker les lignes xdef par bloc
        #print("abstract_pipe : début des opérations")

        def extract_xdef_lines(text):
            lines = text.split('\n')
            local_xdef_lines = []
            remaining_lines = []
            for line in lines:
                if line.startswith("\\xdef"):
                    local_xdef_lines.append(line)
                else:
                    remaining_lines.append(line)
            return '\n'.join(remaining_lines), local_xdef_lines

        # Extract xdef lines from the initial single_text
        single_text, initial_xdef_lines = extract_xdef_lines(single_text)
        xdef_map[0] = initial_xdef_lines

        for i, function_to_apply in enumerate(functions_to_apply):
            function_name, params = function_to_apply
            if not params:
                params = single_text
            else:
                params, local_xdef_lines = extract_xdef_lines(params)
                xdef_map[i + 1] = local_xdef_lines

            if hasattr(self, function_name.__name__):
                result = function_name(params)
                result, local_xdef_lines = extract_xdef_lines(result)
                if i + 1 not in xdef_map:
                    xdef_map[i + 1] = []
                xdef_map[i + 1].extend(local_xdef_lines)
                self.modified_list.append(result)
                #print(f"La méthode {function_name.__name__} de {self.__class__.__name__} a été appliquée.")
            else:
                #print(f"La méthode {function_name.__name__} de {self.__class__.__name__} n'est pas connue : étape annulée.")
                continue

        # Combine all the texts from modified_list with their corresponding xdef lines
        final_text_list = []
        for i, text in enumerate(self.modified_list):
            xdef_lines = xdef_map.get(i + 1, [])
            final_text_list.append('\n'.join(xdef_lines) + '\n' + text)

        #final_text = '\n'.join(final_text_list)

        #print("Fin des opérations d'abstractions demandées.")
        return final_text_list#[final_text.strip()]
 
    def abstract_numbers(self,texte=None):
        if not texte and not self.original_text:
            print("abstract_numbers : Le texte est vide ou manquant : annulation des opérations")
            return
        elif not texte and self.original_text:
            texte=self.original_text

        # Prétraitement pour remplacer les virgules décimales groupées par un format temporaire
        texte = re.sub(r'(\d+),(\d+)', r'\1{,}\2', texte)
        
        # Trouver tous les nombres préformatés et les convertir comme précédemment
        nombres = re.findall(r'\d+(?:\\,\d{3})*(?:\{,\}\d+)?', texte)

        # Dictionnaire pour stocker les paramètres et leurs valeurs
        parametres = {}
        
        # Utiliser les lettres de l'alphabet pour les paramètres
        alphabet = string.ascii_lowercase
        
        # Remplacer les nombres par des paramètres
        for i, nombre in enumerate(nombres):
            parametre = f"number{alphabet[i]}"
            parametres[parametre] = nombre#.replace(',', '{,}')  # Remplacer la virgule par un point pour standardiser
            texte = texte.replace(nombre, f"\\{parametre}", 1)
        
        # Générer les définitions des paramètres
        definitions = "\n".join([f"\\xdef\\{param}{{{val}}}" for param, val in parametres.items()])
        #print(f"{definitions}\n{texte}")
        return f"{definitions}\n{texte}"

class ExoAbstractorTest:
    def __init__(self):
        self.abstractor = ExoAbstractor()
        self.test_results=[]
        self.make_input_output_base()
        self.execute_abstract_numbers_tests()
        self.execute_abstract_pipe_tests()
        print("""
              
        -----------------------
        | Résultats des tests |
        -----------------------
              """)
        print('\n'.join(self.test_results))
        print("\n\n")

    def make_input_output_base(self):
        self.input_a = r"\textbf{Calculer} la longueur de la \textbf{diagonale} d'un \textbf{rectangle} de $80\,\text{m}$ sur $60,5\,\text{m}$. bignumbers : $374\,741$ ou $599\,233,3$ ou encore $87\,599\,233,3$"
        self.output_a=r"""\xdef\numbera{80}
\xdef\numberb{60{,}5}
\xdef\numberc{374\,741}
\xdef\numberd{599\,233{,}3}
\xdef\numbere{87\,599\,233{,}3}
\textbf{Calculer} la longueur de la \textbf{diagonale} d'un \textbf{rectangle} de $\numbera\,\text{m}$ sur $\numberb\,\text{m}$. bignumbers : $\numberc$ ou $\numberd$ ou encore $\numbere$"""
        self.input_b = r"Un agriculteur récolte $120$ kg de pommes sur un terrain de $\dfrac{1}{2}$ ha. \textbf{Calcule} la quantité de pommes qu'il récolterait sur un terrain de $1{,}2$ ha en supposant que la récolte est \textbf{proportionnelle} à la surface."#\textbf{Calculer} la longueur de la \textbf{diagonale} d'un \textbf{rectangle} de $80\,\text{m}$ sur $60\,\text{m}$."
        self.output_b=r"""\xdef\numbera{120}
\xdef\numberb{1}
\xdef\numberc{2}
\xdef\numberd{1{,}2}
Un agriculteur récolte $\numbera$ kg de pommes sur un terrain de $\dfrac{\numberb}{\numberc}$ ha. \textbf{Calcule} la quantité de pommes qu'il récolterait sur un terrain de $\numberd$ ha en supposant que la récolte est \textbf{proportionnelle} à la surface."""

    def execute_abstract_pipe_tests(self):
        todolist = [
            (self.abstractor.abstract_numbers, self.input_a),
            (self.abstractor.abstract_numbers, self.input_b)
        ]
        result_a = self.abstractor.abstract_pipe(todolist)

        todolist_b=[
            (self.abstractor.abstract_numbers, ""),
            (self.abstractor.abstract_numbers, "")
        ]
        result_b = self.abstractor.abstract_pipe(todolist_b,single_text = self.input_a)
        texta = '\n'.join(result_a)
        textb = '\n'.join(result_b)
        print(f"----------------\nPIPE RESULTS :\n----------------\n \n{texta.strip()}\n\n\n{textb.strip()}")
        if texta.strip()==r"""\xdef\numbera{80}
\xdef\numberb{60{,}5}
\xdef\numberc{374\,741}
\xdef\numberd{599\,233{,}3}
\xdef\numbere{87\,599\,233{,}3}
\textbf{Calculer} la longueur de la \textbf{diagonale} d'un \textbf{rectangle} de $\numbera\,\text{m}$ sur $\numberb\,\text{m}$. bignumbers : $\numberc$ ou $\numberd$ ou encore $\numbere$
\xdef\numbera{120}
\xdef\numberb{1}
\xdef\numberc{2}
\xdef\numberd{1{,}2}
Un agriculteur récolte $\numbera$ kg de pommes sur un terrain de $\dfrac{\numberb}{\numberc}$ ha. \textbf{Calcule} la quantité de pommes qu'il récolterait sur un terrain de $\numberd$ ha en supposant que la récolte est \textbf{proportionnelle} à la surface.""":

            self.test_results.append(f"\ttest_a : réussi !")
        else:
            self.test_results.append(f"\ttest_a : échoué.")
        
        if textb.strip()==r"""\xdef\numbera{80}
\xdef\numberb{60{,}5}
\xdef\numberc{374\,741}
\xdef\numberd{599\,233{,}3}
\xdef\numbere{87\,599\,233{,}3}
\textbf{Calculer} la longueur de la \textbf{diagonale} d'un \textbf{rectangle} de $\numbera\,\text{m}$ sur $\numberb\,\text{m}$. bignumbers : $\numberc$ ou $\numberd$ ou encore $\numbere$
\xdef\numbera{80}
\xdef\numberb{60{,}5}
\xdef\numberc{374\,741}
\xdef\numberd{599\,233{,}3}
\xdef\numbere{87\,599\,233{,}3}
\textbf{Calculer} la longueur de la \textbf{diagonale} d'un \textbf{rectangle} de $\numbera\,\text{m}$ sur $\numberb\,\text{m}$. bignumbers : $\numberc$ ou $\numberd$ ou encore $\numbere$""":
            self.test_results.append(f"\ttest_b : réussi !")
        else:
            self.test_results.append(f"\ttest_b : échoué.")

    def execute_abstract_numbers_tests(self):
        returns=[]
        #test de la commande d'abstraction des nombres
        if self.abstractor.abstract_numbers(texte=self.input_a)==self.output_a:
            returns.append([True,"abstract_numbers a"])
        else:
            #print(self.abstractor.abstract_numbers(texte=self.input_a))
            #print(f"\n{self.output_a}")
            returns.append([False,"abstract_numbers a"])
        
        #test 2 pour la commande d'abstraction des nombres 
        if self.abstractor.abstract_numbers(texte=self.input_b)==self.output_b:
            returns.append([True,"abstract_numbers b"])
        else:
            #print(self.abstractor.abstract_numbers(texte=self.input_b))
            #print(f"\n{self.output_b}")
            returns.append([False,"abstract_numbers b"])
        has_passed = True
        for index, duplet in enumerate(returns):

            result = duplet[0]
            function_name = duplet[1]
            if result==True:
                self.test_results.append(f"\ttest réussi pour {function_name}")
            else:
                self.test_results.append(f"\ttest échoué pour {function_name}")
                has_passed = False
        self.test_results.append(f"\thas_passed_abstract_number_test : {str(has_passed)}")
        return has_passed
    
"""
# Exemple d'utilisation
texte_input_a = r"\textbf{Calculer} la longueur de la \textbf{diagonale} d'un \textbf{rectangle} de $80\\,\text{m}$ sur $60,5\\,\text{m}$."

definitions, texte_output = abstraire_exercice(texte_input_a)
print(definitions)
print(texte_output)

# Exemple d'utilisation
texte_input_b = r"Un agriculteur récolte $120$ kg de pommes sur un terrain de 0{,}5 hectare. \textbf{Calcule} la quantité de pommes qu'il récolterait sur un terrain de 1{,}2 hectare en supposant que la récolte est \textbf{proportionnelle} à la surface."#\textbf{Calculer} la longueur de la \textbf{diagonale} d'un \textbf{rectangle} de $80\\,\text{m}$ sur $60\\,\text{m}$."

definitions, texte_output = abstraire_exercice(texte_input_b)
print(definitions)
print(texte_output)
"""

def tests():
    abstractor=ExoAbstractor()
    test_unit=ExoAbstractorTest()

def use_case_one():
    abstractor=ExoAbstractor()
    #utilisation de commandes d'abstraction associé à différents inputs
    input_a="texte n°1 à utiliser"
    input_b="texte n°2 à utiliser"
    todolist = [
            (abstractor.abstract_numbers, input_a),
            (abstractor.abstract_numbers, input_b)
        ]
    result_a = abstractor.abstract_pipe(todolist)

    print('\n'.join(result_a))

def use_case_two():
    abstractor=ExoAbstractor()
    #utilisation de commandes d'abstraction associé à différents inputs
    input_a="Le seul et unique texte n°1 à utiliser de plusieurs façons différentes."
    todolist_b=[
            (abstractor.abstract_numbers, ""),
            (abstractor.abstract_numbers, "")
        ]
    result_b = abstractor.abstract_pipe(todolist_b,single_text = input_a)

    print('\n'.join(result_b))
def abstract_question(input:str)->str:
        abstractor=ExoAbstractor()
        todolist=[
            (abstractor.abstract_numbers, ""),
        ]
        result = abstractor.abstract_pipe(todolist,single_text = input)
        print('\n'.join(result))
async def abstract_AI(input:str)->str:
    abstractor=ExoAbstractor()
    single_text=input
    #thread = Thread(target=abstractor.generate_questions, kwargs={'text':{single_text}}) #abstract_AI
    #thread.start()
    #result = abstractor.abstract_pipe(todolist,single_text = input)
    thread = await abstractor.generate_questions(text=input)
    print(thread)#'\n'.join(thread))
    return thread

def commands_list():
    abstractor = ExoAbstractor()
    methods = [func for func in dir(abstractor) if callable(getattr(abstractor, func)) and not func.startswith("__")]
    print("Méthodes implémentées dans la classe ExoAbstractor:")
    for method in methods:
        print(method)

if __name__=="__main__":
    #tests()
    #use_case_one()
    #use_case_two()
    asyncio.run(abstract_AI(
        r"""
	\item $A=5x\times(-2x)$
"""
    ))
    #commands_list()