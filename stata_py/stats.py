
import pandas as pd
from typing import Union, List
from  control import evaluate_condition
from typing import Union, List
import re
import numpy as np



def tab(df: pd.DataFrame, 
        col: Union[str, List[str]], 
        nofreq: bool = False,
        sort: bool = False,
        round_decimals: int = 2, 
        reset_index: bool = True,
        missing: bool = False,
        total: bool = False,
        if_stata: str = None,
        percent: str = None,
        w: pd.Series = None) -> pd.DataFrame:
 
    """
    Function that replicates the tab function.
    ----------
        df: pd.DataFrame, dataframe to evaluate the tab function.
        col: Union[str, List[str]], variables from df to tabulate.
        nofreq: bool = False, to compute frequencies.
        sort: bool = False, to sort by frequencies.
        round_decimals: int = 2, to round the results.
        reset_index: bool = True, to delete the index of variables.
        missing: bool = False, to handle missing values.
        total: bool = False, to add the total.
        if_stata: str = None, control conditions.
        percent: str = None, control mode percentage with: col, row or cell .
        w: pd.Series = None, expansion factor.
    Returns
    -------
    pd.DataFrame
        table with the tabulation results.
    """
    
    
    # Check if the df is a pandas DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    # Check if col is a list of two strings or a single string
    if isinstance(col, list):
        if len(col) not in [1, 2] or not all(isinstance(item, str) for item in col):
            raise TypeError("col must be a string or a list of two strings")
    elif not isinstance(col, str):
        raise TypeError("col must be a string or a list of two strings")
   
    # Convert col to a list if it's a string
    if isinstance(col, str):
        col = [col]

    df = df.copy()

    # Handle missing w condition
    #if w:
    #    for x in col:
    #        df[x] = df[x]*df[w]
            
    # Handle missing if_stata condition
    if if_stata:
        df = df[evaluate_condition(df,if_stata)]
    
    # Handle missing option
    if missing:
        for x in col:
            df[x] = df[x].fillna('_nan').astype(str)

    # Case when col contains one string
    if len(col) == 1:
        col1 = df[col[0]].value_counts()
        # Handle total option (1/2)
        if total:
            col1.loc['_total'] = col1.sum()
        result = pd.DataFrame()
        
        # Handle missing option
        if not nofreq:
            result["N"] = col1
            
        col2 = (df[col[0]].value_counts(normalize=True) * 100)
        # Handle total option (2/2)
        if total:
            col2.loc['_total'] = col2.sum()
            
        if round_decimals:
            result["%"] = col2.round(round_decimals)
        
        # Handle the reset_index and sort options
        if reset_index and sort:
            result = result.reset_index().rename(columns={"index": col[0]}).sort_values("%", ascending=False).reset_index(drop=True)
        elif reset_index and not sort:
            result = result.reset_index().rename(columns={"index": col[0]}).sort_values(col[0], ascending=True).reset_index(drop=True)
        elif not reset_index and not sort:
            result.sort_index(ascending=True, inplace=True)
        elif not reset_index and sort:
            result.sort_values("%", ascending=False, inplace=True) 
        
    # Case when col contains two strings
    if len(col) == 2:
        result = pd.crosstab(df[col[0]], df[col[1]])
        
        # Handle the reset_index and sort options
        if percent == "col":     
            result =  result.div(result.sum(axis=0),axis = 1)          
        if percent == "row":
            result =  result.div(result.sum(axis=1),axis = 0)
        if percent == "cell":
            result =  result/result.sum().sum()
    
        for col in result.columns:
            if result[col].dtype == 'float64':
                result[col] = result[col].round(round_decimals)
        
    return result


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


def table(df: pd.DataFrame, 
          var: Union[str, List[str]], 
          stats: str,
          pivot:bool = True,
          round_decimals: int = 2,
          if_stata: str = None,
          w: pd.Series = None) -> pd.DataFrame:

    """
    Function that replicates the table function.
    ----------
        df: pd.DataFrame, dataframe to evaluate the tab function.
        var: Union[str, List[str]], variables from df to tabulate.
        pivot: bool = True, to transpose the table results.
        round_decimals: int = 2, to round the results.
        if_stata: str = None, control conditions.
        w: pd.Series = None, expansion factor.
    Returns
    -------
    pd.DataFrame
        table with the tabulation results.
    """
    
    # Check if the df is a pandas DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    # Check if col is a list of two strings or a single string
    if isinstance(var, list):
        if len(var) not in [1, 2] or not all(isinstance(item, str) for item in var):
            raise TypeError("col must be a string or a list of two strings")
    elif not isinstance(var, str):
        raise TypeError("col must be a string or a list of two strings")
   
    # Convert col to a list if it's a string
    if isinstance(var, str):
        var = [var]
    # Copy dataframe
    df = df.copy()

    # Handle missing if_stata condition
    if if_stata:
        df = df[evaluate_condition(df,if_stata)]

    # Define operations
    oper =  [
    'sum',      # Sum of elements
    'mean',     # Compute the arithmetic mean
    'median',   # Compute the median
    'min',      # Find the minimum value
    'max',      # Find the maximum value
    'prod',     # Compute the product of elements
    'std',      # Compute the standard deviation
    'var',      # Compute the variance
    'count',    # Count the number of non-null elements
    'nunique',  # Count the number of unique elements
    'first',    # Get the first non-null element
    'last',     # Get the last non-null element
    'p1/p100'   # Compute the percentile
    ]

    # Translate stats to dict for evalute in .agg
    dic=  dic_stats(stats, oper)
    
    # Handle missing w condition
    #stats_var = list(mi_diccionario.keys())
    #if w:
    #    for x in stats_var:
    #        df[x] = df[x]*df[w]
    
    # Compute stats
    table = df.groupby(var).agg(dic).reset_index()

    # Fix columns name
    columns = table.columns
    new_columns = [f'{col[0]} ({col[1]})' if col[1] else col[0] for col in columns]
    table.columns = new_columns

    # Handle pivot option
    if pivot == True and len(var)==2:
        stats_var = [x for x in new_columns if x not in var]
        table = table.pivot(index=var[0], columns=var[1], values=stats_var)
        nuevas_columnas = [f"{year} - {label}" for label, year in table.columns]
        table.columns = nuevas_columnas

    # Handle round_decimals option
    if round_decimals:
        table = table.apply(lambda col: col.round(round_decimals) if col.dtype == 'float64' else col)
    
    return table



def count(df: pd.DataFrame, 
          if_stata: str = None,
          ) ->int:

    """
    Function that replicates the table function.
    ----------
        df: pd.DataFrame, dataframe to evaluate the tab function.
        var: Union[str, List[str]], variables from df to tabulate.
        pivot: bool = True, to transpose the table results.
        round_decimals: int = 2, to round the results.
        if_stata: str = None, control conditions.
        w: pd.Series = None, expansion factor.
    Returns
    -------
    pd.DataFrame
        table with the tabulation results.
    """
    
    # Handle missing if_stata condition
    if if_stata:
        df = df[evaluate_condition(df,if_stata)]

    n = len(df)
    
    return n