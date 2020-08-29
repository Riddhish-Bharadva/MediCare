import webapp2
import hashlib
import json
import urllib
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from urllib import urlencode
from EmailModule import SendEmail
from UsersDB import UsersDB
from ProductsDB import ProductsDB

class API_MediCare(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'

        WebPageLink = "https://medicare-287205.nw.r.appspot.com/"
        JD = json.loads(self.request.body)
        ResponseData = {}
        FunctionOption = JD["function"]
        userEmail = JD["userEmail"]
        if(userEmail != "" and userEmail != None):
            DBConnect = ndb.Key('UsersDB',userEmail).get()

# Below is code for SignUp.
        if(FunctionOption == "SignUp" and DBConnect == None):
            API_Key = "AIzaSyDvLc7SvzpX6KP6HCfn033xNKaM8UH3e2w"
            params = {"address":JD["Address"],"key":API_Key}
            GoogleAPI = "https://maps.googleapis.com/maps/api/geocode/json"
            url_params = urlencode(params)
            url = GoogleAPI+"?"+url_params
            result = urlfetch.fetch(url=url,method=urlfetch.POST,headers=params)
            Latitude = json.loads(result.content)['results'][0]['geometry']['location']['lat']
            Longitude = json.loads(result.content)['results'][0]['geometry']['location']['lng']
            DBConnect = UsersDB(id=userEmail)
            DBConnect.user_FirstName = JD["FirstName"]
            DBConnect.user_LastName = JD["LastName"]
            DBConnect.user_Email = userEmail
            DBConnect.user_Password = JD["Password"]
            DBConnect.user_Contact = JD["Contact"]
            DBConnect.user_Address = JD["Address"]
            DBConnect.Latitude = Latitude
            DBConnect.Longitude = Longitude
            DBConnect.user_Gender = JD["Gender"]
            DBConnect.user_DOB = JD["DOB"]
            DBConnect.EmailVerified = 0
            DBConnect.ResetPasswordLinkSent = 0
            DBConnect.IsActive = 1
            DBConnect.put()
            SendEmail(userEmail,"Congratulations! Your MediCare account has been setup","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email confirmation sent to you in regards of your MediCare account.

Please click on below link to verify your Email Id:
"""+WebPageLink+"""VerifyEmail?RegisteredAs=User&userEmail="""+userEmail+"""&VerifyStatus="""+hashlib.md5(DBConnect.user_Password.encode()).hexdigest()+"""

Thanks & regards,
MediCare Team.
            """)
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserSuccessfullyRegistered"
            self.response.write(json.dumps(ResponseData))
        elif(FunctionOption == "SignUp" and DBConnect != None):
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserAlreadyRegistered"
            self.response.write(json.dumps(ResponseData))

# Below is code for SignIn.
        elif(FunctionOption == "SignIn" and DBConnect != None):
            userPassword = JD["Password"]
            if(DBConnect.IsActive == 1):
                if(DBConnect.user_Password == userPassword):
                    ResponseData['userEmail'] = userEmail
                    ResponseData['notification'] = "SuccessfulSignIn"
                    ResponseData['FirstName'] = DBConnect.user_FirstName
                    ResponseData['LastName'] = DBConnect.user_LastName
                    ResponseData['Contact'] = DBConnect.user_Contact
                    ResponseData['Address'] = DBConnect.user_Address
                    ResponseData['Gender'] = DBConnect.user_Gender
                    ResponseData['DOB'] = DBConnect.user_DOB
                    ResponseData['EmailVerified'] = DBConnect.EmailVerified
                    self.response.write(json.dumps(ResponseData))
                else:
                    ResponseData['userEmail'] = userEmail
                    ResponseData['notification'] = "PasswordMissmatch"
                    self.response.write(json.dumps(ResponseData))
            else:
                ResponseData['userEmail'] = userEmail
                ResponseData['notification'] = "UserInActive"
                self.response.write(json.dumps(ResponseData))
        elif(FunctionOption == "SignIn" and DBConnect == None):
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserNotRegistered"
            self.response.write(json.dumps(ResponseData))

# Below is code for Forgot Password.
        elif(FunctionOption == "ForgotPassword" and DBConnect != None):
            DBConnect.ResetPasswordLinkSent = 1
            DBConnect.put()
            SendEmail(userEmail,"Reset password for your MediCare account","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email sent to reset password of your MediCare account.

Click on below link to reset your password:

"""+WebPageLink+"""ResetPassword?RegisteredAs=User&userEmail="""+userEmail+"""&FromPage=/UserSignIn&ResetStatus="""+hashlib.md5(DBConnect.user_Password.encode()).hexdigest()+"""

In case above link doesn't work, copy and paste the same in url bar of your browser.

Thanks & regards,
MediCare Team.
            """)
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "ResetLinkSent"
            self.response.write(json.dumps(ResponseData))
        elif(FunctionOption == "ForgotPassword" and DBConnect == None):
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserNotRegistered"
            self.response.write(json.dumps(ResponseData))

# Below is code for DeletingUserProfile.
        elif(FunctionOption == "DeleteUser" and DBConnect != None):
            DBConnect.key.delete()
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserSuccessfullyDeleted"
            self.response.write(json.dumps(ResponseData))
        elif(FunctionOption == "DeleteUser" and DBConnect == None):
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserNotRegistered"
            self.response.write(json.dumps(ResponseData))

# Below is code for HomePageAllProductsID.
        elif(FunctionOption == "AllProductID"):
            ProductsData = ProductsDB.query().fetch()
            ResponseProductID = {}
            Product = []
            for i in range(0,len(ProductsData)):
                Product.append(ProductsData[i].ProductID)
            ResponseProductID['ProductID'] = Product
            self.response.write(json.dumps(ResponseProductID))

# Below is code for HomePageAllProductsData.
        elif(FunctionOption == "ProductData"):
            ResponseProduct = {}
            ProductID = JD["ProductID"]
            ProductData = ndb.Key("ProductsDB",ProductID).get()
            ResponseProduct['ProductID'] = ProductData.ProductID
            ResponseProduct['ProductName'] = ProductData.ProductName
            ResponseProduct['Image'] = ProductData.Images[0]
            ResponseProduct['Description'] = ProductData.Description
            ResponseProduct['Dosage'] = ProductData.Dosage
            ResponseProduct['Category'] = ProductData.Category
            ResponseProduct['Ingredients'] = ProductData.Ingredients
            ResponseProduct['Price'] = ProductData.Price
            ResponseProduct['ProductLife'] = ProductData.ProductLife
            ResponseProduct['Quantity'] = ProductData.Quantity
            Stock = []
            for j in range(0,len(ProductData.StockedIn)):
                Stock.append(ProductData.StockedIn[j])
            ResponseProduct['StockedIn'] = Stock
            self.response.write(json.dumps(ResponseProduct))

# In case no function satisfy conditions, below will be returned.
        else:
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "FunctionNotRecognized"
            self.response.write(json.dumps(ResponseData))

app = webapp2.WSGIApplication([
    ('/API_MediCare',API_MediCare),
], debug=True)
