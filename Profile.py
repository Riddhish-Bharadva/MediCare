import webapp2
import jinja2
import os
import json
import urllib
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from urllib import urlencode
from UsersDB import UsersDB
from ProductsDB import ProductsDB
from EmailModule import SendEmail

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class Profile(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        notification = self.request.get('notification')
        userEmail = self.request.get('userEmail')
        Mode = self.request.get('Mode')
        UserDetails = None
        Category = []

        if(userEmail != ""):
            UserDetails = ndb.Key('UsersDB',userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            SignInStatus = "SignOut"
        else:
            self.redirect('/UserSignIn')

        ProductsData = ProductsDB.query().fetch()
        if(ProductsData == []):
            ProductsData = None
        else:
            for i in range(0,len(ProductsData)):
                if(ProductsData[i].Category not in Category):
                    Category.append(ProductsData[i].Category)
        Category.sort()

        template_values = {
            'SignInStatus' : SignInStatus,
            'UserDetails' : UserDetails,
            'Category' : Category,
            'Mode' : Mode,
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('Profile.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get('userEmail')
        Button = self.request.get('Button')
        if(Button == "EditButton"):
            self.redirect('/Profile?userEmail='+userEmail+'&Mode=Edit')
        elif(Button == "UpdateButton"):
            FirstName = self.request.get('FirstName')
            LastName = self.request.get('LastName')
            Email = self.request.get('userEmail')
            Contact = self.request.get('Contact')
            Address = self.request.get('Address')
            DBConnect = ndb.Key('UsersDB',Email).get()
            if(DBConnect != None):
                API_Key = "AIzaSyDvLc7SvzpX6KP6HCfn033xNKaM8UH3e2w"
                params = {"address":Address,"key":API_Key}
                GoogleAPI = "https://maps.googleapis.com/maps/api/geocode/json"
                url_params = urlencode(params)
                url = GoogleAPI+"?"+url_params
                result = urlfetch.fetch(url=url,method=urlfetch.POST,headers=params)
                Latitude = json.loads(result.content)['results'][0]['geometry']['location']['lat']
                Longitude = json.loads(result.content)['results'][0]['geometry']['location']['lng']
                DBConnect.user_FirstName = FirstName
                DBConnect.user_LastName = LastName
                DBConnect.user_Contact = Contact
                DBConnect.user_Address = Address
                DBConnect.Latitude = Latitude
                DBConnect.Longitude = Longitude
                DBConnect.put()
                SendEmail(Email,"Congratulations! Your MediCare account details are updated successfully","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email confirmation sent to you in regards of successful updation of your MediCare account.

Thanks & regards,
MediCare Team.
                """)
                self.redirect('/Profile?userEmail='+userEmail+'&notification=ProfileUpdatedSuccessfully')
            else:
                self.redirect('/Profile?userEmail='+userEmail+'&notification=ProfileUpdatationFailed')
        else:
            self.redirect('/Profile?userEmail='+userEmail)

app = webapp2.WSGIApplication([
    ('/Profile',Profile),
], debug=True)
