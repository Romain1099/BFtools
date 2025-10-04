

import random
import math
from typing import List
import string
try:
    from number_generator import NumberGenerator
except ImportError:
    from number_generators.number_generator import NumberGenerator

class FloatNumber(NumberGenerator):
    def __init__(self, 
            name="auto",
            inf: float=0, 
            sup: float=1, 
            decimalesG: int = 1, 
            decimalesD: int = 1000):
        """
        Génère un nombre aléatoire entre les bornes inf et sup, et possédant les décimales voulues pour la partie entière ou décimale.
        A implémenter...
        """
        pass