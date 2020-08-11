import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from API_MediCare import API_MediCare
from AdminDB import AdminDB
from UsersDB import UsersDB
from PharmacyDB import PharmacyDB
from VendorsDB import VendorsDB
from EmailModule import SendEmail
from AdminPanel import AdminPanel
from UserSignIn import UserSignIn
from VendorSignIn import VendorSignIn
from VerifyEmail import VerifyEmail
from ResetPassword import ResetPassword

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class mainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        notification = ""
        ButtonName = self.request.get('Button')

        if(ButtonName == "SignInButton"):
            userEmail = self.request.get('userEmail')
            userPassword = self.request.get('userPassword')
            SignInAs = self.request.get('SignInAs')
            SignIn(userEmail,userPassword,SignInAs,self)

        elif(ButtonName == "SignUpButton"):
            FirstName = self.request.get('FirstName')
            LastName = self.request.get('LastName')
            Email = self.request.get('userEmail_SU')
            Password = self.request.get('userPassword_SU')
            Contact = self.request.get('Contact')
            Address = self.request.get('Address')
            Gender = self.request.get('Gender')
            DOB = self.request.get('DOB')
            SignUp(FirstName,LastName,Email,Password,Contact,Address,Gender,DOB,self)

        elif(ButtonName == "ForgotPasswordButton"):
            Email = self.request.get('userEmail_FP')
            RegisteredAs = self.request.get('RegisteredAs')
            ForgotPassword(Email,RegisteredAs,self)

        notification = self.request.get('notification')

        template_values = {
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('mainPage.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/',mainPage),
    ('/ResetPassword',ResetPassword),
    ('/UserSignIn',UserSignIn),
    ('/VendorSignIn',VendorSignIn),
    ('/VerifyEmail',VerifyEmail),
    ('/AdminPanel',AdminPanel),
    ('/API_MediCare',API_MediCare),
], debug=True)
