import pandas as pd
from pulp import *
import numpy as np
import matplotlib.pyplot as plt
import time

#######Interface########################################
#The input are three dataframes
#1. nutrition dataframe, in the form of nutrition.xlsx
#2. ingredients dataframe, in the form of quantity.xlsx
#3. costs dataframe, in the form of costs.xlsx

#the output is two vectors, cost_vec and MaxNumVec, which 
#can be used to draw the plot
#############################################################

#===Add the time measurement=================
start=time.time()
#============================================


#====Read the dataframes mentioned above=====
df = pd.read_excel("nutrition.xlsx",nrows=64)
nutrition_df=pd.read_excel('quantity.xlsx')
cost_df_raw=pd.read_excel('costs.xlsx')
#===============================================

#=====Process the dataframes=============================
np.random.seed(0)
df.columns = ['ingredient' if col.startswith('INGREDIENT') else col for col in df]
food_items = list(df['ingredient'])
food_items_df=pd.DataFrame(food_items,columns=['food'])
costs_df=food_items_df.merge(cost_df_raw,left_on='food',right_on='Ingredients')
costs_df=costs_df.drop('food',axis=1)
costs={}
for i in range (len(costs_df)):
    costs[costs_df['Ingredients'].iloc[i]]=costs_df['Price'].iloc[i]
	
#===========================================================

#===def input==================================================
#MaxNum: the maximum ingredients to be used: int
#nutrition_df: nutrition dataframe: pandas dataframe, in the form of nutrition.xlsx
#food_items: the ingredients included: list
#costs: costs for every ingredient: dictionary
#===========================================================
def cost_calculation(MaxNum,nutrition_df, food_items, costs):
	
    #Extract all the nutritions included
    nutrition=[]
    for i in range (len(nutrition_df)):
        nutrition.append(nutrition_df.iloc[i][0])
    #Create dictionay for every single nutrition. The dictionary includes the amount contained in different ingredient.
    for i in range(len(nutrition)):
        vars()[nutrition[i]] = dict(zip(food_items,df[nutrition[i]]))
    
    food_vars = LpVariable.dicts("Portion",food_items,lowBound=0,cat='Continuous')
    
    food_chosen = LpVariable.dicts("Chosen",food_items,0,1,cat='Integer')
    
    prob2 = LpProblem("Smallholder Layer Starter Diet",LpMinimize)

    # The objective function is added to 'prob' first
    prob2 += lpSum([costs[i]*food_vars[i] for i in food_items]), "Total Cost of the balanced diet"

    for i in range(len(nutrition_df)):
        n = vars()[nutrition_df.iloc[i,0]]
        prob2 += lpSum([n[f]* food_vars[f] for f in food_items]) >= nutrition_df['Minimum'][i]
        if (i in nutrition_df[nutrition_df['Maximum']>0].index):
            prob2 += lpSum([n[f]* food_vars[f] for f in food_items]) <= nutrition_df['Maximum'][i]

    for f in food_items:
        prob2 += food_vars[f]>= 0

        prob2 += food_vars[f]<= food_chosen[f]*1e5
    prob2+= lpSum([food_chosen[f] for f in food_items])<=MaxNum
    # The problem is solved using PuLP's choice of Solver
    prob2.solve(pulp.PULP_CBC_CMD())

    return round(value(prob2.objective),2)

#====Main================================================
cost_vec=[]
MaxNumVec=[]
for MaxNum in range (3,12):
    cost=cost_calculation(MaxNum,nutrition_df,food_items,costs)
    MaxNumVec.append(MaxNum)
    cost_vec.append(cost)
#========================================================

#=========End of the solving time===========================
end=time.time()
print('Total solving time is:',end-start,'seconds')
#=============================================================

#====Draw the plot==============================
plt.plot(MaxNumVec,cost_vec)
plt.ylabel('Optimized Minimum cost')
plt.xlabel('Maxmum number of ingredients chosen')
plt.show()
#=================================================


