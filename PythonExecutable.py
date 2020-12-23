#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Will need to import these modules. 
import sys
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm 
#import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


# In[ ]:



def hello(a, b, c):

if __name__== "__main__":
    hello(int(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]))


# In[ ]:





# In[2]:


#Below is user defined parameters
Use1file1= c
n= a
index = b


# In[3]:


my_data = pd.read_csv(Use1file1, index_col = 'Date')
#Assigning Variable to itself to surpress output
#I have to rename column headers because I will be undsure of the exact strings used in the csv uploaded to the program
#In both the prompt and examples, the strings were different.
my_data = my_data.rename(index={0: "Date", 1: "Symbol", 2: "Close"})


# In[4]:


#Group by similar symbols so that I can compare averages
symbols = my_data.groupby('Symbol')
jim2 = symbols.agg({"Close": [np.mean, np.std]})
jim= jim2['Close']
#Coefficeint of varations- CoeffVar.
#See attached document for why I chose volatility.
jim['CoeffVar']= (jim['std']/jim['mean'])*100
#I am going to subract each Coeffvar against the index's coeffvar. I am trying to minimize the difference in volatilities.
#The lower the DiffofIndex (The difference between volatility of index and the stock) the higher the probability 
#the stocks fluctuate together.
Rank_Value = jim.get_value(index, 'CoeffVar')
jim['DiffofIndex']= (jim['CoeffVar']-Rank_Value)
#Sorting them will allow me to rank order which stocks have closest volatility to index. 
jim = jim.sort_values(by='DiffofIndex', ascending=True)


# In[6]:


#Dropping the index before we rank order is ideal as we don't want to rank DJI as 1 since it is our benchmark
jim = jim.drop(index)
#Below is the script for rank ordering. In this case I need to generate 30 rows. I need a way of generating rank ordered numbers
#that is not index dependent, since the given CSV may be the S&P500 or another, different numbered index. 
total_rows = jim.shape[0] + 1
jim["RankOrd"] = range(1,total_rows)
jim["RankOrd"] = range(1,total_rows)
#The first stock, VZ has a adjusted volatility very similar to the index itself.


# In[8]:


#We will take the top n securities as the data to be used in the regression
data_top = jim.iloc[0:n]
# This grabs the tickers that we will seperate from the long list
tickers = list(data_top.index)
#We will need to add the index(.DJI) so we can grab its data with all the other data in one move. 
tickers.append(index)


# In[9]:


#This collects the index plus top n tickers
my_new_data = my_data[my_data['Symbol'].isin(tickers)]
#Have to reset index for .pivot to work
my_new_data = my_new_data.reset_index()
#.pivot will generate the data into a form that works best with regression analysis.
final = my_new_data.pivot(index='Date', columns='Symbol', values='Close')


# In[11]:


#We will now start to calculate returns that we will use in the regression
#Variable below produces a data table that calculates simple retunrs
returns = (final / final.shift(1)) - 1
#The below function calls a method named resent and index. these functions have nothing to do with variable index
returns1 = returns.reset_index()
#Below allows me to drop the first line which is NaN beause each cell is calcualted from a prior timestep. 
returns1 = returns1.drop(returns1.index[0])
#I am taking the ticker's names below so I can use them as the regressors for the regression
New_tickers= list(returns1.columns) 


# In[12]:


#I have to remove these becuase I am seperating x variables from y variables.
New_tickers.remove('Date')
New_tickers.remove(index)


# In[13]:


#Set up the regression model- OLS
X = returns1[New_tickers]
Y = returns1[index]
X1 = sm.add_constant(X)
reg = sm.OLS(Y, X1).fit()
#reg.summary()


# In[14]:


#Grab the correlation values of the tickers
fun123 = reg.params
#Dropping the first row since it is the constant.
fun123= fun123.iloc[1:]
#That expression is all the correlation not covered in the regresion
j = 1 - fun123.sum(axis = 0, skipna = True) 
#q is how many regressors there are
q = len(fun123)
#j is what remains that cannot be explained by the regressors (I.e. not capatured in the model)
#for purposes here, we have to assume it is random and distributed evenly against all parameters.
#q allows me to split up evenly what is not captured by my model
m = j/q
#I will add m to every correlation coeffecient evenly. 


# In[16]:


#Want to work with these coefficients in a dataframe so I can print them to a csv easily
z = fun123.to_frame()
# Current Index will be too problematic to label
z = z.reset_index()
#This is to label the Symbols to help with CSV presentation
z.columns = ['Symbol','Coefficient']
#This generates the Weights column that scales what each allocation should be, totaling 100%
z['Weight']= (z.iloc[:,1] + m)
#Want to drop the coeffecients column
z= z.drop(z.columns[1],axis=1)
z= z.set_index('Symbol')
#Prints the desired csv with the correct format
z.to_csv('approximation.csv')

