import webapp2
import jinja2
import os
import hashlib
from google.appengine.ext import ndb
from UsersDB import UsersDB
from EmailModule import SendEmail

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class ResetPassword(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        ButtonName = self.request.get('Button')
        notification = ""
        notification = self.request.get('notification')
        Email = self.request.get('userEmail')
        ResetStatus = self.request.get('ResetStatus')
        if(ButtonName == "ResetPasswordButton"):
            Password = self.request.get('userPassword_New')
            Password_Repeat = self.request.get('userPassword_New_Repeat')
            DBConnect = ""
            if(ndb.Key('UsersDB',Email).get() != None):
                DBConnect = ndb.Key('UsersDB',Email).get()
            elif(ndb.Key('Users_Pharmacist',Email).get() != None):
                DBConnect = ndb.Key('Users_Pharmacist',Email).get()
            if(ResetStatus == hashlib.md5(DBConnect.user_Password.encode()).hexdigest()):
                if(Password == Password_Repeat):
                    DBConnect.user_Password = Password
                    DBConnect.put()
                    SendEmail(Email,"Password of your MediCare account was recently changed","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email sent to you in regards of your MediCare account.

It is to inform you that the password of your MediCare account has been recently changed.

Thanks & regards,
MediCare Team.
                """)
                    self.redirect('/?notification=PasswordResetSuccessful')
                else:
                    self.redirect('/ResetPassword?userEmail='+Email+'&ResetStatus='+hashlib.md5(DBConnect.user_Password.encode()).hexdigest()+'&notification=PasswordMissmatch')
            else:
                self.redirect('/?notification=InvalidPasswordResetLink')

        template_values = {
            'user_Email' : Email,
            'ResetStatus' : ResetStatus,
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('ResetPassword.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/ResetPassword',ResetPassword),
], debug=True)
