import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url
from datetime import datetime
from math import sin, cos, sqrt, atan2, radians
from EmailModule import SendEmail
from CartCount import getCartCount
from UsersDB import UsersDB
from ProductsDB import ProductsDB
from VendorProductsDB import VendorProductsDB
from PharmacyDB import PharmacyDB
from CartDB import CartDB
from OrdersDB import OrdersDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class ShoppingCart(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get('userEmail')
        Button = self.request.get('Button')
        notification = self.request.get('notification')
        SignInStatus = ""
        UserDetails = None
        ProductDetails = []
        Category = []
        CartData = []
        Latitude1 = 0.0
        Longitude1 = 0.0
        Distance = {}
        ProductDetailsLength = 0
        ImageUploadURL = "/ShoppingCart"

        if(userEmail != ""):
            UserDetails = ndb.Key('UsersDB',userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails != None and UserDetails.IsActive == 1):
                Latitude1 = UserDetails.Latitude
                Longitude1 = UserDetails.Longitude
                SignInStatus = "SignOut"
                CartCount = getCartCount(self,userEmail)
                CartData = ndb.Key("CartDB",userEmail).get()
                if(CartData != None):
                    if(CartData.PrescriptionRequired == 1):
                        ImageUploadURL = blobstore.create_upload_url("/ShoppingCart")
                    for i in range(0,len(CartData.ProductID)):
                        ProductData = ndb.Key("ProductsDB",CartData.ProductID[i]).get()
                        ProductDetails.append(ProductData)
                ProductDetailsLength = len(ProductDetails)
                if(Button == "RemoveFromCart"):
                    ProductID = self.request.get("ProductID")
                    ProductData = ndb.Key("ProductsDB",ProductID).get()
                    if(len(CartData.ProductID)>1):
                        for i in range(0,len(CartData.ProductID)):
                            if(CartData.ProductID[i] == ProductID):
                                del CartData.ProductID[i]
                                # del CartData.Quantity[i]
                                # del CartData.PharmacyID[i]
                                # del CartData.Price[i]
                                CartData.put()
                                break
                        if(ProductData.PrescriptionRequired == 1):
                            CartData.PrescriptionRequired = 0
                            del CartData.PrescriptionImage
                            CartData.put()
                    else:
                        CartData.key.delete()
                    self.redirect('/ShoppingCart?userEmail='+UserDetails.user_Email+'&notification=ProductRemoved')
        else:
            self.redirect('/UserSignIn')

        ProductsData = ProductsDB.query().fetch()
        if(ProductsData == []):
            ProductsData = None
        else:
            for i in range(0,len(ProductsData)):
                if(ProductsData[i].Category not in Category):
                    Category.append(ProductsData[i].Category)
        Category.sort()

        VendorProductsDetails = VendorProductsDB.query().fetch()
        PharmacyDetails = PharmacyDB.query().fetch()
        if(PharmacyDetails != None):
            for i in PharmacyDetails:
                Latitude2 = i.Latitude
                Longitude2 = i.Longitude
                DifferenceInLatitude = radians(Latitude2 - Latitude1)
                DifferenceInLongitude = radians(Longitude2 - Longitude1)
                Formula = (sin(DifferenceInLatitude/2)**2) + cos(radians(Latitude1)) * cos(radians(Latitude2)) * (sin(DifferenceInLongitude/2)**2)
                Result = 6373.0*2*atan2(sqrt(Formula),sqrt(1-Formula))
                Distance[i.PharmacyID] = round(Result,3)
            Distance = sorted(Distance.items(), key=lambda x:x[1])

        template_values = {
            'SignInStatus' : SignInStatus,
            'UserDetails' : UserDetails,
            'CartCount' : CartCount,
            'CartData' : CartData,
            'ImageUploadURL' : ImageUploadURL,
            'ProductDetails' : ProductDetails,
            'ProductDetailsLength' : ProductDetailsLength,
            'PharmacyDetails' : PharmacyDetails,
            'VendorProductsDetails' : VendorProductsDetails,
            'Category' : Category,
            'Distance' : Distance,
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('ShoppingCart.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get("userEmail")
        if(userEmail != ""):
            UserDetails = ndb.Key('UsersDB',userEmail).get()
            Latitude1 = 0.0
            Longitude2 = 0.0
            if(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails != None and UserDetails.IsActive == 1):
                Latitude1 = UserDetails.Latitude
                Longitude1 = UserDetails.Longitude
                CartData = ndb.Key("CartDB",userEmail).get()
                if(CartData != None):
                    UserComments = self.request.get("UserComments")
                    OrderType = self.request.get('OrderType')
                    CartData.UserComments = UserComments
                    Quantity = []
                    PharmacyID = []
                    UniquePharmacy = []
                    Price = []
                    DeliveryCharge = 0.00
                    ServiceCharge = 0.00
                    CartTotal = 0.00
                    Valid = True
                    if(CartData.PrescriptionRequired == 1):
                        Images = self.get_uploads()[0]
                        PrescriptionImage = get_serving_url(Images.key())
                        CartData.PrescriptionImage = PrescriptionImage
                    for i in range(0,len(CartData.ProductID)):
                        Key1 = "Quantity"+CartData.ProductID[i]
                        if(self.request.get(Key1) == ""):
                            self.redirect('/ShoppingCart?userEmail='+UserDetails.user_Email+'&notification=InvalidQuantityOrPharmacyName')
                            Valid = False
                            break
                        else:
                            Quantity.append(int(self.request.get(Key1)))
                        Key2 = "PharmacyName"+CartData.ProductID[i]
                        if(self.request.get(Key2) == ""):
                            self.redirect('/ShoppingCart?userEmail='+UserDetails.user_Email+'&notification=InvalidQuantityOrPharmacyName')
                            Valid = False
                            break
                        else:
                            PharmacyID.append(self.request.get(Key2))
                    if(OrderType != ""):
                        if(Valid == True):
                            CartData.Quantity = Quantity
                            CartData.PharmacyID = PharmacyID
                            CartData.OrderType = OrderType
                            if(OrderType == "Delivery"):
                                for i in range(0,len(CartData.PharmacyID)):
                                    VPData = ndb.Key("VendorProductsDB",CartData.PharmacyID[i]+""+CartData.ProductID[i]).get()
                                    Price.append(VPData.Price)
                                    CartTotal = CartTotal + (VPData.Price*CartData.Quantity[i])
                                    if(CartData.PharmacyID[i] not in UniquePharmacy):
                                        UniquePharmacy.append(CartData.PharmacyID[i])
                                for i in UniquePharmacy:
                                    PharmacyData = ndb.Key("PharmacyDB",i).get()
                                    if(PharmacyData != None):
                                        Latitude2 = PharmacyData.Latitude
                                        Longitude2 = PharmacyData.Longitude
                                        DifferenceInLatitude = radians(Latitude2 - Latitude1)
                                        DifferenceInLongitude = radians(Longitude2 - Longitude1)
                                        Formula = (sin(DifferenceInLatitude/2)**2) + cos(radians(Latitude1)) * cos(radians(Latitude2)) * (sin(DifferenceInLongitude/2)**2)
                                        Result = 6373.0*2*atan2(sqrt(Formula),sqrt(1-Formula))
                                        if(round(Result,3) <= 1.5):
                                            DeliveryCharge = DeliveryCharge + 1.00
                                        elif(round(Result,3) > 1.5 and round(Result,3) <= 3.0):
                                            DeliveryCharge = DeliveryCharge + 2.00
                                        elif(round(Result,3) > 3.0 and round(Result,3) <= 4.5):
                                            DeliveryCharge = DeliveryCharge + 3.00
                                        elif(round(Result,3) > 4.5 and round(Result,3) <= 6.0):
                                            DeliveryCharge = DeliveryCharge + 4.00
                                        else:
                                            DeliveryCharge = DeliveryCharge + 5.00
                                ServiceCharge = 1.00
                            else:
                                for i in range(0,len(CartData.PharmacyID)):
                                    VPData = ndb.Key("VendorProductsDB",CartData.PharmacyID[i]+""+CartData.ProductID[i]).get()
                                    Price.append(VPData.Price)
                                    CartTotal = CartTotal + (VPData.Price*CartData.Quantity[i])
                            CartData.Price = Price
                            CartData.DeliveryCharge = DeliveryCharge
                            CartData.ServiceCharge = ServiceCharge
                            CartTotal = CartTotal + DeliveryCharge + ServiceCharge
                            CartData.CartTotal = CartTotal
                            CartData.put()
# Now placing request in orders for review.
                            OrderID = datetime.now().strftime("%Y%m%d%H%M%S")
                            OrderPlacedOn = datetime.now().strftime("%d/%m/%Y at %H:%M:%S")
                            UniquePharmacyID = []
                            for i in range(0,len(CartData.PharmacyID)):
                                if(CartData.PharmacyID[i] not in UniquePharmacyID):
                                    UniquePharmacyID.append(CartData.PharmacyID[i])
                            for i in range(0,len(UniquePharmacyID)):
                                OrdersConnect = OrdersDB(userEmail = userEmail)
                                OrdersConnect.OrderID = OrderID
                                OrdersConnect.OrderType = CartData.OrderType
                                OrdersConnect.PharmacyID = UniquePharmacyID[i]
                                PharmacyData = ndb.Key("PharmacyDB",UniquePharmacyID[i]).get()
                                PR = 0
                                DC = 0.00
                                if(PharmacyData != None and CartData.OrderType == "Delivery"):
                                    Latitude2 = PharmacyData.Latitude
                                    Longitude2 = PharmacyData.Longitude
                                    DifferenceInLatitude = radians(Latitude2 - Latitude1)
                                    DifferenceInLongitude = radians(Longitude2 - Longitude1)
                                    Formula = (sin(DifferenceInLatitude/2)**2) + cos(radians(Latitude1)) * cos(radians(Latitude2)) * (sin(DifferenceInLongitude/2)**2)
                                    Result = 6373.0*2*atan2(sqrt(Formula),sqrt(1-Formula))
                                    if(round(Result,3) <= 1.5):
                                        DC = 1.00
                                    elif(round(Result,3) > 1.5 and round(Result,3) <= 3.0):
                                        DC = 2.00
                                    elif(round(Result,3) > 3.0 and round(Result,3) <= 4.5):
                                        DC = 3.00
                                    elif(round(Result,3) > 4.5 and round(Result,3) <= 6.0):
                                        DC = 4.00
                                    else:
                                        DC = 5.00
                                OrdersConnect.OrderTotal = 0.00
                                for j in range(0,len(CartData.ProductID)):
                                    PD = ndb.Key("ProductsDB",CartData.ProductID[j]).get()
                                    if(UniquePharmacyID[i] == CartData.PharmacyID[j] and PD.PrescriptionRequired == 1 and PR == 0):
                                        PR = 1
                                        OrdersConnect.PrescriptionImage = CartData.PrescriptionImage
                                    elif(UniquePharmacyID[i] == CartData.PharmacyID[j] and PD.PrescriptionRequired == 0 and PR == 0):
                                        PR = 0
                                    if(UniquePharmacyID[i] == CartData.PharmacyID[j]):
                                        OrdersConnect.ProductID.append(CartData.ProductID[j])
                                        OrdersConnect.Price.append(CartData.Price[j])
                                        OrdersConnect.Quantity.append(CartData.Quantity[j])
                                        OrdersConnect.OrderTotal = OrdersConnect.OrderTotal + (CartData.Quantity[j]*CartData.Price[j])
                                OrdersConnect.PrescriptionRequired = PR
                                OrdersConnect.DeliveryCharge = DC
                                OrdersConnect.OrderTotal = OrdersConnect.OrderTotal + DC + CartData.ServiceCharge
                                OrdersConnect.ServiceCharge = CartData.ServiceCharge
                                OrdersConnect.OrderPlacedOn = OrderPlacedOn
                                OrdersConnect.UserComments = CartData.UserComments
                                OrdersConnect.GrandTotal = CartData.CartTotal
                                OrdersConnect.GrandDC = CartData.DeliveryCharge
                                OrdersConnect.OrderStatus = "Active"
                                OrdersConnect.OrderSubStatus = "Reviewing"
                                OrdersConnect.put()
                            SendEmail(userEmail,"Your order has been successfully submitted for reviewing at MediCare","""
Dear """+UserDetails.user_FirstName+""",

This is an automated email confirmation sent to you in regards of your recently placed order at MediCare.

Your order has been successfully placed on """+OrderPlacedOn+""".
You can view the same in "My Orders" tab after logging into your MediCare account.

Please note your Order ID : """+OrderID+""" for the reference.

Thanks & regards,
MediCare Team.
                            """)
                            CartData.key.delete()
                            self.redirect('/?userEmail='+UserDetails.user_Email)
                        else:
                            self.redirect('/ShoppingCart?userEmail='+UserDetails.user_Email+'&notification=InvalidQuantityOrPharmacyName')
                    else:
                        self.redirect('/ShoppingCart?userEmail='+UserDetails.user_Email+'&notification=InvalidOrderType')
                else:
                    self.redirect('/ShoppingCart?userEmail='+UserDetails.user_Email)
            else:
                self.redirect('/UserSignIn')
        else:
            self.redirect('/UserSignIn')

app = webapp2.WSGIApplication([
    ('/ShoppingCart',ShoppingCart),
], debug=True)
