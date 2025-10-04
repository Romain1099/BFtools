import numpy as np
import random

def addition(a=0,b=0,random_conditions=[],completion_mode="random"):
    if completion_mode == "random":
        a = random_conditions[0]# random.randint(0,20)
        b = random_conditions[1]#random.randint(0,20)
        return f'a + b = {a + b}' 
    elif completion_mode == "manual":
        return f'a + b = {a + b}' 
print(addition(random_conditions=["random.randint(0,20)","random.randint(0,20)"]))