# Data Stats Library

This library contains a collection of functions designed to make working with pandas data sets easier. Below, you will find a description of each of them:

## Installation

Open a terminal and run:

```bash
pip install git+https://github.com/dmenares93/stata_py
```

## Functions

### 1. `tab`

Function that replicates the tabulation function, providing a table with counts and percentages.

```python
tab(df: pd.DataFrame, col: Union[str, List[str]], nofreq: bool = False,
sort: bool = False, round_decimals: int = 2, reset_index: bool = True,
missing: bool = False, total: bool = False, if_stata: str = None,
percent: str = None, w: pd.Series = None) -> pd.DataFrame
```

**Parameters:**

- `df`: `pd.DataFrame` - The DataFrame containing the data to be tabulated.
- `col`: `Union[str, List[str]]` - Column(s) from df to tabulate. Either a single string or a list of one or two strings.
- `nofreq` (optional): `bool` - If False, frequencies are computed; if True, frequencies are not computed. Default is False.
- `sort` (optional): `bool` - If True, the results are sorted by frequencies. Default is False.
- `round_decimals` (optional): `int` - Number of decimals to which the results are rounded. Default is 2.
- `reset_index` (optional): `bool` - If True, deletes the index of variables. Default is True.
- `missing` (optional): `bool` - If True, handles missing values. Default is False.
- `total` (optional): `bool` - If True, adds the total. Default is False.
- `if_stata` (optional): `str` - Control conditions, following the syntax used in Stata. Default is None.
- `percent` (optional): `str` - Control mode percentage with the options: "col", "row", or "cell". Default is None.
- `w` (optional): `pd.Series` - Expansion factor, typically used for weighted survey data. Default is None.

**Returns:**

- `pd.DataFrame` - Table with the tabulation results. Contains counts and percentages based on the given parameters.

**Raises:**

- `TypeError` - If df is not a DataFrame or col is not a string or a list of one or two strings.

**Notes:**

- If `w` is provided, each value in the specified col is multiplied by the corresponding value in `w`.
- The `if_stata` parameter allows for complex conditions to filter the DataFrame before tabulation.
- The `percent` parameter controls how percentages are computed: by column ("col"), by row ("row"), or by cell ("cell").

**Examples:**

```python
from stata_py.stats import tab
from gapminder import gapminder as df

tab(df,"continent")
tab(df,"country", if_stata = "pop>100000000", nofreq = True)
tab(df,"country", if_stata = "pop>100000000", total = True, round_decimals = 3)
tab(df,["country","continent"], if_stata = "pop>100000000")
```

### 2. `table`

Generates a table that computes various statistics based on the given variables.

```python
def table(df: pd.DataFrame, 
          var: Union[str, List[str]], 
          stats: str,
          pivot:bool = True,
          round_decimals: int = 2,
          if_stata: str = None,
          w: pd.Series = None) -> pd.DataFrame:
```

**Parameters:**

- `df`: `pd.DataFrame` - Dataframe on which to evaluate the function.
- `var`: `Union[str, List[str]]` - Variables from df to tabulate. Can be a string or a list of one or two strings.
- `stats`: `str` - Statistics to be calculated, must match the available operations. The accepted operations include:
  - `sum` - Sum of elements
  - `mean` - Compute the arithmetic mean
  - `median` - Compute the median
  - `min` - Find the minimum value
  - `max` - Find the maximum value
  - `prod` - Compute the product of elements
  - `std` - Compute the standard deviation
  - `var` - Compute the variance
  - `count` - Count the number of non-null elements
  - `nunique` - Count the number of unique elements
  - `first` - Get the first non-null element
  - `last` - Get the last non-null element
  - `p1/p100` - Compute the percentile
- `pivot` (optional): `bool` - If True, transposes the table results (useful for cross-tabulations). Default is True.
- `round_decimals` (optional): `int` - Number of decimal places to round the results to. Default is 2.
- `if_stata` (optional): `str` - Control conditions, following the syntax used in Stata. Default is None.
- `w` (optional): `pd.Series` - Expansion factor, typically used in survey-weighted data. Default is None.

**Returns:**

- `pd.DataFrame` - Table with the tabulation results, including the requested statistics.

**Raises:**

- `TypeError` - If df is not a DataFrame or var is not a string or a list of one or two strings.

**Notes:**

- Available statistics include: sum, mean, median, minimum, maximum, product, standard deviation, variance, count, number of unique elements, first and last non-null element, percentiles.
- The `if_stata` parameter allows complex conditions to filter the DataFrame before tabulation.
- If `w` is provided, it is used to weight the calculated statistics.

**Examples:**

```python
from stata_py.stats import table
from gapminder import gapminder as df

table(df,"continent", if_stata = "pop>100000000", stats= "mean gdpPercap", round_decimals = 3)
table(df,"continent", if_stata = "pop>100000000", stats= "mean gdpPercap lifeExp median lifeExp")
table(df,["continent","year"], if_stata = "year>2000", stats= "mean gdpPercap max lifeExp")
table(df,["continent","year"], if_stata = "year>2000", stats= "mean gdpPercap", pivot = False)
```

### 3. `count`

Returns the count of rows in the DataFrame, optionally filtered by a condition.

```python
def count(df: pd.DataFrame, 
          if_stata: str = None) -> int:
```

**Parameters:**
- `df`: `pd.DataFrame` - The DataFrame for which to count the rows.
- `if_stata` (optional): `str` - Control conditions to filter the DataFrame before counting rows, following the syntax used in Stata. Default is None.

**Returns:**
- `int` - Count of rows in the DataFrame after applying any specified conditions.

**Notes:**
- The `if_stata` parameter allows for complex conditions to filter the DataFrame before counting rows.
- If no conditions are specified, the function returns the total number of rows in the DataFrame.

**Examples:**

```python
from stata_py.stats import table
from gapminder import gapminder as df

count(df)
ount(df,if_stata = "lifeExp>70")
```

### 4. `to_excel`

Function to export table in excel

```python
def to_excel(data: Union[pd.DataFrame, 
                  List[pd.DataFrame]], path: str, 
                  sheet_names: List[str] = None) -> None:
 ```
                 
**Parameters:**
- `data`: `Union[pd.DataFrame, List[pd.DataFrame]]` - DataFrame or a list of DataFrames that will be written to the Excel file.
- `path`: `str` - Full path to the Excel file where the data will be written.
- `sheet_names` (optional): `List[str]` - List of names for the sheets within the Excel file. If omitted, sheets will be named as 'Sheet1', 'Sheet2', etc.

**Returns:**
- `None` - The function does not return any value but saves the Excel file to the specified location.

**Notes:**
- The function applies custom styling to the cells, including thin borders, a maximum column width of 25, and blue fill with white font in the first row and first column. The function uses the 'openpyxl' engine for writing the Excel file.

**Examples:**

```python
from stata_py.stats import table
from gapminder import gapminder as df

df1 = table(df,["continent","year"], if_stata = "year>2000", stats= "mean gdpPercap max lifeExp")
df2 = table(df,["continent","year"], if_stata = "year<=2000", stats= "mean gdpPercap max lifeExp")

data = [d1,d2]
sheet_names = [">200","<=2000"]
path = "/stats.xlsx"
 to_excel(data,path, sheet_names = sheet_names )
```

## License
MIT License

