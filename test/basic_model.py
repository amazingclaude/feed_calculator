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

#The output is result_df
#############################################################

#===Add the time measurement=================
start=time.time()
#============================================

#====Read the dataframes mentioned above=====
df = pd.read_excel("nutrition.xlsx",nrows=64)
nutrition_df=pd.read_excel('quantity.xlsx')
cost_df_raw=pd.read_excel('costs.xlsx')
#===============================================

def cost_calculation(df,nutrition_df,cost_df_raw):

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
	#Extract all the nutritions included
	nutrition=[]
	for i in range (len(nutrition_df)):
		nutrition.append(nutrition_df.iloc[i][0])
	#Create dictionay for every single nutrition. The dictionary includes the amount contained in different ingredient.
	for i in range(len(nutrition)):
		vars()[nutrition[i]] = dict(zip(food_items,df[nutrition[i]]))
	food_vars = LpVariable.dicts("Portion",food_items,lowBound=0,cat='Continuous')
	#===========================================================


	prob = LpProblem("Smallholder Layer Starter Diet",LpMinimize)
	# The objective function is added to 'prob' first
	prob += lpSum([costs[i]*food_vars[i] for i in food_items]), "Total Cost of the balanced diet"
	for i in range(len(nutrition_df)):
		n = vars()[nutrition_df.iloc[i,0]]
	#     print('Min',i)
		
		prob += lpSum([n[f]* food_vars[f] for f in food_items]) >= nutrition_df['Minimum'][i]
		if (i in nutrition_df[nutrition_df['Maximum']>0].index):
	#         print('Max',i)
			prob += lpSum([n[f]* food_vars[f] for f in food_items]) <= nutrition_df['Maximum'][i]
	#     print('------')


	# The problem data is written to an .lp file
	prob.writeLP("SimpleDietProblem.lp")
	# The problem is solved using PuLP's choice of Solver
	prob.solve(pulp.PULP_CBC_CMD())

	#=========End of the solving time===========================
	end=time.time()
	print('Total solving time is:',end-start,'seconds')
	#=============================================================
	
	#====Print the result==================================
	# print("Solution"+"-"*100)
	# for v in prob.variables():
		# if v.varValue>0 and v.name[0]=='P':
			# print(v.name, "=", v.varValue,'kg')
	# print("The total cost of this balanced diet is: {} in Nigeria Currency ".format(round(value(prob.objective),2)))
	#=========================================================
	
	#=====Write into the dataframe====================
	Ingredients=[]
	Amount=[]
	for v in prob.variables():
		if v.varValue>0 and v.name[0]=='P':
			Ingredients.append(v.name[8:])
			Amount.append(v.varValue)
	
	total_cost=round(value(prob.objective),2)
	result_df={'Ingredients':Ingredients,'Amount':Amount}
	result_df=pd.DataFrame(result_df)
	result_df['total_cost']=total_cost
	#===================================================
	return result_df