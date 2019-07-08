import pandas as pd
from pulp import *
import numpy as np
import matplotlib.pyplot as plt
import time

from basic_model import cost_calculation as cost_cal_basic
from extension1_0 import cost_calculation as cost_cal_extension_1_0
from extension1_1 import cost_calculation as cost_cal_extension_1_1


#====Read the dataframes mentioned above=====
df = pd.read_excel("nutrition.xlsx",nrows=64)
nutrition_df=pd.read_excel('quantity.xlsx')
cost_df_raw=pd.read_excel('costs.xlsx')
ingre_percentage_df=pd.read_excel('ingredients_percentage.xlsx')
#===============================================

result1=cost_cal_basic(df,nutrition_df,cost_df_raw)

result2=cost_cal_extension_1_0(df,nutrition_df,cost_df_raw,ingre_percentage_df)

result3=cost_cal_extension_1_1(3,df,nutrition_df,cost_df_raw)
print('====Result of Basic model====\n')
print(result1)
print('====Result of Extension 1_0=====\n')
print(result2)
print('=====Result of Extension 1_1======\n')
print(result3)