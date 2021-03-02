# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 20:13:38 2021

@author: Sandhya Menon
"""

'''
======================================================================
Import the necessary libraries
======================================================================
'''
import pandas as pd
import numpy as np
import re
import seaborn as sns
import matplotlib.pyplot as plt

'''
======================================================================
Read data from files into variable
======================================================================
'''

stock_data1 = pd.read_csv('Stock_File_1.csv')
stock_data2 = pd.read_csv('Stock_File_2.txt')

'''
======================================================================
Check that the files have been read properly and check 
general structure of data 
======================================================================
'''

stock_data1.head()
stock_data2.head()
stock_data1.info()
stock_data2.info()
'''
=====================================================================
It is established that both files contain similar data variables
with similar data types, hence should be appended after creating
deep copies. This creates a single data set with (165 + 204) rows
=====================================================================
'''

stock_copy1 = stock_data1.copy(deep=True)
stock_copy2 = stock_data2.copy(deep=True)

stock_copy = stock_copy1.append(stock_copy2,ignore_index=True, 
                   verify_integrity= False,sort = False)
stock_copy.info()

'''
=====================================================================
Check that that all data in 'Date' field are valid -Check that it 
is in dd-mmm-yy format and also check that the year is between 
2006 and 2016(ten year data)
Check for duplicates, drop duplicate records if present. Analyse
data types of variables, look for null values
=====================================================================
'''
pattern = '^(([0-9])|([0-2][0-9])|([3][0-1]))\-\
(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\-(([0][6-9])|([1][0-6]))$'


p =re.compile(pattern)
q= [i for i,value in enumerate(stock_copy['Date']) \
                  if p.match(str(value))==None]
print(q) 

#q is an empty list, hence date is in correct format througout 

stock_copy[stock_copy.duplicated(subset=['Date'], keep = False )]
# Shows no duplicates
stock_copy.info()
  
'''
======================================================================
On checking output of .info() command, 'Volume' is object instead of 
int.Check whether volume has non numerical values. Retrieve the index 
of records that have non numeric 'Volume'. Put the non numeric values 
of 'Volume' into a list and run np.unique on the list to find out 
what are the non numeric values. 
======================================================================
'''
a = re.compile("^[0-9]+$")
s = [i for i,value in enumerate(stock_copy['Volume'])\
     if a.match(str(value))==None]

print(s)
non_num_lst =[]
for i in s:
    non_num_lst.append(str(stock_copy.Volume[i]))

np.unique(non_num_lst)

'''
======================================================================
This returns 'zero' as the only unique non numeric value. Replace 
'zero' with the number 0 and convert Volume into data type 'int'
Also make sure Open, High, Low and Close have same value for all
records with 'Volume' =0 - indicating a day when no trading takes
place(-checking for a logical fallacy)
======================================================================
'''

stock_copy['Volume'].replace('zero',0, inplace = True)
stock_copy['Volume'] = stock_copy['Volume'].astype('int64')

stock_copy.info() 

b = stock_copy[(stock_copy.Volume == 0)]
 
c = [i for i,row in b.iterrows() if not(stock_copy.Open[i] == \
                        stock_copy.High[i]== stock_copy.Low[i]\
                        ==stock_copy.Close[i])]
print(c)

for i in c:
    print(stock_copy.loc[i])

'''
=====================================================================
Only 6 records are incorrect.On printing the wrong records it is 
noted that in all of them only the "Open" column has a different 
value. High, Low and Close have same value. Assuming Open has been 
wrongly updated, it is replaced with the same value as High, Low 
and Close. Make sure that the problem is solved by this manipulation
======================================================================
''' 
for i in c:
    if (stock_copy.High[i] == stock_copy.Low[i] == stock_copy.Close[i]):
        stock_copy.Open[i] = stock_copy.High[i]

#Checking again:
c = [i for i,row in b.iterrows() if not(stock_copy.Open[i] == \
                        stock_copy.High[i]== stock_copy.Low[i]\
                        ==stock_copy.Close[i])]
print(c)
# c is empty Hence confirmed that Open = High =Low=Close when Volume =0

# Check the data frame for null values
stock_copy.isnull().sum()
       
'''
=====================================================================
So far done:
1. Data read, copied, merged.
2. Date is confirmed to be correct format and between 2006 and 2016
3. Checked for duplicate data based on date value. None exist. 
4. Checked for and corrected all non numeric values in 'Volume', 
   and 'Volume' converted to int.
5. Confirmed data types in all columns are correct.
6. Ensured that columns 1 to 4 have same value when 'Volume'= 0
7. Observed that columns 0 & 5 have no missing values

Next:
1. Check that columns 1 to 4 have no outlier values.
2. Volume has outliers, it is retained because it makes business 
   sense to have very high trade volumes on certain days
3. Check correlation between the numeric values in data
4. Drop rows with more than one missing values. 
5. Check that 'High' has the highest and 'Low' has the lowest value 
   in a day.Then fill missing values as follows: 

i.  Open - fill with the average of 2,3 & 4 columns    
ii. High - fill with the highest value for the day amongst 1,3,& 4 cols
iii.Low - fill with the lowest value for the day amongst 1,2, & 4 cols
iv. Close- fill with the average of 1,2 & 3 columns

This logic is based on the fact that these values vary on a daily
basis. A mean or median taken over a period of ten years will not
make sense. This logic is re-inforced by making a correlation matrix
which shows very strong correlation between 'Open','High','Low' and 
'Close' 

It has been decided to fill the missing values instead of dropping 
the records with missing values because in a data set of just 369
records, losing even a few records is a huge loss of information 
=======================================================================
'''
sns.boxplot(y = stock_copy.High)
sns.boxplot(y = stock_copy.Low)
sns.boxplot(y = stock_copy.Open)
sns.boxplot(y = stock_copy.Close)
#Box Plot shows no outliers in Open, High, Low, Close

sns.boxplot(y = stock_copy.Volume)
plt.show()

# Shows many outliers in 'Volume' column

numeric_data = stock_copy.select_dtypes(exclude=['object'])
corr_matrix = numeric_data.corr()
print(corr_matrix)
# Correlation matrix shows strong correlation between 'Open',
#'High','Low' and 'Close' variables

'''
===================================================================
Drop rows with more than one missing value, else fill values.
===================================================================
'''

for i in range(len(stock_copy)):
    if(stock_copy.High[i]<max(stock_copy.Open[i],stock_copy.Close[i],
                              stock_copy.Low[i])):
        stock_copy.High[i]=max(stock_copy.Open[i],
                               stock_copy.Close[i],stock_copy.Low[i])
        
    if(stock_copy.Low[i]>min(stock_copy.Open[i],stock_copy.Close[i])):
        stock_copy.Low[i]=min(stock_copy.Open[i],stock_copy.Close[i])

#Checking number of missing values in a row
    na_count = stock_copy.iloc[i].isnull().sum()
    if na_count > 1:
        stock_copy.drop(stock_copy.index[i], inplace = True)
        
    elif na_count==1:
        if np.isnan(stock_copy.High[i]):
            stock_copy.High[i]=max(stock_copy.Open[i],
                            stock_copy.Close[i],stock_copy.Low[i])
          
        elif np.isnan(stock_copy.Low[i]):
            stock_copy.Low[i]=min(stock_copy.Open[i],stock_copy.Close[i])
    
        elif np.isnan(stock_copy.Open[i]):
             stock_copy.Open[i]=round(np.mean([stock_copy.High[i],
                                stock_copy.Close[i],stock_copy.Low[i]]),2)
             
        elif np.isnan(stock_copy.Close[i]):
             stock_copy.Close[i]=round(np.mean([stock_copy.High[i],
                                stock_copy.Open[i],stock_copy.Low[i]]),2)

print(stock_copy.info())
print(stock_copy.isnull().sum())
    
'''
==========================================================================
End of Script File
==========================================================================
'''


    









