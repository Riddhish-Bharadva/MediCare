import webapp2
import jinja2
import os
import hashlib
from google.appengine.ext import ndb
from google.appengine.api import users
from EmailModule import SendEmail
from PharmacyDB import PharmacyDB
from VendorsDB import VendorsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class VendorSignIn(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        notification = ""
        notification = self.request.get('notification')

        template_values = {
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('VendorSignIn.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        WebPageLink = "https://medicare-287205.nw.r.appspot.com/"
        ButtonName = self.request.get('Button')
        if(ButtonName == "SignInButton"):
            vendorEmail = self.request.get('vendorEmail')
            vendorPassword = self.request.get('vendorPassword')
            DBConnect = ndb.Key('VendorsDB',vendorEmail).get()
            if(DBConnect != None):
                if(DBConnect.Password == vendorPassword and DBConnect.IsActive == 1):
                    self.redirect('/VendorHomePage?vendorEmail='+vendorEmail)
                elif(DBConnect.Password != vendorPassword and DBConnect.IsActive == 1):
                    self.redirect('/VendorSignIn?notification=PasswordMissmatch')
                elif(DBConnect.Password == vendorPassword and DBConnect.IsActive == 0):
                    self.redirect('/VendorSignIn?notification=VendorInActive')
            else:
                self.redirect('/VendorSignIn?notification=EmailIdNotRegistered')

        elif(ButtonName == "SignUpButton"):
            PharmacyID = self.request.get('PharmacyID')
            FirstName = self.request.get('FirstName')
            LastName = self.request.get('LastName')
            Email = self.request.get('vendorEmail_SU')
            Password = self.request.get('vendorPassword_SU')
            Contact = self.request.get('Contact')
            Address = self.request.get('Address')
            Gender = self.request.get('Gender')
            DOB = self.request.get('DOB')
            RegisteredAs = self.request.get('RegisteredAs')
            DBConnect_Pharmacy = ndb.Key('PharmacyDB',PharmacyID).get()
            if(DBConnect_Pharmacy != None):
                if(DBConnect_Pharmacy.IsActive == 1):
                    if(DBConnect_Pharmacy.EmailVerified == 1):
                        DBConnect = ndb.Key('VendorsDB',Email).get()
                        if(DBConnect == None):
                            DBConnect = VendorsDB(id=Email)
                            DBConnect.PharmacyID = PharmacyID
                            DBConnect.FirstName = FirstName
                            DBConnect.LastName = LastName
                            DBConnect.Email = Email
                            DBConnect.Password = Password
                            DBConnect.Contact = Contact
                            DBConnect.Address = Address
                            DBConnect.Gender = Gender
                            DBConnect.DOB = DOB
                            DBConnect.RegisteredAs = RegisteredAs
                            DBConnect.EmailVerified = 0
                            DBConnect.ResetPasswordLinkSent = 0
                            DBConnect.IsActive = 1
                            DBConnect.put()
                            SendEmail(Email,"Congratulations! Your MediCare's vendor account has been setup","""
Dear """+DBConnect.FirstName+""",

This is an automated email confirmation sent to you in regards of your MediCare account.

Your MediCare account has been registered as : '"""+RegisteredAs+"""' for vendor : """+DBConnect_Pharmacy.PharmacyName+"""

Please click on below link to verify your Email Id:
"""+WebPageLink+"""VerifyEmail?RegisteredAs="""+RegisteredAs+"""&vendorEmail="""+Email+"""&VerifyStatus="""+hashlib.md5(Password.encode()).hexdigest()+"""

Thanks & regards,
MediCare Team.
                        """)
                            self.redirect('/VendorSignIn?notification=VendorSuccessfullyRegistered')
                        else:
                            self.redirect('/VendorSignIn?notification=EmailAlreadyRegistered')
                    else:
                        self.redirect('/VendorSignIn?notification=EmailIdNotVerified')
                else:
                    self.redirect('/VendorSignIn?notification=VendorNotActive')
            else:
                self.redirect('/VendorSignIn?notification=InvalidPharmacyID')

        elif(ButtonName == "ForgotPasswordButton"):
            Email = self.request.get('vendorEmail_FP')
            DBConnect = ndb.Key('VendorsDB',Email).get()
            if(DBConnect != None):
                SendEmail(Email,"Reset password for your MediCare's vendor account","""
Dear """+DBConnect.FirstName+""",

This is an automated email sent to reset password of your MediCare account.

Click on below link to reset your password:

"""+WebPageLink+"""ResetPassword?RegisteredAs="""+DBConnect.RegisteredAs+"""&vendorEmail="""+Email+"""&FromPage=/VendorSignIn&ResetStatus="""+hashlib.md5(DBConnect.Password.encode()).hexdigest()+"""

In case above link doesn't work, copy and paste the same in url bar of your browser.

Thanks & regards,
MediCare Team.
                """)
                DBConnect.ResetPasswordLinkSent = 1
                DBConnect.put()
                self.redirect('/VendorSignIn?notification=PasswordResetLinkSent')
            else:
                self.redirect('/VendorSignIn?notification=EmailIdNotRegistered')

app = webapp2.WSGIApplication([
    ('/VendorSignIn',VendorSignIn),
], debug=True)
