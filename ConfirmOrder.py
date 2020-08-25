import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from math import sin, cos, sqrt, atan2, radians
from UsersDB import UsersDB
from ProductsDB import ProductsDB
from VendorProductsDB import VendorProductsDB
from PharmacyDB import PharmacyDB
from CartDB import CartDB

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
        OrderTotal = 1.0
        DeliveryCharge = 0.0
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
                        ProductData.Quantity = CartData.Quantity[i]
                        Price.append(ProductData.Price)
                        ProductDetails.append(ProductData)
                    CartData.ServiceCharge = 1.0
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
                CartData.DeliveryCharge = DeliveryCharge
            else:
                CartData.DeliveryCharge = 0.0
            CartData.CartTotal = OrderTotal
            CartData.put()

        template_values = {
            'SignInStatus' : SignInStatus,
            'UserDetails' : UserDetails,
            'CartData' : CartData,
            'ProductDetails' : ProductDetails,
            'OrderTotal' : OrderTotal,
            'DeliveryCharge' : DeliveryCharge,
            'Category' : Category,
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('ConfirmOrder.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get("userEmail")


app = webapp2.WSGIApplication([
    ('/ConfirmOrder',ConfirmOrder),
], debug=True)
