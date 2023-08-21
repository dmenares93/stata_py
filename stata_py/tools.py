# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:05:12 2023

@author: UCHILE
"""
import numpy as np
import re

def dic_stats(stats: str, 
              oper: list) -> dict:
    
    """
    Function that translates stats from the tabulate to a dictionary for evaluation in agg.
    ----------
        stats: str, stats instructions from the table command.
        oper: list, list with identification of the operations handled in
            stats from the table command.
    Returns
    -------
    dict
        Dictionary with the transcription of table stats for evaluation in agg.
    """
    
    oper = [re.sub("p1/p100", 'p[1-9]|p[1-9][0-9]|p100', item) for item in oper]
    # Create a regular expression that matches any of the operators and splits the text into segments
    pattern = r'\b(?:' + '|'.join(oper) + r')\b'
    segments = re.split(pattern, stats)
    # Create a list of operators in the order they appear in the text
    operators = re.findall(pattern, stats)
    # Create the result dictionary
    result_dict = {}
    for op, col in zip(operators, segments[1:]):
        # Remove extra spaces and split the columns into a list
        col = col.strip().split()
        # Assign the columns to the operator in the result dictionary
        result_dict[op] = col
    
    # Create the inverse dictionary
    inv_dict = {}
    for op, cols in result_dict.items():
        for c in cols:
            if c in inv_dict:
                inv_dict[c].append(op)
            else:
                inv_dict[c] = [op]
                
    # Itera sobre las claves y valores del diccionario para crear funcion de percentil
    for key, values in inv_dict.items():
        new_values = []
        for value in values:
            # Si el valor empieza con 'p', extrae el número y crea una función lambda para el percentil
            if value.startswith('p'):
                percentile_value = int(value[1:])
                new_values.append(lambda x: np.percentile(x, q=percentile_value))
            else:
                new_values.append(value)
        # Actualiza los valores en el diccionario
        inv_dict[key] = new_values
        
    return inv_dict
