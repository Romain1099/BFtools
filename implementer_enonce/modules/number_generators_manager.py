from exo_number import ExoNumber,numberType
from number_generators.arithmetic_number_def import ArithmeticNumber
import inspect
import json
from enum import Enum,StrEnum
class NumberGeneratorType(Enum):
    EXONUMBER=ExoNumber
    #ARITHMETIC=ArithmeticNumber
import os
import importlib.util
from enum import Enum

'''class NumberGeneratorType(Enum):
    pass'''

class NumberGeneratorManager:
    def __init__(self,custom_generators=r"C:\Users\Utilisateur\Desktop\Faire\Macros\Programmes_de_facilitation\implementer_enonce\modules\number_generators"):
        #self._load_default_generators()
        #print(custom_generators)
        self.already_generated=[]
        self.incorporate_generators_from_directory(custom_generators)

    def _load_default_generators(self):
        """Charge les générateurs par défaut dans NumberGeneratorType."""
        from exo_number import ExoNumber
        from number_generators.arithmetic_number_def import ArithmeticNumber

        NumberGeneratorType.EXONUMBER = ExoNumber
        NumberGeneratorType.ARITHMETIC = ArithmeticNumber

    def incorporate_generators_from_directory(self, directory):
        """
        Parcourt un répertoire, charge les modules Python, et ajoute
        les classes valides en tant que nouveaux types de générateurs.
        TODO : définir cette méthode comme une méthode de classe pour la classe d'énumération NumberGeneratorType. 
        En effet il faut pouvoir redéfinir l'ENUM après avoir chargé les différents types de nombres dynamiquement. 
        
        """
        #print(directory)
        for filename in os.listdir(directory):
            #print(filename)
            if filename.endswith(".py") and filename != "__init__.py":
                module_path = os.path.join(directory, filename)
                module_name = filename[:-3]

                # Charger dynamiquement le module
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Parcourir les classes du module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Vérifier si la classe est dans le module en cours
                    if obj.__module__ == module_name:
                        # Ajouter la classe au type de générateur
                        setattr(NumberGeneratorType, name.upper(), obj)
        print(f"générateurs définis : {[n for n in NumberGeneratorType._member_map_]}")
    def generate_number(self,text):
        #print(f"texte de generate_number : {text}")
        count=0
        value_already_done=True
        while value_already_done and count<5:
            count+=1
            number=eval(text)
            if number.number in self.already_generated:
                value_already_done = True
            else:
                self.already_generated.append(number.number)
                value_already_done = False
        #print(number)
        return number
    def generate_placeholders_number(self,number_class:NumberGeneratorType|str=NumberGeneratorType.EXONUMBER,input:str|dict=""):
        if isinstance(number_class,str):
            number_class=self.match_gen_type_from_str(number_class)
        if isinstance(input,dict):
            param_text=',\n\t'.join([f"{key}={value}" if (key != "number_type" and key != "name") else f"{key}='{value}'" for key,value in input.items()])#.value.__name__
            to_return=f"""{number_class}(
\t{param_text}
)"""
            #print(to_return)
        elif isinstance(input,str):
            to_return=f"Generating {number_class.value.__name__} with input '{input}'"
            print(f"Generating {number_class.value.__name__} with input '{input}'")
        elif isinstance(input,list):
            param_text=',\n\t'.join([f"{value}" for value in input])
            to_return=f"""{number_class.value.__name__}(
\t{param_text}
)"""
            print(f"""{number_class.value.__name__}(
\t{param_text}
)""")
        else:
            print(f"Format non pris en charge : {input.__class__.__name__}")
        return to_return
    def match_gen_type_from_str(self,name:str)->NumberGeneratorType:
        match=[v for v in NumberGeneratorType if v.value.__name__.upper() == name.upper()]
        print([v.value.__name__ for v in NumberGeneratorType])
        try:
            return match[0]
        except Exception as e:
            raise ValueError(f"Pas de générateur trouvé. \n{e}\n---------------")

    def get_class_defaults(self,type:NumberGeneratorType|None=None):
            """Récupère les paramètres et leurs valeurs par défaut pour chaque classe."""
            defaults = {}
            if type is not None:
                if isinstance(type,str):
                    type=self.match_gen_type_from_str(type)
                cls = type.value
                # Récupère les arguments de __init__ et leurs valeurs par défaut
                signature = inspect.signature(cls.__init__)
                params = [
                    f"{k.split(':')[0]}='{v.split('=')[1].strip()}'"#k: v.default #ancien, ou pour générer un dictionnaire
                    if isinstance(v,str) else f"{k.split(':')[0]}={v.__str__().split('=')[1].strip()}"
                    for k, v in signature.parameters.items()
                    if k != 'self'  # Ignore `self`
                ]
                #print(f"Paramètres : {params}")
                defaults[cls.__name__] = params
            else:
                for gen_type in NumberGeneratorType:
                    cls = gen_type.value
                    # Récupère les arguments de __init__ et leurs valeurs par défaut
                    signature = inspect.signature(cls.__init__)
                    params = {
                        k: v.default
                        for k, v in signature.parameters.items()
                        if k != 'self'  # Ignore `self`
                    }
                    print(f"Paramètres pour {gen_type} : {params}")
                    defaults[cls.__name__] = params
            return defaults
    


def use_case_one():
    manager= NumberGeneratorManager()
    manager.generate_placeholders_number(number_class=NumberGeneratorType.ARITHMETICNUMBER,input={
        "min":41,
        "max":77
    })
    manager.generate_placeholders_number(number_class=NumberGeneratorType.EXONUMBER,input='''"min":41,"max":77''')

    # Affiche les paramètres et leurs valeurs par défaut
    defaults = manager.get_class_defaults()#type=NumberGeneratorType.ARITHMETIC)
    #print(defaults)
    print("\nDefault Parameters:")
    for class_name, params in defaults.items():
        print(f"{class_name}: {params}")

    generators=[manager.generate_placeholders_number(number_class=class_name,input=defaults[class_name.value.__name__]) for class_name in NumberGeneratorType]
    print(generators)
    generated = manager.generate_number(generators[1])
    print(generated.number)#.__str__())
    print(generated.__str__())
    print(generated.to_latex())
if __name__=="__main__":
    use_case_one()