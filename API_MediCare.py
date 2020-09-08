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
from PharmacyDB import PharmacyDB
from CartDB import CartDB
from OrdersDB import OrdersDB
from VendorProductsDB import VendorProductsDB

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
            ResponseProduct['PrescriptionRequired'] = ProductData.PrescriptionRequired
            Stock = []
            for j in range(0,len(ProductData.StockedIn)):
                Stock.append(ProductData.StockedIn[j])
            ResponseProduct['StockedIn'] = Stock
            self.response.write(json.dumps(ResponseProduct))

# Below is code to add products to cart.
        elif(FunctionOption == "AddToCart" and DBConnect != None):
            ProductID = JD["ProductID"]
            CartDBStatus = ndb.Key("CartDB",userEmail).get()
            if(CartDBStatus != None):
                if(ProductID not in CartDBStatus.ProductID):
                    CartDBStatus.ProductID.append(ProductID)
                    CartDBStatus.Quantity.append(0)
                    CartDBStatus.PharmacyID.append("None")
            else:
                CartDBStatus = CartDB(id=userEmail)
                CartDBStatus.userEmail = userEmail
                CartDBStatus.OrderType = "None"
                CartDBStatus.ProductID.append(ProductID)
                CartDBStatus.Quantity.append(0)
                CartDBStatus.PharmacyID.append("None")
            CartDBStatus.put()
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "ProductSuccessfullyAdded"
            self.response.write(json.dumps(ResponseData))

# Below is code to remove products from cart.
        elif(FunctionOption == "RemoveFromCart" and DBConnect != None):
            ProductID = JD["ProductID"]
            CartData = ndb.Key("CartDB",userEmail).get()
            if(CartData != None):
                if(len(CartData.ProductID)>1):
                    for i in range(0,len(CartData.ProductID)):
                        if(CartData.ProductID[i] == ProductID):
                            del CartData.ProductID[i]
                            del CartData.Quantity[i]
                            del CartData.PharmacyID[i]
                            CartData.put()
                            break
                else:
                    CartData.key.delete()
                ResponseData['notification'] = "ProductSuccessfullyRemoved"
            else:
                ResponseData['notification'] = "FailedToRemoveProduct"
            ResponseData['userEmail'] = userEmail
            self.response.write(json.dumps(ResponseData))

# Below is code for Fetching user profile data.
        elif(FunctionOption == "FetchProfileData" and DBConnect != None):
            ResponseData['userEmail'] = DBConnect.user_Email
            ResponseData['notification'] = "ProfileDataFound"
            ResponseData['FirstName'] = DBConnect.user_FirstName
            ResponseData['LastName'] = DBConnect.user_LastName
            ResponseData['Contact'] = DBConnect.user_Contact
            ResponseData['Address'] = DBConnect.user_Address
            ResponseData['Gender'] = DBConnect.user_Gender
            ResponseData['DOB'] = DBConnect.user_DOB
            ResponseData['EmailVerified'] = DBConnect.EmailVerified
            self.response.write(json.dumps(ResponseData))
        elif(FunctionOption == "FetchProfileData" and DBConnect == None):
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserNotRegistered"
            self.response.write(json.dumps(ResponseData))

