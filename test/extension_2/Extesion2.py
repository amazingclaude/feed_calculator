# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 10:23:13 2019
@author: ZeynabR
Input: 
 1.  
 Nutrition_ingredient included compounds.xlsx => it contains ingredient(also compound ingredients which are assumed to have an equal percentage for different ingredien) 
 and the amount of nutrition in each of it.
 2. 'example fc.xlsx', sheet_name='Layer feed rules' => it contaons the rules(min and max value of ingredients and nutrition) of feeding animals
 3. 'Price.xlsx' => this file contains the price of all kind of ingredient(compound ingredients included)
 4. 'compound ingredient.xlsx' => this file contains the compound ingredients and the percentage of each ingredient in them.

Output:
    As an output we will have the name of the ingredient in optimized recipe and percentage of each for a portion. 
"""

# Import Packages
import time
start_time = time.time()
import pandas as pd
from pulp import*
import numpy as np

start_time = time.time()
# Import datasets and clean it
df = pd.read_excel('Nutrition_ingredient included compounds.xlsx')
dfc = pd.read_excel('example fc.xlsx', sheet_name='Layer feed rules')
Price = pd.read_excel('Price.xlsx')
constraint = dfc.iloc[:, 0:4]
nutritionC = constraint.iloc[0:16,:]
nutritionC.drop(index =[9],inplace=True)
nutritionC['Minimum'].fillna(value = 0, inplace = True)
nutritionC.reset_index(inplace = True)
ingredientC = constraint.iloc[20:68,:]
ingredientC.drop(index=[59], inplace=True)
ingredientC['Minimum'].fillna(value = 1, inplace = True)
ingredientC.rename(columns={'Afkorting in WEBCALCULATOR':'Ingredient'},inplace=True)
ingredientC.reset_index(inplace = True)
compound_ingredient = pd.read_excel('compound ingredient.xlsx')
compound_ingredient.fillna(value = 0, inplace = True)
compound_ingredient.set_index('Ingredient', inplace = True)

# Merging 
dfM = pd.merge(ingredientC,df,how='inner',on='Ingredient')
dfM = pd.merge(dfM,Price,how='inner',on='Ingredient')

# Function for Extension 2 which covers constrains for nutrition, Ingredient and Compound ingredient 
def FeedOptimization(dfM,dfc,compound_ingredient,nutritionC, ingredientC):
    # Create Lp
    prob = LpProblem('DietProblem', LpMinimize)
    
    # Parameters
    food_item = list(dfM['Ingredient'])
    food_compound_item = food_item[39:47]
    Cost =dict(zip(food_item,dfM['price']))
    nutrition = dfM.iloc[:,4:77] 
    for i in range(70):
        vars()[nutrition.columns[i]]=dict(zip(food_item,nutrition[nutrition.columns[i]]))
    for i in range(39):
        vars()[compound_ingredient.columns[i]]=dict(zip(food_compound_item,compound_ingredient[compound_ingredient.columns[i]]))
    
    # Decision variable
    food_var = LpVariable.dicts("Food", food_item, lowBound=0, cat="Continous")
    included_recipe = LpVariable.dicts( "Chosen", food_item,0,1 ,LpInteger)
    
    # Objective Function
    prob += lpSum([Cost[i]*food_var[i] for i in food_item])
    
    #Constraint
    # For Nutrition
    for i in range(len(nutritionC)):
        n = vars()[nutritionC.iloc[i,1]]
    #print(i)
    prob += lpSum([n[f]* food_var[f] for f in food_item]) >= nutritionC['Minimum'][i]
    if (i in nutritionC[nutritionC['Maximum']>0].index):
        prob += lpSum([n[f]* food_var[f] for f in food_item]) <= nutritionC['Maximum'][i]
    
    # For Binay Variable(Connection Between two decision vaiables) 
    for f in food_item:
        prob += food_var[f]>=0
        prob += food_var[f]<= included_recipe[f] * 10000
    
    # The constrain for Ingredient
    for i in food_item:
        j = list(ingredientC[ingredientC['Ingredient']== i].index)
        Min = ingredientC['Minimum'][j[0]]/100
        Max = ingredientC['Maximum'][j[0]]/100
        prob += food_var[i] >= Min*lpSum(food_var[f] for f in food_item)+ 100*(included_recipe[i]-1) 
        if (ingredientC['Maximum'][j[0]] > 0):
            prob += food_var[i] <= Max*lpSum(food_var[f] for f in food_item)
    
    # The constrain for Comppound Ingredient
    for i in range(len(ingredientC)-len(compound_ingredient)):
        n = vars()[ingredientC.iloc[i,1]]
        g = ingredientC.iloc[i,1]
        #print(i)
        prob += (food_var[g] + lpSum([n[f]* food_var[f] for f in food_compound_item])) >= (ingredientC['Minimum'][i]/100)*lpSum(food_var[n] for n in food_item)+(included_recipe[g]-1) * 100
        if (i in ingredientC[ingredientC['Maximum']>0].index):
            prob += (food_var[g] + lpSum([n[f]* food_var[f] for f in food_compound_item])) <= (ingredientC['Maximum'][i]/100)*lpSum(food_var[n] for n in food_item)

    prob.solve()
    s= 0
    for v in prob.variables():
        if v.varValue>0 and v.name[0]=='F':
            s+=v.varValue
    Ingredient_name = []
    Ingredient_value = []
    for v in prob.variables():
        if v.varValue>0 and v.name[0]=='F':
            Ingredient_name.append(v.name)
            Ingredient_value.append((v.varValue/s)*100)
    
    return Ingredient_name, Ingredient_value

Ingredient_name, Ingredient_value = FeedOptimization(dfM,dfc,compound_ingredient,nutritionC, ingredientC)
for i in range(len(Ingredient_name)):
    print('%s =%.1f %%' %(Ingredient_name[i],Ingredient_value[i]))

print("--- %s seconds ---" % (time.time() - start_time))






