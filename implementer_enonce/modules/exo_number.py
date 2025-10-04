
import random
import re
import string
class numberType:
    INT = "INT"
    FLOAT = "FLOAT"
    FRAC = "FRAC"

current_letter_index=1

class ExoNumber:
    def __init__(self, number_type: str = numberType.INT, value_min: float | int = 0, value_max: float | int = 20,nombre_decimalesD:int=0,nombre_decimalesG:int=2,name="auto", exclude=None):
        global current_letter_index
        if name=="auto":
            self.name = f"\\exonum"#{string.ascii_lowercase[current_letter_index]}
            current_letter_index += 1
        else:
            self.name=name
        self.number_type = number_type
        self.nombre_decimalesD=nombre_decimalesD
        self.nombre_decimalesG=nombre_decimalesG
        #print(f"décimales : {self.nombre_decimales}")
        self.value_min = value_min
        self.value_max = value_max
        if isinstance(self.value_min,str):
            try:
                self.value_min = int(self.value_min)
            except:
                self.value_min = float(self.value_min)
        if isinstance(self.value_max,str):
            try:
                self.value_max = int(self.value_max)
            except:
                self.value_max = float(self.value_max)
        self.exclude = exclude if exclude is not None else []
        self.number = self.determine_random_value()

    def determine_random_value(self):
        count = 0
        while True and count < 5:
            count+=1
            if self.number_type == numberType.INT:
                value = random.randint(self.value_min, self.value_max)
                if self.nombre_decimalesG > 0:
                    int_digits_number = len(str(int(abs(value))))  # Nombre de chiffres dans la partie entière
                    #print(int_digits_number)
                    incount = 0
                    while int_digits_number < self.nombre_decimalesG and incount <= self.nombre_decimalesG:
                        if int_digits_number < self.nombre_decimalesG and incount < 5:
                            value *= 10  # Multiplier pour ajouter des zéros
                            int_digits_number = len(str(int(abs(value))))
                        incount += 1
                    incount=0
                    while int_digits_number > self.nombre_decimalesG and incount <= self.nombre_decimalesG:
                        if int_digits_number > self.nombre_decimalesG and incount < 5:
                            value = int(value / 10)  # Diviser pour retirer des zéros
                            int_digits_number = len(str(int(abs(value))))
                        incount += 1

            elif self.number_type == numberType.FLOAT:
                value = random.uniform(self.value_min, self.value_max)
                if self.nombre_decimalesG > 0:
                    int_digits_number = len(str(int(abs(value))))  # Nombre de chiffres dans la partie entière
                    #print(int_digits_number)
                    incount = 0
                    while int_digits_number < self.nombre_decimalesG and incount <= self.nombre_decimalesG:
                        if int_digits_number < self.nombre_decimalesG and incount < 5:
                            value *= 10  # Multiplier pour ajouter des zéros
                            int_digits_number = len(str(int(abs(value))))
                        incount += 1
                    incount=0
                    while int_digits_number > self.nombre_decimalesG and incount <= self.nombre_decimalesG:
                        if int_digits_number > self.nombre_decimalesG and incount < 5:
                            value = int(value / 10)  # Diviser pour retirer des zéros
                            int_digits_number = len(str(int(abs(value))))
                        incount += 1

                # Gestion de la partie décimale (décimales à droite)
                if self.nombre_decimalesD > 0:
                    value = round(value, self.nombre_decimalesD)
                    # Formater pour garantir exactement `nombre_decimalesD` après la virgule
                    format_str = f"{{:.{self.nombre_decimalesD}f}}"
                    value = float(format_str.format(value))
                    
            elif self.number_type == numberType.FRAC:
                value = [random.randint(self.value_min, self.value_max), random.randint(self.value_min, self.value_max)]
                # Vérifier que le dénominateur n'est pas dans `exclude` ou nul
                if value[1] in self.exclude:
                    value[1] = random.randint(self.value_min, self.value_max)
                if value[1] == 0:
                    value[1] += 4 if 4 not in self.exclude else 5
            else:
                return "Format non pris en charge"

            # Vérifier les exclusions
            if isinstance(value, list):
                if value in self.exclude:
                    continue
            elif value in self.exclude:
                continue
            if count > 3:
                print(f"Plusieurs itérations ont été nécessaires pour {value} : {count} itérations")
            return value

    def __str__(self):
        #print(self.number_type, self.number)
        if self.number_type == numberType.INT:
            #print(f"int trigg : {self.number}")
            return str(self.number)
        elif self.number_type == numberType.FLOAT:
            return str(self.number)#f"{self.number}"
        elif self.number_type == numberType.FRAC:
            return f"\\dfrac{{{self.number[0]}}}{{{self.number[1]}}}"
        else:
            return "Format non pris en charge"
    def to_latex(self):
        return f"\\def\\{self.name}{{{self.__str__()}}}"