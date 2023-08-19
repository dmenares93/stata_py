# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:06:11 2023

@author: UCHILE
"""
import pandas as pd
import re

def condition(df: pd.DataFrame, 
              stata_condition: str) -> pd.Series:
    """
    Función que evalua condiciones logicas individuales sobre un dataframe,
    considera como validas condiciones <,=<,>,>=,==,inlist(),inrange()
    Parameters
    ----------
    df : pd.DataFrame
        dataframe a evular condiciones.
    stata_condition : str
        condicion logica con la sintaxis de Stata, puede procesar las condiciones:
            <,=<,>,>=,==,inlist(),inrange().
        ejemplos stata_condition = "year == 1978", "year >= 1978", 
        "inlist(country,"Chile","Argentina)"
    Returns
    -------
    pd.Series
        Serie booleana de condicion evaluada

    """
    # Create a copy of the original DataFrame
    df = df.copy()

    # Case for inrange
    inrange_match = re.search(r"\s*inrange\(\s*(\w+)\s*,\s*([\d\w]+)\s*,\s*([\d\w]+)\s*\)\s*", stata_condition)
    if inrange_match:
        column, lower, upper = inrange_match.groups()
        return (df[column] >= float(lower)) & (df[column] <= float(upper))

    # Case for inlist
    inlist_match = re.match(r"\s*inlist\(\s*(\w+)\s*,\s*(.*?)\s*\)", stata_condition)
    if inlist_match:
        column, values = inlist_match.groups()
        # Separate the values using the comma, then strip whitespace and single quotes if any
        values = [value.strip().strip("'") for value in values.split(',')]
        # Try to convert each value to an integer; if not possible, leave it as is (as a string)
        values = [float(value) if value.isdigit() else value for value in values]
        return df[column].isin(values)

    # Case for simple comparisons
    match = re.match(r"\s*(\w+)\s*([<>==!]+)\s*(.+)\s*", stata_condition)
    if not match:
        raise ValueError("Invalid condition syntax")

    column, operator, value = match.groups()
    if value.isdigit():
        value = float(value)  # Convert value to an integer if it's a digit
    else:
        value = value.strip("'") # Remove quotes if it's a string

    # Apply the corresponding filter based on the operator
    if operator == '==':
        return df[column] == value
    elif operator == '>=':
        return df[column] >= value
    elif operator == '<=':
        return df[column] <= value
    elif operator == '>':
        return df[column] > value
    elif operator == '<':
        return df[column] < value
    elif operator == '!=':
        return df[column] != value
    else:
        raise ValueError(f"Unrecognized operator: {operator}")

def compile_conditions(df: pd.DataFrame, 
                       complex_condition: str) -> pd.Series:
    """
    Function that evaluates complex logical conditions, where there are operators & and
    |, divides into individual conditions, and evaluates them in the stata_condition function,
    then performs the corresponding |/& operations.
    ----------
    df : pd.DataFrame
        DataFrame to evaluate conditions.
    complex_condition : str
        complex logical condition.
        examples of complex_condition = "year == 1978 & country == 'Chile'",
        "inlist(country, 'Chile', 'Argentina') | country == 'Bolivia'"
    Returns
    -------
    pd.Series
        Boolean series of the evaluated complex condition
    """
    
    # Create a copy of the original DataFrame
    df = df.copy()
    # Split the complex condition into individual parts using logical operators
    conditions = re.split(r'\s*(&|\|)\s*', complex_condition)

    # Initialize the result as a series of True (to comply with all conditions)
    result = pd.Series(True, index=df.index)
    
    # Split the complex condition into parts using a regular expression that identifies the operators
    parts = re.split(r'\s*(&|\|)\s*', complex_condition)
    conditions = parts[::2]  # The conditions are in even positions
    operators = parts[1::2]  # The operators are in odd positions
    
    # Initialize the result with the first condition
    result = condition(df, conditions[0].strip())
    
    # Iterate through the remaining conditions and operators, applying each operator with its corresponding condition
    for i in range(len(operators)):
        condition_result = condition(df, conditions[i + 1].strip())
        operator = operators[i].strip()
        if operator == '&':
            result &= condition_result
        elif operator == '|':
            result |= condition_result

    return result


def clear_text(text, sec):
    # Replace multiple whitespace with a single space and remove leading/trailing whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # If the pattern 'sec' is found in the text, remove all parentheses
    if re.findall(sec, text):
        text = re.sub(r'[()]', '', text).strip()
    # If the text starts with '(' but doesn't end with ')', append ')'
    elif text.startswith('(') and not text.endswith(')'):
        text += ')'
    # If the text ends with ')' but doesn't start with '(', prepend '('
    elif not text.startswith('(') and text.endswith(')'):
        text = '(' + text
    # If the text doesn't contain either '(' or ')', enclose it in parentheses
    elif '(' not in text and ')' not in text:
        text = '(' + text + ')'

    return text

def normalize_text(text):
    # Replace multiple whitespace with a single space and remove leading/trailing whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Regular expression pattern to match certain logical operator-related sequences
    sec = r"(\)\s*&)|(&\s*\()|(\)\s*\|)|(\|\s*\()"

    # Split the text based on the pattern and clear each part using the clear_text function
    parts = re.split(sec, text)
    
    if len(parts)>1:
        parts = [clear_text(p, sec=sec) for p in parts if p]
        # Join the parts back together into a normalized text string
        norm_text = " ".join(parts)
    else:
        norm_text = text
    # If double parentheses are found with possible spaces between them, raise an error
    if re.search(r'\(\s*\(', text) or re.search(r'\)\s*\)', text):
        raise ValueError(f"Logical operator control does not handle double parentheses in: {text}")

    return norm_text

def evaluate_condition(df: pd.DataFrame,
                             complex_condition: str) -> pd.Series:
    """
    Function that evaluates complex logical conditions, where there are operators & and
    |, grouped in parentheses.
    It divides into groups of parentheses, and evaluates in compile_conditions,
    then performs the corresponding |/& operations between the groups.
    ----------
    df : pd.DataFrame
        DataFrame to evaluate conditions.
    complex_condition : str
        complex logical condition.
        examples of complex_condition = "(year == 1978 & country == 'Chile') | (year == 1978 & country == 'Argentina')",
        "(inlist(country, 'Chile', 'Argentina') | country == 'Bolivia) | (year == 2000)"
    Returns
    -------
    pd.Series
        Boolean series of the evaluated complex condition
    """

    # Create a copy of the original DataFrame
    df = df.copy()
    # Normalize text in complex_condition
    complex_condition = normalize_text(complex_condition)
    # Split to separate the () blocks by ")&(" and ")|("
    parts = re.split(r'\)\s*\|\s*\(|\)\s*&\s*\(', complex_condition)
    if len(parts) > 1:
        parts[0] = parts[0][1:]
        parts[-1] = parts[-1][0:-1]
    # Retrieve orderly & and |
    operators = re.findall(r'\)\s*([&|])\s*\(', complex_condition)

    # Evaluate the conditions in each () block

    parts_results = [compile_conditions(df, p) for p in parts]

    # Compute condition of the results in each ()
    result = parts_results[0]
    i = 1
    for o in operators:
        if o == "&":
            result &= parts_results[i]
        if o == "|":
            result |= parts_results[i]
        i += 1
    return result