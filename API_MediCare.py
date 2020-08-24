import webapp2
import json
import hashlib
from google.appengine.ext import ndb
from UsersDB import UsersDB
from EmailModule import SendEmail

class API_MediCare(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'

        WebPageLink = "https://medicare-287205.nw.r.appspot.com/"
        Json_Data = json.loads(self.request.body)
        Data = {}
        FunctionOption = Json_Data["function"]
        Email = Json_Data["userEmail"]
        DBConnect = ndb.Key('UsersDB',Email).get()
        if(FunctionOption == "ForgotPassword"):
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
                Data['Email'] = Email
                Data['notification'] = "ResetLinkSent"
                self.response.write(json.dumps(Data))
            else:
                Data['Email'] = Email
                Data['notification'] = "EmailIdNotRegistered"
                self.response.write(json.dumps(Data))
        else:
            Data['Email'] = Email
            Data['notification'] = "FunctionNotRecognized"
            self.response.write(json.dumps(Data))

app = webapp2.WSGIApplication([
    ('/API_MediCare',API_MediCare),
], debug=True)
