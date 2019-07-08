import pandas as pd
from pulp import *
import numpy as np
import matplotlib.pyplot as plt
import time

from basic_model import cost_calculation 
#====Read the dataframes mentioned above=====
df = pd.read_excel("nutrition.xlsx",nrows=64)
nutrition_df=pd.read_excel('quantity.xlsx')
cost_df_raw=pd.read_excel('costs.xlsx')
#===============================================

result=cost_calculation(df,nutrition_df,cost_df_raw)
print(result)