# Below is code for updating user profile data.
        elif(FunctionOption == "UpdateProfileData" and DBConnect != None):
            API_Key = "AIzaSyDvLc7SvzpX6KP6HCfn033xNKaM8UH3e2w"
            params = {"address":JD["Address"],"key":API_Key}
            GoogleAPI = "https://maps.googleapis.com/maps/api/geocode/json"
            url_params = urlencode(params)
            url = GoogleAPI+"?"+url_params
            result = urlfetch.fetch(url=url,method=urlfetch.POST,headers=params)
            DBConnect.user_FirstName = JD["FirstName"]
            DBConnect.user_LastName = JD["LastName"]
            DBConnect.user_Contact = JD["Contact"]
            DBConnect.user_Address = JD["Address"]
            DBConnect.Latitude = json.loads(result.content)['results'][0]['geometry']['location']['lat']
            DBConnect.Longitude = json.loads(result.content)['results'][0]['geometry']['location']['lng']
            DBConnect.put()
            SendEmail(DBConnect.user_Email,"Congratulations! Your MediCare account details are updated successfully","""
Dear """+DBConnect.user_FirstName+""",

This is an automated email confirmation sent to you in regards of successful updation of your MediCare account.

Thanks & regards,
MediCare Team.
            """)
            ResponseData['userEmail'] = DBConnect.user_Email
            ResponseData['notification'] = "ProfileSuccessfullyUpdated"
            ResponseData['FirstName'] = DBConnect.user_FirstName
            ResponseData['LastName'] = DBConnect.user_LastName
            ResponseData['Contact'] = DBConnect.user_Contact
            ResponseData['Address'] = DBConnect.user_Address
            ResponseData['Gender'] = DBConnect.user_Gender
            ResponseData['DOB'] = DBConnect.user_DOB
            ResponseData['EmailVerified'] = DBConnect.EmailVerified
            self.response.write(json.dumps(ResponseData))
        elif(FunctionOption == "UpdateProfileData" and DBConnect == None):
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserNotRegistered"
            self.response.write(json.dumps(ResponseData))

# Below is code for searching product and returning product id if keyword matches.
        elif(FunctionOption == "SearchProduct"):
            ProductIDs = []
            SearchKeyword = JD["SearchKeyword"]
            if(SearchKeyword != ""):
                AllProducts = ProductsDB.query().fetch()
                if(AllProducts != None):
                    for i in range(0,len(AllProducts)):
                        ProdName = AllProducts[i].ProductName.lower()
                        ProdDescription = AllProducts[i].Description.lower()
                        ProdIngredients = AllProducts[i].Ingredients.lower()
                        if(ProdName.find(SearchKeyword.lower()) != -1):
                            ProductIDs.append(AllProducts[i].ProductID)
                        elif(ProdDescription.find(SearchKeyword.lower()) != -1):
                            ProductIDs.append(AllProducts[i].ProductID)
                        elif(ProdIngredients.find(SearchKeyword.lower()) != -1):
                            ProductIDs.append(AllProducts[i].ProductID)
            ResponseData['ProductID'] = ProductIDs
            self.response.write(json.dumps(ResponseData))

# Below is code for fetching MyOrdersData for logged in user in android device.
        elif(FunctionOption == "MyOrdersData" and DBConnect != None):
            OrderID = []
            OrderType = []
            OrderStatus = []
            OrderTotal = []
            ActiveOrderDetails = []
            CompletedOrderDetails = []
            OrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail, OrdersDB.OrderStatus == "Active").fetch()
            UON1 = []
            UON2 = []
            if(OrderDetails != []):
                for i in range(0,len(OrderDetails)):
                    if(OrderDetails[i].OrderID not in UON1):
                        UON1.append(OrderDetails[i].OrderID)
                for i in range(0,len(UON1)):
                    OrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail, OrdersDB.OrderStatus == "Active", OrdersDB.OrderID == UON1[i]).fetch()
                    ActiveOrderDetails.append(OrderDetails[0])
                    OrderID.append(ActiveOrderDetails[i].OrderID)
                    OrderType.append(ActiveOrderDetails[i].OrderType)
                    OrderTotal.append(ActiveOrderDetails[i].GrandTotal)
                    if(len(OrderDetails) > 1):
                        for j in range(1,len(OrderDetails)):
                            if(ActiveOrderDetails[i].OrderSubStatus != "Reviewing" and OrderDetails[j].OrderSubStatus == "Reviewing"):
                                ActiveOrderDetails[i].OrderSubStatus = OrderDetails[j].OrderSubStatus
                    OrderStatus.append(ActiveOrderDetails[i].OrderSubStatus)
            OrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail, OrdersDB.OrderStatus == "Completed").fetch()
            if(OrderDetails != []):
                for i in range(0,len(OrderDetails)):
                    if(OrderDetails[i].OrderID not in UON1 and OrderDetails[i].OrderID not in UON2):
                        UON2.append(OrderDetails[i].OrderID)
                for i in range(0,len(UON2)):
                    OrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail, OrdersDB.OrderID == UON2[i]).fetch()
                    OrderID.append(OrderDetails[0].OrderID)
                    OrderType.append(OrderDetails[0].OrderType)
                    OrderTotal.append(OrderDetails[0].GrandTotal)
                    if(len(OrderDetails)>1):
                        OS = OrderDetails[0].OrderStatus
                        OSS = OrderDetails[0].OrderSubStatus
                        for j in range(1,len(OrderDetails)):
                            if(OS != OrderDetails[j].OrderStatus):
                                OS = OrderDetails[j]
                            if(OSS != OrderDetails[j].OrderSubStatus and OSS != "OrderComplete"):
                                OSS = OrderDetails[j].OrderSubStatus
                            if(OS == "Completed"):
                                CompletedOrderDetails.append(OrderDetails[0])
                                if(OSS != CompletedOrderDetails[len(CompletedOrderDetails)-1].OrderSubStatus):
                                    OrderDetails[0].OrderSubStatus = OSS
                    else:
                        if(OrderDetails[0].OrderStatus == "Completed"):
                            CompletedOrderDetails.append(OrderDetails[0])
                    OrderStatus.append(OrderDetails[0].OrderSubStatus)
            ResponseData['OrderID'] = OrderID
            ResponseData['OrderType'] = OrderType
            ResponseData['OrderStatus'] = OrderStatus
            ResponseData['OrderTotal'] = OrderTotal
            self.response.write(json.dumps(ResponseData))

        elif(FunctionOption == "MyOrdersData" and DBConnect == None):
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserNotRegistered"
            self.response.write(json.dumps(ResponseData))

