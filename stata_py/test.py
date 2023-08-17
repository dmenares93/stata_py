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






