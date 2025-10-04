

import random
import math
from typing import List
import string
try:
    from number_generator import NumberGenerator
except ImportError:
    from number_generators.number_generator import NumberGenerator

class ArithmeticNumber(NumberGenerator):
    """
    Classe destinée à contenir un nombre créé de façon aléatoire possédant les caractéristiques suivantes : 
    - Nombre entier
    - Possédant un nombre contraint de diviseurs premiers
    - Indicateur de difficulté basé sur la longueur et la taille des diviseurs premiers
    """
    def __init__(self, 
                name="auto",
                allowed_generators: List[int] = [2, 3, 5, 7, 11, 13, 17, 19], 
                prime_length: List[int] = [2,4], 
                inf: int = 1, 
                sup: int = 1000):
        """
        Construit un nombre par produit de 'prime_length' nombres premiers de la liste 'allowed_generators'. 
        Le nombre produit est situé entre les bornes inf et sup.
        """
        #global current_letter_index
        self.allowed_generators = allowed_generators
        self.prime_length = prime_length
        self.inf = inf
        self.sup = sup
        self.max_difficulty=self._load_max_difficulty()
        '''if name=="auto":
            #self.name = f"\\arithnum{string.ascii_lowercase(current_letter_index)}"
            sequence = generate_alphabet_sequence(current_letter_index)
            self.name = f"\\arithnum{sequence}"
            current_letter_index += 1
        else:
            self.name=f"\\{name}"'''
        if not self.allowed_generators:
            raise ValueError("La liste des générateurs autorisés est vide après exclusion.")
        
        self.number, self.prime_factors = self._generate_number()
        super().__init__(self.number,name=name)
        self.difficulty = self._compute_difficulty()
    def _load_max_difficulty(self)->int:
        try:
            return self.prime_length[1]
        except:
            return self.prime_length
    def _parse_prime_length(self) -> int:
        """Interpréte la contrainte de longueur des diviseurs premiers."""
        if isinstance(self.prime_length,list):
            return random.randint(self.prime_length[0],self.prime_length[1])
        else:
            return self.prime_length
    
    def _generate_number(self) -> int| List[int]:
        """Génère un nombre en respectant les contraintes."""
        prime_count = self._parse_prime_length()
        self.count=0
        while True and self.count <100:
            prime_factors = random.choices(self.allowed_generators, k=prime_count)
            number = math.prod(prime_factors)
            self.count+=1
            if self.inf <= number <= self.sup:
                #print(f"{count} passes pour générer le nombre {number}")
                return number, prime_factors
        prime_factors = random.choices(self.allowed_generators, k=prime_count)
        number = math.prod(prime_factors)
        #print(f"{count} passes pour générer le nombre {number}")
        return number, prime_factors
    
    def _compute_difficulty(self) -> float:
        """Calcule un indicateur de difficulté basé sur les facteurs premiers."""
        
        difficulty = len(self.prime_factors) / self.max_difficulty# * sum(unique_factors)
        return round(difficulty, 2)
    
    def __str__(self):
        return (f"Nombre généré : {self.number}\n"
                f"Facteurs premiers : {sorted(self.prime_factors)}\n"
                f"Indicateur de difficulté : {self.difficulty}\n"
                f"Nombre de passes nécessaires pour générer : {self.count}")
    def to_latex(self):
        return f"\\def{self.name}{{{self.number}}}"

if __name__ == "__main__":
    number = ArithmeticNumber(
        allowed_generators=[2, 3, 5, 7, 11],
        prime_length=[2,5],
        inf=30,
        sup=50
    )
    print(number.number)
    print(number)
    print(number.to_latex())

