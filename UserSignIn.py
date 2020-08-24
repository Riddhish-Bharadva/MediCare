import webapp2
import jinja2
import os
import hashlib
import json
import urllib
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from urllib import urlencode
from EmailModule import SendEmail
from UsersDB import UsersDB
from ProductsDB import ProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class UserSignIn(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        notification = ""
        Category = []
        notification = self.request.get('notification')
        ProductsData = ProductsDB.query().fetch()
        if(ProductsData == []):
            ProductsData = None
        else:
            for i in range(0,len(ProductsData)):
                if(ProductsData[i].Category not in Category):
                    Category.append(ProductsData[i].Category)
        Category.sort()

        template_values = {
            'notification' : notification,
            'Category' : Category,
        }

        template = JINJA_ENVIRONMENT.get_template('UserSignIn.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        WebPageLink = "https://medicare-287205.nw.r.appspot.com/"
        ButtonName = self.request.get('Button')

        if(ButtonName == "SignInButton"):
            userEmail = self.request.get('userEmail')
            userPassword = self.request.get('userPassword')
            DBConnect = ndb.Key('UsersDB',userEmail).get()
            if(DBConnect != None and DBConnect.IsActive == 1):
                if(DBConnect.user_Password == userPassword):
                    self.redirect('/?userEmail='+userEmail)
                else:
                    self.redirect('/UserSignIn?notification=PasswordMissmatch')
            else:
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')

        elif(ButtonName == "SignUpButton"):
            FirstName = self.request.get('FirstName')
            LastName = self.request.get('LastName')
            Email = self.request.get('userEmail_SU')
            Password = self.request.get('userPassword_SU')
            Contact = self.request.get('Contact')
            Address = self.request.get('Address')
            Gender = self.request.get('Gender')
            DOB = self.request.get('DOB')
            DBConnect = ndb.Key('UsersDB',Email).get()
            if(DBConnect == None):
                API_Key = "AIzaSyDvLc7SvzpX6KP6HCfn033xNKaM8UH3e2w"
                params = {"address":Address,"key":API_Key}
                GoogleAPI = "https://maps.googleapis.com/maps/api/geocode/json"
                url_params = urlencode(params)
                url = GoogleAPI+"?"+url_params
                result = urlfetch.fetch(url=url,method=urlfetch.POST,headers=params)
                Latitude = json.loads(result.content)['results'][0]['geometry']['location']['lat']
                Longitude = json.loads(result.content)['results'][0]['geometry']['location']['lng']
                DBConnect = UsersDB(id=Email)
                DBConnect.user_FirstName = FirstName
                DBConnect.user_LastName = LastName
                DBConnect.user_Email = Email
                DBConnect.user_Password = Password
                DBConnect.user_Contact = Contact
                DBConnect.user_Address = Address
                DBConnect.Latitude = Latitude
                DBConnect.Longitude = Longitude
                DBConnect.user_Gender = Gender
                DBConnect.user_DOB = DOB
                DBConnect.EmailVerified = 0
                DBConnect.ResetPasswordLinkSent = 0
                DBConnect.IsActive = 1
                DBConnect.put()
                SendEmail(Email,"Congratulations! Your MediCare account has been setup","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email confirmation sent to you in regards of your MediCare account.

Please click on below link to verify your Email Id:
"""+WebPageLink+"""VerifyEmail?RegisteredAs=User&userEmail="""+Email+"""&VerifyStatus="""+hashlib.md5(DBConnect.user_Password.encode()).hexdigest()+"""

Thanks & regards,
MediCare Team.
                """)
                self.redirect('/UserSignIn?notification=UserSuccessfullyRegistered')
            else:
                self.redirect('/UserSignIn?notification=EmailAlreadyRegistered')

        elif(ButtonName == "ForgotPasswordButton"):
            Email = self.request.get('userEmail_FP')
            DBConnect = ndb.Key('UsersDB',Email).get()
            if(DBConnect != None):
                SendEmail(Email,"Reset password for your MediCare account","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email sent to reset password of your MediCare account.

Click on below link to reset your password:

"""+WebPageLink+"""ResetPassword?RegisteredAs=User&userEmail="""+Email+"""&FromPage=/UserSignIn&ResetStatus="""+hashlib.md5(DBConnect.user_Password.encode()).hexdigest()+"""

In case above link doesn't work, copy and paste the same in url bar of your browser.

Thanks & regards,
MediCare Team.
                """)
                DBConnect.ResetPasswordLinkSent = 1
                DBConnect.put()
                self.redirect('/UserSignIn?notification=PasswordResetLinkSent')
            else:
                self.redirect('/UserSignIn?notification=EmailIdNotRegistered')

app = webapp2.WSGIApplication([
    ('/UserSignIn',UserSignIn),
], debug=True)
