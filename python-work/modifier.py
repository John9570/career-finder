from tempfile import NamedTemporaryFile
import shutil
import csv

filename = 'existing.csv'
tempfile = 'newfile.csv'

all_csv_data = list()

with open(filename, 'rb') as csvFile:
     reader = csv.reader(csvFile, delimiter=',', quotechar='"')

     for row in reader:
         row = row[:16]
	 org_list = row[15].split()
         org_list = list(set(org_list))
         for org in org_list:
             row.append(org)

         #print(row)
	 all_csv_data.append(row)


with open(tempfile, 'w') as tempfile:
     writer = csv.writer(tempfile, delimiter=',', quotechar='"')
     
     for row in all_csv_data:
	 writer.writerow(row)



