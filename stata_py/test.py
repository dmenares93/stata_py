# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:05:12 2023

@author: UCHILE
"""

from stats import tab, table
from gapminder import gapminder as df


var = "country"
stats = "min year lifeExp max year median gdpPercap"
t = table(df,var = var,stats = stats)
print(t)


var = ["continent","year"]
stats = "min year lifeExp max year median gdpPercap"
print(t)


var = ["continent","year"]
stats = "min lifeExp"
t = table(df,var = var,stats = stats)
print(t)


var = ["continent","year"]
stats = "min lifeExp"
t = table(df,var = var,stats = stats)
print(t)


var = ["continent","year"]
stats = "mean lifeExp"
t = table(df,var = var,stats = stats, if_stata= "continent!='Americas'")
print(t)



tab(df,"country")

r = tab(df,["country","continent"])

tab(df,["country","continent"],percent="cell")


import pandas as pd
from typing import List, Union
from openpyxl.styles import Border, Side, Alignment, PatternFill, Font

def save_to_excel(data: Union[pd.DataFrame, List[pd.DataFrame]], path: str, sheet_names: List[str] = None) -> None:
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

    
# Ejemplo de uso
path = r"C:\Users\Daga\Desktop\prueba\ver4.xlsx"
df = [t,r]
name = ["tabla t","tabla r"]
save_to_excel(df, path, sheet_names=name)