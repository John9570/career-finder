import webapp2

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers

#https://docs.python.org/2/library/pickle.html
import pickle

import logging
import jinja2
import os
import csv

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#database model for storing user & profile information 
class Profiles(ndb.Model): 
    owner = ndb.StringProperty() #the key (email) of the person who owns it
    name = ndb.StringProperty()
    user_since = ndb.DateTimeProperty(auto_now_add=True)



class MajorData(ndb.Model): 
    owner = ndb.StringProperty() #the key (email) of the person who owns it
    name_clean = ndb.StringProperty() 
    name_raw = ndb.StringProperty() 
    sample_name = ndb.StringProperty() #all, millenials, male, female, etc.
    csv_data_refined = ndb.PickleProperty() # This is of the format list[ occupation ] [ amount ]  
    



class CareerData(ndb.Model):
    blobkey = ndb.BlobKeyProperty()


class BlobIterator:
    """Because the python csv module doesn't like strange newline chars and
        the google blob reader cannot be told to open in universal mode, then
        we need to read blocks of the blob and 'fix' the newlines as we go.
        Fixed the problem with the corrupted lines when fetching new data into the buffer."""
    
    def __init__(self, blob_reader):
        self.blob_reader = blob_reader
        self.last_line = ""
        self.line_num = 0
        self.lines = []
        self.buffer = None
    
    def __iter__(self):
        return self
    
    def next(self):
        if not self.buffer or len(self.lines) == self.line_num + 1:
            if self.lines:
                self.last_line = self.lines[self.line_num]
            self.buffer = self.blob_reader.read(1048576) # 1MB buffer
            self.lines = self.buffer.splitlines()
            self.line_num = 0
            
            # Handle special case where our block just happens to end on a new line
            if self.buffer[-1:] == "\n" or self.buffer[-1:] == "\r":
                self.lines.append("")
    
        if not self.buffer:
            raise StopIteration

        if self.line_num == 0 and len(self.last_line) > 0:
           result = self.last_line + self.lines[self.line_num] + "\n"
        else:
            result = self.lines[self.line_num] + "\n"

        self.line_num += 1
        return result




#this is for organizations
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):


	"""
	TODO

	Delete old entries of MajorData
        """

	user = users.get_current_user()

        upload = self.get_uploads()[0]
        #delete all the old links
        career_data_list = CareerData.query().fetch()

        for data in career_data_list:
            data.key.delete()
           
	upload_new_file = CareerData(blobkey=upload.key())
	upload_new_file.put()


        fileReader = blobstore.BlobReader(upload.key())



        self.redirect("/admin")





class HomePage(webapp2.RequestHandler):
    def get(self):

        template_values = {
        }

        template = jinja_environment.get_template('front.html')
        self.response.write(template.render(template_values))


class Dashboard(webapp2.RequestHandler):
    def get(self):
    
	user = users.get_current_user()
        
	if user:
	   parent = ndb.Key('Profiles', users.get_current_user().email())
           person = parent.get()


           #creating a new user
           if person == None:
              person = Profiles(id=users.get_current_user().email())
              person.owner = users.get_current_user().email()
              person.put()


           template_values = {
              'user_email': users.get_current_user().email(),
	      'name': person.name,
              'logout': users.create_logout_url(self.request.host_url)
           }

           template = jinja_environment.get_template('dashboard.html')
           self.response.write(template.render(template_values))

        else:
           self.redirect(users.create_login_url(self.request.uri))



class View_Data(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key): 
	if not blobstore.get(blob_key):
           self.error(404)
        else:
           self.send_blob(blob_key)



class CareerFileDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):

        #we expect to only ever get one
        career_download = CareerData.query().fetch()
        csv_key = career_download[0].blobkey
	self.send_blob(csv_key)


class Search(webapp2.RequestHandler):
    def get(self):
    
	user = users.get_current_user()
        
	if user:
	   parent = ndb.Key('Profiles', users.get_current_user().email())
           person = parent.get()

           career_download = CareerData.query().fetch()
           csv_key = career_download[0].blobkey
	
           blob_reader = blobstore.BlobReader(csv_key)
           blob_iterator = BlobIterator(blob_reader)           
           fileReader = csv.reader(blob_iterator, delimiter=',', quotechar='"')

           #bulk parsing of data 

           majors_object_list = list()

           for index, data_row in enumerate(fileReader):
	       
	       if index == 0:
	          for col_index, data_column in enumerate(data_row):
		      if col_index > 2:
                         majors_object_list.append(data_column) 

                  break

 
           template_values = {
              'user_email': users.get_current_user().email(),
	      'name': person.name,
	      'major_names': majors_object_list,
              'logout': users.create_logout_url(self.request.host_url)
           }

           template = jinja_environment.get_template('search.html')
           self.response.write(template.render(template_values))

        else:
           self.redirect(users.create_login_url(self.request.uri))
    
    def post(self):

        sample = self.request.get('sample')
        major = self.request.get('major')

        print(sample)
        print(major)

        self.redirect("/searchResult?sample={0}&major={1}".format(sample, major))




