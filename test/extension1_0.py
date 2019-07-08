import pandas as pd
from pulp import *
import numpy as np
import matplotlib.pyplot as plt
import time

#######Interface###########################################
#The input are four dataframes
#1. nutrition dataframe, in the form of nutrition.xlsx
#2. ingredients dataframe, in the form of quantity.xlsx
#3. costs dataframe, in the form of costs.xlsx
#4. ingredient_percentage dataframe, in the form of ingredient_percentage.xlsx

#The output is result_df_extention1_0
#############################################################

#===Add the time measurement=================
start=time.time()
#============================================

#====Read the dataframes mentioned above=====
df = pd.read_excel("nutrition.xlsx",nrows=64)
nutrition_df=pd.read_excel('quantity.xlsx')
cost_df_raw=pd.read_excel('costs.xlsx')
ingre_percentage_df=pd.read_excel('ingredients_percentage.xlsx')
#===============================================



def cost_calculation(df, nutrition_df, cost_df_raw,ingre_percentage_df):

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
	#Extract all the nutritions included
	nutrition=[]
	for i in range (len(nutrition_df)):
		nutrition.append(nutrition_df.iloc[i][0])
	#Create dictionay for every single nutrition. The dictionary includes the amount contained in different ingredient.
	for i in range(len(nutrition)):
		vars()[nutrition[i]] = dict(zip(food_items,df[nutrition[i]]))
	food_vars = LpVariable.dicts("Portion",food_items,lowBound=0,cat='Continuous')
	prob3 = LpProblem("Smallholder Layer Starter Diet",LpMinimize)
	prob3 += lpSum([costs[i]*food_vars[i] for i in food_items]), "Total Cost of the balanced diet"
	food_chosen = LpVariable.dicts("Chosen",food_items,0,1,cat='Integer')

	for i in range(len(nutrition_df)):
		n = vars()[nutrition_df.iloc[i,0]]
	#     print(n)
	#     print('Min',i)
		
		prob3 += lpSum([n[f]* food_vars[f] for f in food_items]) >= nutrition_df['Minimum'][i]
		
		if (i in nutrition_df[nutrition_df['Maximum']>0].index):
	#         print('Max',i)
			prob3 += lpSum([n[f]* food_vars[f] for f in food_items]) <= nutrition_df['Maximum'][i]
	#     print('------')

	for f in food_items:
		prob3 += food_vars[f]>= 0
		prob3 += food_vars[f]<= food_chosen[f]*100

	#Unlock the maximum number of the ingredients (so that extension 1_1 is combined.)   
	# prob3+= lpSum([food_chosen[f] for f in food_items])<=6


	for i in range(len(ingre_percentage_df)):
		pmin=ingre_percentage_df.iloc[i][2]/100
		x_i=ingre_percentage_df.iloc[i][0]
		prob3 += -100*(1-food_chosen[x_i])+pmin*lpSum([food_vars[f] for f in food_items])<=food_vars[x_i]
		
		if (i in ingre_percentage_df[ingre_percentage_df['Maximum']>0].index):
	#         print('Max',i)
			pmax=ingre_percentage_df.iloc[i][3]/100
			prob3 += pmax*lpSum([food_vars[f] for f in food_items])>=food_vars[x_i]
																			  

	# The problem is solved using PuLP's choice of Solver
	prob3.solve(pulp.PULP_CBC_CMD())



	#=========End of the solving time===========================
	# end=time.time()
	# print('Total solving time is:',end-start,'seconds')
	#=============================================================
	
	#====Printing================================
	# print("Solution"+"-"*100)

	# for v in prob3.variables():
		# if v.varValue>0 and v.name[0]=='P':
	# #     if v.varValue>0 :
			# print(v.name, "=", v.varValue,'kg')
	# print("The total cost of this balanced diet is: {} in Nigeria Currency ".format(round(value(prob3.objective),2)))
	#==============================================
	
	
	Ingredients=[]
	Amount=[]
	for v in prob3.variables():
		if v.varValue>0 and v.name[0]=='P':
			Ingredients.append(v.name[8:])
			Amount.append(v.varValue)
	total_cost=round(value(prob3.objective),2)
	result_df_extention1_0={'Ingredients':Ingredients,'Amount':Amount}
	result_df_extention1_0=pd.DataFrame(result_df_extention1_0)
	result_df_extention1_0['total_cost']=total_cost
	return result_df_extention1_0