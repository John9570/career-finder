from tempfile import NamedTemporaryFile
import shutil
import csv


""" 
TODO


"""


filename = 'careerdata.csv'
tempfile = 'accounting_bm_all.csv'

occupation_row_number = 300

all_csv_data = list()

with open(filename, 'rb') as csvFile:
     reader = csv.reader(csvFile, delimiter=',', quotechar='"')

     for index, data_row in enumerate(reader):

         if index is 0: 
            all_csv_data.append(data_row)

         #only looking at the "all" data
         if "All" in data_row[2]:
            
            if "NULL" in data_row[occupation_row_number]: 
	       data_row[occupation_row_number] = 0	   
         
            #print(data_row[2])
	    all_csv_data.append(data_row)


with open(tempfile, 'w') as tempfile:
     writer = csv.writer(tempfile, delimiter=',', quotechar='"')
     
     for row in all_csv_data:
	 writer.writerow(row)

     numberList = list()

     for index, item in enumerate(all_csv_data):

	 if index != 0:    
	    numberList.append(int(item[occupation_row_number]))
         else:
            numberList.append(0) # need to do this so we have two equivalent sized lists
         
         #sortedList = sorted(numberList)


     """
     The below function outputs the indices of the top 5 numbers in the list.

     For future reference here is how it works
  
     Sorted has a key propoerty which takes a function and runs it on each value in its sort. The returned function value is then used as 
     a key during the sort (items are sorted based on their keys). 

     So, lets pretend we has numberList = [5, 3, 1, 4, 10]
     The range(len(numberList) piece returns [0, 1, 2, 3, 4] Which is what the sort function will be called on

     so first it takes the first value 0 and uses the key function, the key function returns numberList[0] which is 5, so 5 is the key in the sort value
     In other words, 0 represents the end result, but it is represented by 5 in the sort. And so on for the other numbers. 
 
     """
     topFive = sorted(range(len(numberList)), key=lambda x: numberList[x])[-5:]
     #print(topFive)

     #print(numberList)
     #print(sum(numberList))

     summation = sum(numberList)
     print(summation)


     if summation != 0:


        print("=====================================================")
        print("Occupation: " + all_csv_data[0][occupation_row_number])
        print("The most likely career choices | Percent likelihood")
   
        for x in range(4, -1, -1): 
            #print(numberList[topFive[x]])

            percentage = numberList[topFive[x]] / float(summation)
	    percentage = percentage * 100

            if percentage == 0:
	       break

            print(all_csv_data[topFive[x]][1] + " || " + str(percentage))
            
 
        print("=====================================================")


     else:
        print("=====================================================")
        print("Occupation: " + all_csv_data[0][occupation_row_number])
        print("No data on this occupation")
        print("=====================================================")





