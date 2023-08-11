
import pandas as pd
import numpy as np
from gapminder import gapminder as df
from typing import Union, List

# Cargar el DataFrame de Gapminder


def tab(df: pd.DataFrame, 
        col: Union[str, List[str]], 
        nofreq: bool = False,
        sort: bool = False,
        round_decimals: int = 2, 
        reset_index: bool = True,
        missing: bool = False,
        total: bool = False) -> pd.DataFrame:
    
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

    # Print and return the result
    print(result)
    return result

df = df.sample(frac=0.8)
prob_missing = 0.1
mask = np.random.rand(df['year'].shape[0]) < prob_missing
df.loc[mask, 'year'] = np.nan
prob_missing = 0.1
mask = np.random.rand(df['continent'].shape[0]) < prob_missing
df.loc[mask, 'continent'] = np.nan

result = tab(df,["year"],sort=False,reset_index=True,nofreq=False,missing=True, total  = True)


result = tab(df,["year","continent"],sort=False,reset_index=True,nofreq=False,missing=True)