# Below is code for fetching OrdersData for selected OrderID of logged in user in android device.
        elif(FunctionOption == "OrderIDData" and DBConnect != None):
            OrderID = JD["OrderID"]
            ProductID = []
            PharmacyID = []
            ProductStatus = []
            ServiceCharge = 0.0
            DeliveryCharge = 0.0
            ReUploadPrescription = 0
            PaymentRequired = 0
            SubTotalPrice = 0.0

            OrderData = OrdersDB.query(OrdersDB.OrderID == OrderID).fetch()
            if(OrderData != []):
                OrderDetails = OrderData[0]
                DeliveryCharge = DeliveryCharge + OrderData[0].DeliveryCharge
                for i in range(0,len(OrderDetails.ProductID)):
                    PharmacyID.append(OrderData[0].PharmacyID) # I have got pharmacy id for each product id.
                    ProductStatus.append(OrderData[0].OrderSubStatus) # I have got individual product status from here.
                    SubTotalPrice = SubTotalPrice + (OrderDetails.Quantity[i] * OrderDetails.Price[i])
                    if(OrderData[0].OrderSubStatus == "ReUploadPrescription"):
                        ReUploadPrescription = 1
                        PaymentRequired = 0
                    elif(OrderData[0].OrderSubStatus == "PaymentRequired"):
                        ReUploadPrescription = 0
                        PaymentRequired = 1
                    elif(OrderData[0].OrderSubStatus == "CancelledByVendor" and len(OrderData) > 1):
                        ReUploadPrescription = 0
                        PaymentRequired = 1
                    else:
                        ReUploadPrescription = 0
                        PaymentRequired = 0
                if(len(OrderData) > 1):
                    for i in range(1,len(OrderData)):
                        DeliveryCharge = DeliveryCharge + OrderData[i].DeliveryCharge
                        if(OrderData[i].OrderSubStatus != "CancelledByVendor" and OrderData[i].OrderSubStatus != "CancelledByCustomer" and OrderDetails.ServiceCharge == 0.0):
                            if(OrderData[i].OrderType != "Collection"):
                                OrderDetails.ServiceCharge = 1.0
                            OrderDetails.OrderTotal = OrderDetails.OrderTotal + OrderData[i].OrderTotal
                        elif(OrderData[i].OrderSubStatus != "CancelledByVendor" and OrderData[i].OrderSubStatus != "CancelledByCustomer" and OrderDetails.ServiceCharge != 0.0):
                            OrderDetails.OrderTotal = OrderDetails.OrderTotal + OrderData[i].OrderTotal - OrderData[i].ServiceCharge
                        OrderDetails.DeliveryCharge = OrderDetails.DeliveryCharge + OrderData[i].DeliveryCharge
                        if(OrderDetails.PrescriptionRequired == 0):
                            OrderDetails.PrescriptionRequired = OrderData[i].PrescriptionRequired
                            if(OrderDetails.PrescriptionRequired == 1):
                                OrderDetails.PrescriptionImage = OrderData[i].PrescriptionImage
                        for j in range(0,len(OrderData[i].ProductID)):
                            PharmacyID.append(OrderData[i].PharmacyID)
                            OrderDetails.ProductID.append(OrderData[i].ProductID[j])
                            OrderDetails.Quantity.append(OrderData[i].Quantity[j])
                            OrderDetails.Price.append(OrderData[i].Price[j])
                            SubTotalPrice = SubTotalPrice + (OrderData[i].Quantity[j] * OrderData[i].Price[j])
                            ProductStatus.append(OrderData[i].OrderSubStatus)
                        if(OrderData[i].OrderSubStatus == "ReUploadPrescription"):
                            ReUploadPrescription = 1
                            PaymentRequired = 0
                        elif(OrderData[i].OrderSubStatus == "CancelledByVendor" and PaymentRequired == 1):
                            ReUploadPrescription = 0
                            PaymentRequired = 1
                        elif(OrderData[i].OrderSubStatus == "PaymentRequired" and PaymentRequired == 1):
                            ReUploadPrescription = 0
                            PaymentRequired = 1
                        else:
                            PaymentRequired = 0
                ProductID = OrderDetails.ProductID
                ServiceCharge = OrderDetails.ServiceCharge

                ResponseData['OrderID'] = OrderID
                ResponseData['notification'] = "DataFound"
                ResponseData['OrderType'] = OrderDetails.OrderType
                ResponseData['ProductID'] = ProductID
                ResponseData['Quantity'] = OrderDetails.Quantity
                ResponseData['Price'] = OrderDetails.Price
                ResponseData['PharmacyID'] = PharmacyID
                ResponseData['ProductStatus'] = ProductStatus
                ResponseData['ServiceCharge'] = ServiceCharge
                ResponseData['DeliveryCharge'] = DeliveryCharge
                ResponseData['PrescriptionRequired'] = OrderDetails.PrescriptionRequired
                ResponseData['PrescriptionImage'] = OrderDetails.PrescriptionImage
                ResponseData['ReUploadPrescription'] = ReUploadPrescription
                ResponseData['PaymentRequired'] = PaymentRequired
                ResponseData['SubTotalPrice'] = SubTotalPrice
            else:
                ResponseData['OrderID'] = OrderID
                ResponseData['notification'] = "NoData"
            self.response.write(json.dumps(ResponseData))
        elif(FunctionOption == "OrderIDData" and DBConnect == None):
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "UserNotRegistered"
            self.response.write(json.dumps(ResponseData))

# Below is code for fetching data for given pharmacy id.
        elif(FunctionOption == "PharmacyData" and DBConnect != None):
            PharmacyID = JD["PharmacyID"]
            PharmacyData = ndb.Key("PharmacyDB",PharmacyID).get()
            ResponseData['PharmacyID'] = PharmacyData.PharmacyID
            ResponseData['PharmacyName'] = PharmacyData.PharmacyName
            ResponseData['OfficialEmailId'] = PharmacyData.OfficialEmailId
            ResponseData['OfficialContact'] = PharmacyData.OfficialContact
            ResponseData['PhysicalAddress'] = PharmacyData.PhysicalAddress
            ResponseData['Latitude'] = PharmacyData.Latitude
            ResponseData['Longitude'] = PharmacyData.Longitude
            self.response.write(json.dumps(ResponseData))

# In case no function satisfy conditions, below will be returned.
        else:
            ResponseData['userEmail'] = userEmail
            ResponseData['notification'] = "FunctionNotRecognized"
            self.response.write(json.dumps(ResponseData))

app = webapp2.WSGIApplication([
    ('/API_MediCare',API_MediCare),
], debug=True)
