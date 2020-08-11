import webapp2
import jinja2
import os
import hashlib
from google.appengine.ext import ndb
from UsersDB import UsersDB
from VendorsDB import VendorsDB
from EmailModule import SendEmail

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class ResetPassword(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        notification = ""
        notification = self.request.get('notification')
        RegisteredAs = self.request.get('RegisteredAs')

        EmailId = None
        if(RegisteredAs == "User"):
            EmailId = self.request.get('userEmail')
        elif(RegisteredAs == "Staff" or RegisteredAs == "Pharmacist"):
            EmailId = self.request.get('vendorEmail')
        ResetStatus = self.request.get('ResetStatus')
        FromPage = self.request.get('FromPage')

        template_values = {
            'RegisteredAs' : RegisteredAs,
            'ResetStatus' : ResetStatus,
            'EmailId' : EmailId,
            'FromPage' : FromPage,
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('ResetPassword.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        ButtonName = self.request.get('Button')
        RegisteredAs = self.request.get('RegisteredAs')
        ResetStatus = self.request.get('ResetStatus')
        FromPage = self.request.get('FromPage')

        if(ButtonName == "ResetPasswordButton"):
            Password = self.request.get('Password_New')
            Password_Repeat = self.request.get('Password_New_Repeat')
            if(RegisteredAs == "User"):
                Email = self.request.get('Email')
                DBConnect = ndb.Key('UsersDB',Email).get()
                if(DBConnect != None and ResetStatus == hashlib.md5(DBConnect.user_Password.encode()).hexdigest() and DBConnect.ResetPasswordLinkSent == 1):
                    if(Password == Password_Repeat):
                        DBConnect.user_Password = Password
                        DBConnect.ResetPasswordLinkSent = 0
                        DBConnect.put()
                        SendEmail(Email,"Password of your MediCare account was recently changed","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email sent to you in regards of your MediCare account.

It is to inform you that the password of your MediCare account has been recently changed.

Thanks & regards,
MediCare Team.
                        """)
                        self.redirect(FromPage+'?notification=PasswordResetSuccessful')
                    else:
                        self.redirect("/ResetPassword?RegisteredAs="+RegisteredAs+"&userEmail="+Email+"&FromPage="+FromPage+"&ResetStatus="+hashlib.md5(DBConnect.user_Password.encode()).hexdigest()+"&notification=PasswordMissmatch")
                else:
                    self.redirect(FromPage+'?notification=InvalidPasswordResetLink')

            elif(RegisteredAs == "Staff" or RegisteredAs == "Pharmacist"):
                Email = self.request.get('Email')
                DBConnect = ndb.Key('VendorsDB',Email).get()
                if(DBConnect != None and ResetStatus == hashlib.md5(DBConnect.Password.encode()).hexdigest() and DBConnect.ResetPasswordLinkSent == 1):
                    if(Password == Password_Repeat):
                        DBConnect.Password = Password
                        DBConnect.ResetPasswordLinkSent = 0
                        DBConnect.put()
                        SendEmail(Email,"Password of your MediCare's vendor account was recently changed","""
Dear """+DBConnect.FirstName+""",

This is an automated email sent to you in regards of your MediCare account.

It is to inform you that the password of your MediCare account has been recently changed.

Thanks & regards,
MediCare Team.
                        """)
                        self.redirect(FromPage+'?notification=PasswordResetSuccessful')
                    else:
                        self.redirect("/ResetPassword?RegisteredAs="+RegisteredAs+"&vendorEmail="+Email+"&FromPage="+FromPage+"&ResetStatus="+hashlib.md5(DBConnect.Password.encode()).hexdigest()+"&notification=PasswordMissmatch")
                else:
                    self.redirect(FromPage+'?notification=InvalidPasswordResetLink')

app = webapp2.WSGIApplication([
    ('/ResetPassword',ResetPassword),
], debug=True)
