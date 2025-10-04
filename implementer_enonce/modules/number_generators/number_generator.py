from abc import abstractmethod,ABC
import string

current_letter_index=0
max_index = 1000


def generate_alphabet_sequence(index):
    """Génère une séquence alphabétique en base 26 pour un index donné."""
    alphabet = string.ascii_lowercase
    base = len(alphabet)
    result = []
    
    # Conversion de l'index en base 26 alphabétique
    while index >= 0:
        result.append(alphabet[index % base])
        index = index // base - 1  # Passage à la "colonne" supérieure
    
    return ''.join(reversed(result))


class NumberGenerator(ABC):
    def __init__(self,number,name="auto"):
        super().__init__()
        global current_letter_index
        self.number=number
        #self.name=name
        if name=="auto":
            #self.name = f"\\arithnum{string.ascii_lowercase(current_letter_index)}"
            sequence = generate_alphabet_sequence(current_letter_index)
            self.name = f"\\arithnum{sequence}"
            current_letter_index += 1
        else:
            self.name=f"\\{name}"

    def _generate_number(self):
        pass

    def __str__(self):
        return (f"Nombre généré : {self.number}\n")
    
    def to_latex(self):
        return f"\\def{self.name}{{{self.number}}}"