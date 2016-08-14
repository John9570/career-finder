from tempfile import NamedTemporaryFile
import shutil
import csv

import pandas as pd
import statsmodels.api as sm
import pylab as pl
import numpy as np
from math import exp


filename = 'org_four_admit.csv'

new_students_file = 'new.csv'

resultfile = 'result_four_first_hundred.csv'

# read the data in
df = pd.read_csv(filename) # nrows=500)
ns = pd.read_csv(new_students_file)


# take a look at the dataset
#print df.head()


#If you want to trim the results
#df.drop(df.index[:400], inplace=True)
ns.drop(ns.index[999:-1], inplace=True)

# rename the 'rank' column because there is also a DataFrame method called 'rank'
df.columns = ["admit", "id", "person_name", "ethics", "composure1", "socialbility", "cooperation", "motivation", "composure2", "flexibility", "practicality", "curiosity", "creativity", "coaching", "persuasiveness", "analytical", "organizations"]


ns.columns =  ["id", "person_name", "ethics", "composure1", "socialbility", "cooperation", "motivation", "composure2", "flexibility", "practicality", "curiosity", "creativity", "coaching", "persuasiveness", "analytical"]


#print df.columns

print df.describe()



#print df.std()

cols_to_keep = ["admit", "ethics", "composure1", "socialbility", "cooperation", "motivation", "composure2", "flexibility", "practicality", "curiosity", "creativity", "coaching", "persuasiveness", "analytical"]

data = df[cols_to_keep]
data['intercept'] = 1.0




print data.columns
print data.head()


print("Performing regression.... \n")


train_cols = data.columns[1:]
logit = sm.Logit(data['admit'], data[train_cols])

#fit the model
result = logit.fit()


print result.summary()




print("NEW STUDENT DESCRIPTION")
print ns.describe()


print("RESULT PARAMS")

intercept = result.params[-1]

parameters = result.params[:-1]


print parameters

print("intercept: {0}".format(intercept))
print("====================================== !! ====================================")



#ns.columns =  ["id", "person_name", "ethics", "composure1", "socialbility", "cooperation", "motivation", "composure2", "flexibility", "practicality", "curiosity", "creativity", "coaching", "persuasiveness", "analytical"]

all_csv_data = list()


for index, row in ns.iterrows():
     
    ethics_val = parameters[0] * row['ethics']
    comp1_val = parameters[1] * row['composure1']
    soc_val = parameters[2] * row['socialbility']
    coop_val = parameters[3] * row['cooperation']
    motivation_val = parameters[4] * row['motivation']
    comp2_val = parameters[5] * row['composure2']
    flex_val = parameters[6] * row['flexibility']
    prac_val = parameters[7] * row['practicality']
    curi_val = parameters[8] * row['curiosity']
    create_val = parameters[9] * row['creativity']
    coach_val = parameters[10] * row['coaching']
    persuasive_val = parameters[11] * row['persuasiveness']
    analytic_val = parameters[12] * row['analytical']
	
	
    final_val = ethics_val + comp1_val + soc_val + coop_val + motivation_val + comp2_val + flex_val + prac_val + curi_val + create_val + coach_val + persuasive_val + analytic_val + intercept

    probability = exp(final_val) / float(1 + exp(final_val)) 

    row_data = list()
    row_data.append([row['id'], row['person_name'], row['ethics'], row['composure1'], row['socialbility'], row['cooperation'], row['motivation'], row['composure2'], row['flexibility'], row['practicality'], row['curiosity'], row['creativity'], row['coaching'], row['persuasiveness'], row['analytical'], probability])
 
    all_csv_data.append(row_data[0])


with open(resultfile, 'w') as resultfile:
     writer = csv.writer(resultfile, delimiter=',', quotechar='"')
     
     for row in all_csv_data:
	 writer.writerow(row)





