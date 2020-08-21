import webapp2
import jinja2
import os
import hashlib
from google.appengine.ext import ndb
from EmailModule import SendEmail
from VendorsDB import VendorsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class VendorHomePage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get("vendorEmail")
        VendorDetails = []
        EditMode = self.request.get("EditMode")
        notification = self.request.get("notification")
        if(vendorEmail != ""):
            VendorDetails = ndb.Key("VendorsDB",vendorEmail).get()
            if(VendorDetails == None):
                self.redirect('/VendorSignIn')
        else:
            self.redirect('/VendorSignIn')

        template_values = {
            'VendorDetails' : VendorDetails,
            'EditMode' : EditMode,
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('VendorHomePage.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        WebPageLink = "http://localhost:8080"

        Button = self.request.get("Button")
        vendorEmail = self.request.get("vendorEmail")
        if(vendorEmail != ""):
            VendorsDBConnect = ndb.Key("VendorsDB",vendorEmail).get()
            if(Button == "EditProfile"):
                EditMode = self.request.get('EditMode')
                if(EditMode == "On"):
                    self.redirect('/VendorHomePage?vendorEmail='+vendorEmail)
                else:
                    self.redirect('/VendorHomePage?vendorEmail='+vendorEmail+'&EditMode=On')
            elif(Button == "Update"):
                FirstName = self.request.get('FirstName_New')
                LastName = self.request.get('LastName_New')
                Contact = self.request.get('Contact_New')
                Address = self.request.get('Address_New')
                if(VendorsDBConnect != None):
                    VendorsDBConnect.FirstName = FirstName
                    VendorsDBConnect.LastName = LastName
                    VendorsDBConnect.Contact = Contact
                    VendorsDBConnect.Address = Address
                    VendorsDBConnect.put()
                    self.redirect('/VendorHomePage?vendorEmail='+vendorEmail+'&notification=ProfileUpdated')
                else:
                    self.redirect('/VendorHomePage?vendorEmail='+vendorEmail+'&notification=InvalidProfile')
            elif(Button == "ChangePassword"):
                if(VendorsDBConnect != None):
                    SendEmail(vendorEmail,"Reset password for your MediCare's vendor account","""
Dear """+VendorsDBConnect.FirstName+""",

This is an automated email sent to reset password of your MediCare account.

Click on below link to reset your password:

"""+WebPageLink+"""/ResetPassword?RegisteredAs="""+VendorsDBConnect.RegisteredAs+"""&vendorEmail="""+vendorEmail+"""&FromPage=/VendorSignIn&ResetStatus="""+hashlib.md5(VendorsDBConnect.Password.encode()).hexdigest()+"""

In case above link doesn't work, copy and paste the same in url bar of your browser.

Thanks & regards,
MediCare Team.
                    """)
                    VendorsDBConnect.ResetPasswordLinkSent = 1
                    VendorsDBConnect.put()
                    self.redirect('/VendorSignIn?notification=PasswordResetLinkSent')

            elif(Button == "DeleteProfile"):
                VendorsDBConnect.key.delete()
                self.redirect('/VendorSignIn?&notification=VendorProfileDeleted')
        else:
            self.redirect('/VendorSignIn')

app = webapp2.WSGIApplication([
    ('/VendorHomePage',VendorHomePage),
], debug=True)
