import webapp2
import jinja2
import os
import hashlib
from google.appengine.ext import ndb
from UsersDB import UsersDB
from EmailModule import SendEmail
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
            DBConnect = ""
            if(SignInAs == "Member"):
                DBConnect = ndb.Key('UsersDB',userEmail).get()
            else:
                DBConnect = ndb.Key('Users_Pharmacist',userEmail).get()
            if(DBConnect != None):
                if(DBConnect.user_Password == userPassword):
                    if(SignInAs == "Member"):
                        self.redirect('/UsersHomePage')
                    elif(SignInAs == "Pharmacist"):
                        self.redirect('/PharmacistHomePage')
                else:
                    self.redirect('/?notification=PasswordMissmatch')
            else:
                self.redirect('/?notification=EmailIdNotRegistered')

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
                DBConnect = UsersDB(id=Email)
                DBConnect.user_FirstName = FirstName
                DBConnect.user_LastName = LastName
                DBConnect.user_Email = Email
                DBConnect.user_Password = Password
                DBConnect.user_Contact = Contact
                DBConnect.user_Address = Address
                DBConnect.user_Gender = Gender
                DBConnect.user_DOB = DOB
                DBConnect.put()
                SendEmail(Email,"Congratulations! Your MediCare account has been setup","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email confirmation sent to you in regards of your MediCare account.

Thank you for choosing MediCare. We hope you enjoy services provided by MediCare.com

Thanks & regards,
MediCare Team.
                """)
                self.redirect('/?notification=UserSuccessfullyRegistered')
            else:
                self.redirect('/?notification=EmailAlreadyRegistered')

        elif(ButtonName == "ForgotPasswordButton"):
            Email = self.request.get('userEmail_FP')
            RegisteredAs = self.request.get('RegisteredAs')
            DBConnect = ""
            if(RegisteredAs == "Member"):
                DBConnect = ndb.Key('UsersDB',Email).get()
            elif(RegisteredAs == "Pharmacist"):
                DBConnect = ndb.Key('Users_Pharmacist',Email).get()
            if(DBConnect != None):
                SendEmail(Email,"Reset password for your MediCare account","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email sent to reset password of your MediCare account.

Click on below link to reset your password:
http://localhost:8080/ResetPassword?userEmail="""+Email+"""&ResetStatus="""+hashlib.md5(DBConnect.user_Password.encode()).hexdigest()+"""&notification=""

In case above link doesn't work, copy and paste the same in url bar of your browser.

Thanks & regards,
MediCare Team.
                """)
                self.redirect('/?notification=PasswordResetLinkSent')
            else:
                self.redirect('/?notification=EmailIdNotRegistered')

        notification = self.request.get('notification')
        print(notification," is notification")

        template_values = {
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('mainPage.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/',mainPage),
    ('/ResetPassword',ResetPassword),
], debug=True)
