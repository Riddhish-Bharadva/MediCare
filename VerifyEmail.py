import webapp2
import jinja2
import os
import hashlib
from google.appengine.ext import ndb
from UsersDB import UsersDB
from PharmacyDB import PharmacyDB
from VendorsDB import VendorsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class VerifyEmail(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        VerifyStatus = self.request.get('VerifyStatus')
        RegisteredAs = self.request.get('RegisteredAs')
        DBConnect = None

        if(RegisteredAs == "User"):
            Email = self.request.get('userEmail')
            DBConnect = ndb.Key('UsersDB',Email).get()
            if(DBConnect != None and VerifyStatus == hashlib.md5(DBConnect.user_Password.encode()).hexdigest() and DBConnect.EmailVerified == 0):
                DBConnect.EmailVerified = 1
                DBConnect.put()
                Message = "Your email id has been verified."
            else:
                Message = "There is some error in verification link. It is either expired or invalid."

        elif(RegisteredAs == "Vendor"):
            PharmacyID = self.request.get('PharmacyID')
            DBConnect = ndb.Key('PharmacyDB',PharmacyID).get()
            if(DBConnect != None and VerifyStatus == hashlib.md5(DBConnect.PhysicalAddress.encode()).hexdigest() and DBConnect.EmailVerified == 0):
                DBConnect.EmailVerified = 1
                DBConnect.put()
                Message = "Your email id has been verified."
            else:
                Message = "There is some error in verification link. It is either expired or invalid."

        elif(RegisteredAs == "Staff" or RegisteredAs == "Pharmacist"):
            Email = self.request.get('vendorEmail')
            DBConnect = ndb.Key('VendorsDB',Email).get()
            if(DBConnect != None and VerifyStatus == hashlib.md5(DBConnect.Password.encode()).hexdigest() and DBConnect.EmailVerified == 0):
                DBConnect.EmailVerified = 1
                DBConnect.put()
                Message = "Your email id has been verified."
            else:
                Message = "There is some error in verification link. It is either expired or invalid."

        template_values = {
            'Message' : Message,
            'RegisteredAs' : RegisteredAs,
        }

        template = JINJA_ENVIRONMENT.get_template('VerifyEmail.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/VerifyEmail',VerifyEmail),
], debug=True)
