import webapp2
import jinja2
import os
from datetime import datetime
from google.appengine.ext import ndb
from math import sin, cos, sqrt, atan2, radians
from EmailModule import SendEmail
from UsersDB import UsersDB
from ProductsDB import ProductsDB
from VendorProductsDB import VendorProductsDB
from PharmacyDB import PharmacyDB
from CartDB import CartDB
from OrdersDB import OrdersDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class ConfirmOrder(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get('userEmail')
        notification = self.request.get('notification')
        SignInStatus = ""
        UserDetails = None
        CartData = None
        ProductDetails = []
        OrderTotal = 0.0
        DeliveryCharge = 0.0
        ServiceCharge = 1.0
        SubTotal = 0.0
        Price = []
        UniquePharmacy = []
        Distance = {}
        Category = []
        CartData = []

        if(userEmail != ""):
            UserDetails = ndb.Key('UsersDB',userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails != None and UserDetails.IsActive == 1):
                SignInStatus = "SignOut"
                Latitude1 = UserDetails.Latitude
                Longitude1 = UserDetails.Longitude
                CartData = ndb.Key("CartDB",userEmail).get()
                if(CartData != None):
                    for i in range(0,len(CartData.ProductID)):
                        ProductData = ndb.Key("ProductsDB",CartData.ProductID[i]).get()
                        VendorProductsData = ndb.Key("VendorProductsDB",CartData.PharmacyID[i]+""+CartData.ProductID[i]).get()
                        ProductData.Price = CartData.Quantity[i]*VendorProductsData.Price
                        SubTotal = SubTotal + CartData.Quantity[i]*VendorProductsData.Price
                        ProductData.Quantity = CartData.Quantity[i]
                        Price.append(ProductData.Price)
                        ProductDetails.append(ProductData)
                    CartData.Price = Price
                    CartData.put()
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

        for i in ProductDetails:
            OrderTotal = OrderTotal + i.Price
        if(CartData != None and CartData != []):
            for i in CartData.PharmacyID:
                if(i not in UniquePharmacy):
                    UniquePharmacy.append(i)
            for i in UniquePharmacy:
                PharmacyData = ndb.Key("PharmacyDB",i).get()
                if(PharmacyData != None):
                    Latitude2 = PharmacyData.Latitude
                    Longitude2 = PharmacyData.Longitude
                    DifferenceInLatitude = radians(Latitude2 - Latitude1)
                    DifferenceInLongitude = radians(Longitude2 - Longitude1)
                    Formula = (sin(DifferenceInLatitude/2)**2) + cos(radians(Latitude1)) * cos(radians(Latitude2)) * (sin(DifferenceInLongitude/2)**2)
                    Result = 6373.0*2*atan2(sqrt(Formula),sqrt(1-Formula))
                    Distance[PharmacyData.PharmacyID] = round(Result,3)
                    if(round(Result,3) <= 1.5):
                        DeliveryCharge = DeliveryCharge + 1.0
                    elif(round(Result,3) > 1.5 and round(Result,3) <= 3.0):
                        DeliveryCharge = DeliveryCharge + 2.0
                    elif(round(Result,3) > 3.5 and round(Result,3) <= 4.5):
                        DeliveryCharge = DeliveryCharge + 3.0
                    elif(round(Result,3) > 4.5 and round(Result,3) <= 6.0):
                        DeliveryCharge = DeliveryCharge + 3.0
            if(CartData.OrderType == "Delivery"):
                CartData.DeliveryCharge = DeliveryCharge + ServiceCharge
                CartData.ServiceCharge = ServiceCharge
                OrderTotal = OrderTotal + DeliveryCharge + ServiceCharge
            else:
                CartData.DeliveryCharge = 0.0
                CartData.ServiceCharge = 0.0
                ServiceCharge = 0.0
            CartData.CartTotal = OrderTotal
            CartData.put()

        template_values = {
            'SignInStatus' : SignInStatus,
            'UserDetails' : UserDetails,
            'CartData' : CartData,
            'ProductDetails' : ProductDetails,
            'OrderTotal' : OrderTotal,
            'DeliveryCharge' : DeliveryCharge,
            'ServiceCharge' : ServiceCharge,
            'SubTotal' : SubTotal,
            'Category' : Category,
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('ConfirmOrder.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get("userEmail")
        if(userEmail != ""):
            UserDetails = ndb.Key('UsersDB',userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails != None and UserDetails.IsActive == 1):
                SignInStatus = "SignOut"
                PaymentStatus = self.request.get("PaymentStatus")
                if(PaymentStatus == "Success"):
                    CartData = ndb.Key("CartDB",userEmail).get()
                    if(CartData != None):
                        OrderID = datetime.now().strftime("%Y%m%d%H%M%S")
                        OrderPlacedOn = datetime.now().strftime("%d/%m/%Y at %H:%M:%S")
                        UniquePharmacyID = []
                        for i in range(0,len(CartData.PharmacyID)):
                            ProductsData = ndb.Key("ProductsDB",CartData.ProductID[i]).get()
                            if(ProductsData.Quantity > 0):
                                ProductsData.Quantity = ProductsData.Quantity - CartData.Quantity[i]
                            VendorProductsData = ndb.Key("VendorProductsDB",CartData.PharmacyID[i]+""+CartData.ProductID[i]).get()
                            if(VendorProductsData.Quantity > 0):
                                VendorProductsData.Quantity = VendorProductsData.Quantity - CartData.Quantity[i]
                            else:
                                self.redirect("/ConfirmOrder?userEmail="+userEmail+"&notification=ProductNotAvailableInSelectedVendor")
                            VendorProductsData.put()
                            ProductsData.put()
                            if(CartData.PharmacyID[i] not in UniquePharmacyID):
                                UniquePharmacyID.append(CartData.PharmacyID[i])
                        for i in range(0,len(UniquePharmacyID)):
                            OrdersConnect = OrdersDB(userEmail = userEmail)
                            OrdersConnect.OrderID = OrderID
                            OrdersConnect.PrescriptionRequired = 0
                            OrdersConnect.OrderType = CartData.OrderType
                            OrdersConnect.PharmacyID = UniquePharmacyID[i]
                            for j in range(0,len(CartData.ProductID)):
                                if(UniquePharmacyID[i] == CartData.PharmacyID[j]):
                                    OrdersConnect.ProductID.append(CartData.ProductID[j])
                                    OrdersConnect.Price.append(CartData.Price[j])
                                    OrdersConnect.Quantity.append(CartData.Quantity[j])
                            OrdersConnect.DeliveryCharge = CartData.DeliveryCharge
                            OrdersConnect.ServiceCharge = CartData.ServiceCharge
                            OrdersConnect.OrderTotal = CartData.CartTotal
                            OrdersConnect.OrderPlacedOn = OrderPlacedOn
                            OrdersConnect.OrderStatus = "Active"
                            OrdersConnect.OrderSubStatus = "OrderPlaced"
                            OrdersConnect.put()
                        SendEmail(userEmail,"Your order has been successfully placed at MediCare","""
Dear """+UserDetails.user_FirstName+""",

This is an automated email confirmation sent to you in regards of your recently placed order at MediCare.

Your order has been successfully placed on """+OrderPlacedOn+""".
You can view the same in "My Orders" tab after logging into your MediCare account.

Please note your Order ID : """+OrderID+""" for the reference.

Thanks & regards,
MediCare Team.
                        """)
                        CartData.key.delete()
                        self.redirect("/ConfirmOrder?userEmail="+userEmail+"&notification=Success")
                    else:
                        self.redirect("/?userEmail="+userEmail)
                elif(PaymentStatus == "Failed"):
                    defg = 0
                    self.redirect("/ConfirmOrder?userEmail="+userEmail+"&notification=Failed")
        else:
            self.redirect('/UserSignIn')

app = webapp2.WSGIApplication([
    ('/ConfirmOrder',ConfirmOrder),
], debug=True)
