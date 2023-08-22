
import pandas as pd
from typing import Union, List
from  .control import evaluate_condition
from openpyxl.styles import Border, Side, Alignment, PatternFill, Font
from  tools import dic_stats


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
    Function that replicates the tabulation function, providing a table with counts and percentages.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the data to be tabulated.
    col : Union[str, List[str]]
        Column(s) from df to tabulate. Either a single string or a list of one or two strings.
    nofreq : bool, optional (default=False)
        If False, frequencies are computed; if True, frequencies are not computed.
    sort : bool, optional (default=False)
        If True, the results are sorted by frequencies.
    round_decimals : int, optional (default=2)
        Number of decimals to which the results are rounded.
    reset_index : bool, optional (default=True)
        If True, deletes the index of variables.
    missing : bool, optional (default=False)
        If True, handles missing values.
    total : bool, optional (default=False)
        If True, adds the total.
    if_stata : str, optional (default=None)
        Control conditions, following the syntax used in Stata.
    percent : str, optional (default=None)
        Control mode percentage with the options: "col", "row", or "cell".
    w : pd.Series, optional (default=None)
        Expansion factor, typically used for weighted survey data.

    Returns
    -------
    pd.DataFrame
        Table with the tabulation results. Contains counts and percentages based on the given parameters.

    Raises
    ------
    TypeError
        If df is not a DataFrame or col is not a string or a list of one or two strings.

    Notes
    -----
    - If w is provided, each value in the specified col is multiplied by the corresponding value in w.
    - The if_stata parameter allows for complex conditions to filter the DataFrame before tabulation.
    - The percent parameter controls how percentages are computed: by column ("col"), by row ("row"), or by cell ("cell").
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



def table(df: pd.DataFrame, 
          var: Union[str, List[str]], 
          stats: str,
          pivot:bool = True,
          round_decimals: int = 2,
          if_stata: str = None,
          w: pd.Series = None) -> pd.DataFrame:

    """
    Generates a table that computes various statistics based on the given variables.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe on which to evaluate the function.
    var : Union[str, List[str]]
        Variables from df to tabulate. Can be a string or a list of one or two strings.
    stats : str
        Statistics to be calculated, must match the available operations.
    pivot : bool, optional (default=True)
        If True, transposes the table results (useful for cross-tabulations).
    round_decimals : int, optional (default=2)
        Number of decimal places to round the results to.
    if_stata : str, optional (default=None)
        Control conditions, following the syntax used in Stata.
    w : pd.Series, optional (default=None)
        Expansion factor, typically used in survey-weighted data.

    Returns
    -------
    pd.DataFrame
        Table with the tabulation results, including the requested statistics.

    Raises
    ------
    TypeError
        If df is not a DataFrame or var is not a string or a list of one or two strings.

    Notes
    -----
    - Available statistics include: sum, mean, median, minimum, maximum, product, standard deviation, variance, count, number of unique elements, first and last non-null element, percentiles.
    - The if_stata parameter allows complex conditions to filter the DataFrame before tabulation.
    - If w is provided, it is used to weight the calculated statistics.

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
    Returns the count of rows in the DataFrame, optionally filtered by a condition.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame for which to count the rows.
    if_stata : str, optional (default=None)
        Control conditions to filter the DataFrame before counting rows, following the syntax used in Stata.

    Returns
    -------
    int
        Count of rows in the DataFrame after applying any specified conditions.

    Notes
    -----
    - The if_stata parameter allows for complex conditions to filter the DataFrame before counting rows.
    - If no conditions are specified, the function returns the total number of rows in the DataFrame.

    """
    
    # Handle missing if_stata condition
    if if_stata:
        df = df[evaluate_condition(df,if_stata)]

    n = len(df)
    
    return n



def to_excel(data: Union[pd.DataFrame, 
                  List[pd.DataFrame]], path: str, 
                  sheet_names: List[str] = None) -> None:
    """
    Function to write one or multiple DataFrames to an Excel file with custom styling.
    ----------
    data: Union[pd.DataFrame, List[pd.DataFrame]]
        DataFrame or a list of DataFrames that will be written to the Excel file.
    path: str
        Full path to the Excel file where the data will be written.
    sheet_names: List[str], optional
        List of names for the sheets within the Excel file. If omitted, sheets will be named as 'Sheet1', 'Sheet2', etc.

    Returns
    -------
    None
        The function does not return any value but saves the Excel file to the specified location.

    Notes
    -----
    The function applies custom styling to the cells, including thin borders, a maximum column width of 25,
    and blue fill with white font in the first row and first column. The function uses the 'openpyxl' engine
    for writing the Excel file.
    """
    
    # If a single DataFrame is passed, convert it into a list with one element
    if isinstance(data, pd.DataFrame):
        data = [data]

    # Create an Excel writer using Pandas
    writer = pd.ExcelWriter(path, engine='openpyxl')

    # Define border style
    thin_border = Border(left=Side(style='thin'), 
                         right=Side(style='thin'), 
                         top=Side(style='thin'), 
                         bottom=Side(style='thin'))

    # Maximum column width
    max_column_width = 25

    # Define fill for header row and second column
    blue_fill = PatternFill(start_color="1F4E78",
                            end_color="1F4E78",
                            fill_type="solid")
    
    white_font = Font(color="FFFFFF")

    # Write each DataFrame to a different sheet
    for i, df in enumerate(data):
        # Use the custom sheet name if provided, otherwise use a default name
        sheet_name = sheet_names[i] if sheet_names and i < len(sheet_names) else 'Sheet' + str(i+1)
        df.to_excel(writer, sheet_name=sheet_name)

        # Get the sheet to apply styles
        worksheet = writer.sheets[sheet_name]

        # Apply styles to all cells, adjust column width, and set alignment
        for col_idx, column in enumerate(worksheet.columns):
            max_length = max(len(str(cell.value)) for cell in column)
            column_width = min(max_length + 2, max_column_width)
            worksheet.column_dimensions[column[0].column_letter].width = column_width

            alignment = Alignment(horizontal='left') if col_idx == 0 else Alignment(horizontal='right')

            for row_idx, cell in enumerate(column):
                cell.border = thin_border
                cell.alignment = alignment

                # Apply blue fill and white font to first row and second column
                if row_idx == 0 or col_idx == 0:
                    cell.fill = blue_fill
                    cell.font = white_font

    # Save the Excel file
    writer.save()

    