class SearchResultPage(webapp2.RequestHandler):
    def get(self):
    
	user = users.get_current_user()
        
	if user:
	   parent = ndb.Key('Profiles', users.get_current_user().email())
           person = parent.get()


           sample = self.request.get('sample')
	   major = self.request.get('major')
	   major = int(major) + 2 # we add 2 here b/c the select list int returned doesnt account for the occupation and sample fields 

           career_download = CareerData.query().fetch()
           csv_key = career_download[0].blobkey
	
           blob_reader = blobstore.BlobReader(csv_key)
           blob_iterator = BlobIterator(blob_reader)           
           fileReader = csv.reader(blob_iterator, delimiter=',', quotechar='"')

           occupation_row_number = major

           #bulk parsing of data 

           majors_object_list = list()
           all_csv_data = list()


           for index, data_row in enumerate(fileReader):
    
               if index is 0: 
                  all_csv_data.append(data_row)

               #only looking at the "all" data
               if sample in data_row[2]:
            
                  if "NULL" in data_row[occupation_row_number]: 
	             data_row[occupation_row_number] = 0	   
         
	          all_csv_data.append(data_row)

           #Nulls have been removed and data is formatted for the column we want.
           numberList = list()
           for index, item in enumerate(all_csv_data):

	       if index != 0:    
	          numberList.append(int(item[occupation_row_number]))
               else:
                  numberList.append(0) # need to do this so we have two equivalent sized lists
 

           topFive = sorted(range(len(numberList)), key=lambda x: numberList[x])[-5:]

           summation = sum(numberList)
           #print(summation)

           results = list()

           if summation != 0:


              print("=====================================================")
              print("Occupation: " + all_csv_data[0][occupation_row_number])
              print("The most likely career choices | Percent likelihood")
   

              for x in range(4, -1, -1): 
                  #print(numberList[topFive[x]])

                  percentage = numberList[topFive[x]] / float(summation)
	          percentage = percentage * 100

                  percentage = round(percentage, 2)


                  if percentage == 0:
	             results.append("")
	             continue
                     

                  print(all_csv_data[topFive[x]][1] + " || " + str(percentage))
		  result_str = str(all_csv_data[topFive[x]][1]) + " & percent certainty is " + str(percentage) + "%"
                  results.append(result_str)
 
              print("=====================================================")

           else:
              print("=====================================================")
              print("Occupation: " + all_csv_data[0][occupation_row_number])
              print("No data on this occupation")
              print("=====================================================")
              results = ['','','','','']



           major = all_csv_data[0][occupation_row_number]
	   major = major.split("\\")[0]

           template_values = {
              'user_email': users.get_current_user().email(),
	      'name': person.name,
	      'sample': sample,
	      'summation': summation,
	      'major': major,
	      'result1': results[0],
	      'result2': results[1],
	      'result3': results[2],
	      'result4': results[3],
	      'result5': results[4],
              'logout': users.create_logout_url(self.request.host_url)
           }

           template = jinja_environment.get_template('searchResult.html')
           self.response.write(template.render(template_values))

        else:
           self.redirect(users.create_login_url(self.request.uri))
    

class adminPage(webapp2.RequestHandler):
    def get(self):
    
	user = users.get_current_user()
        
 
	if user:
	   parent = ndb.Key('Profiles', users.get_current_user().email())
           person = parent.get()

           upload_url = blobstore.create_upload_url('/uploadhandler')

           template_values = {
              'user_email': users.get_current_user().email(),
	      'name': person.name,
	      'upload_url': upload_url,
              'logout': users.create_logout_url(self.request.host_url)
           }

           template = jinja_environment.get_template('administration.html')
           self.response.write(template.render(template_values))

        else:
           self.redirect(users.create_login_url(self.request.uri))
    




app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/dashboard', Dashboard),
    ('/viewdata', View_Data),
    ('/uploadhandler', UploadHandler),
    ('/downloadcareer', CareerFileDownloadHandler),
    ('/search', Search),
    ('/searchResult', SearchResultPage),
    ('/admin', adminPage)
], debug=False)
