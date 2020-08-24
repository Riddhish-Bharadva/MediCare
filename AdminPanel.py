import webapp2
import jinja2
import os
import json
import urllib
import hashlib
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from urllib import urlencode
from datetime import datetime
from EmailModule import SendEmail
from AdminDB import AdminDB
from PharmacyDB import PharmacyDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class AdminPanel(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        notification = ""
        notification = self.request.get('notification')
        AdminLoggedIn = users.get_current_user()
        if AdminLoggedIn:
            SigninLink = users.create_logout_url(self.request.uri)
            SigninStatus = "Sign Out"
            adminDB_Reference = ndb.Key('AdminDB',AdminLoggedIn.email()).get() # Here I am checking if current user already have record in my DB or not.
            if adminDB_Reference == None: # If user record does not exist in DB, variable will be None.
                adminDB_Reference = AdminDB(id=AdminLoggedIn.email())
                adminDB_Reference.AdminEmail = AdminLoggedIn.email()
                adminDB_Reference.AdminPassword = ""
                adminDB_Reference.put()
                AdminEmail = AdminLoggedIn.email()
            else:
                AdminLoggedIn = adminDB_Reference
        else:
            SigninLink = users.create_login_url(self.request.uri)
            SigninStatus = "Sign In"

        template_values = {
            'notification' : notification,
            'AdminLoggedIn' : AdminLoggedIn,
            'SigninLink' : SigninLink,
            'SigninStatus' : SigninStatus,
        }

        template = JINJA_ENVIRONMENT.get_template('AdminPanel.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        WebPageLink = "https://medicare-287205.nw.r.appspot.com/"
        Button = self.request.get('Button')
        AdminLoggedIn = users.get_current_user()
        AdminEmail = AdminLoggedIn.email()

        if(Button == "RegisterVendorButton"):
            DateTime = datetime.now()
            PharmacyID = DateTime.strftime("%Y%m%d%H%M%S")
            self.response.write(PharmacyID)
            PharmacyName = self.request.get('PharmacyName')
            OfficialEmailId = self.request.get('OfficialEmailId')
            OfficialContact = self.request.get('OfficialContact')
            PhysicalAddress = self.request.get('PhysicalAddress')
            API_Key = "AIzaSyDvLc7SvzpX6KP6HCfn033xNKaM8UH3e2w"
            params = {"address":PhysicalAddress,"key":API_Key}
            GoogleAPI = "https://maps.googleapis.com/maps/api/geocode/json"
            url_params = urlencode(params)
            url = GoogleAPI+"?"+url_params
            result = urlfetch.fetch(url=url,method=urlfetch.POST,headers=params)
            Latitude = json.loads(result.content)['results'][0]['geometry']['location']['lat']
            Longitude = json.loads(result.content)['results'][0]['geometry']['location']['lng']
            EmailVerified = 0
            PharmacyDB_Reference = PharmacyDB.query(PharmacyDB.PharmacyName == PharmacyName and PharmacyDB.PhysicalAddress == PhysicalAddress).get()
            if(PharmacyDB_Reference == None):
                PharmacyDB_Reference = PharmacyDB(id=PharmacyID)
                PharmacyDB_Reference.PharmacyID = PharmacyID
                PharmacyDB_Reference.PharmacyName = PharmacyName
                PharmacyDB_Reference.OfficialEmailId = OfficialEmailId
                PharmacyDB_Reference.OfficialContact = OfficialContact
                PharmacyDB_Reference.PhysicalAddress = PhysicalAddress
                PharmacyDB_Reference.Latitude = Latitude
                PharmacyDB_Reference.Longitude = Longitude
                PharmacyDB_Reference.EmailVerified = EmailVerified
                PharmacyDB_Reference.RegisteredBy = AdminEmail
                PharmacyDB_Reference.IsActive = 1
                PharmacyDB_Reference.put()
                SendEmail(OfficialEmailId,"Confirmation email for vendor registered as : "+PharmacyName+" at MediCare","""
Dear Vendor,

This is an automated email sent to you regarding your MediCare account registration.

You have been registered as : """+PharmacyName+"""
Your Pharmacy Id is """+PharmacyID+"""

Please click on below link to confirm your email id:
"""+WebPageLink+"""/VerifyEmail?RegisteredAs=Vendor&PharmacyID="""+PharmacyID+"""&VerifyStatus="""+hashlib.md5(PhysicalAddress.encode()).hexdigest()+"""

In case above link doesn't work, copy and paste the same in url bar of your browser.

Please Note:
1) You will not be able to register any employee unless your email id has been confirmed using above link.
2) Your pharmacy will not be listed to customers to place order unless this email id is confirmed.

Thanks & regards,
MediCare Team.
            """)
                self.redirect('/AdminPanel?notification=VendorRegistrationSuccessful')
            else:
                self.redirect('/AdminPanel?notification=VendorAlreadyRegistererd')

app = webapp2.WSGIApplication([
    ('/AdminPanel',AdminPanel),
], debug=True)
