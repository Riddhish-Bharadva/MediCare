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

class ShoppingCart(webapp2.RequestHandler):
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
                CartData = ndb.Key("CartDB",userEmail).get()
                if(CartData != None):
                    for i in range(0,len(CartData.ProductID)):
                        ProductData = ndb.Key("ProductsDB",CartData.ProductID[i]).get()
                        ProductDetails.append(ProductData)
                ProductDetailsLength = len(ProductDetails)
                if(Button == "RemoveFromCart"):
                    ProductID = self.request.get("ProductID")
                    if(len(CartData.ProductID)>1):
                        for i in range(0,len(CartData.ProductID)):
                            if(CartData.ProductID[i] == ProductID):
                                del CartData.ProductID[i]
                                del CartData.Quantity[i]
                                CartData.put()
                                break
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
            'ProductDetails' : ProductDetails,
            'ProductDetailsLength' : ProductDetailsLength,
            'PharmacyDetails' : PharmacyDetails,
            'VendorProductsDetails' : VendorProductsDetails,
            'CartData' : CartData,
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
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            CartData = ndb.Key("CartDB",userEmail).get()
            if(CartData != None):
                Quantity = []
                PharmacyID = []
                OrderType = self.request.get('OrderType')
                Valid = True
                for i in range(0,len(CartData.ProductID)):
                    Key1 = "Quantity"+CartData.ProductID[i]
                    if(self.request.get(Key1) == "None"):
                        self.redirect('/ShoppingCart?userEmail='+UserDetails.user_Email+'&notification=InvalidQuantityOrPharmacyName')
                        Valid = False
                        break
                    else:
                        Quantity.append(int(self.request.get(Key1)))
                    Key2 = "PharmacyName"+CartData.ProductID[i]
                    if(self.request.get(Key2) == "None"):
                        self.redirect('/ShoppingCart?userEmail='+UserDetails.user_Email+'&notification=InvalidQuantityOrPharmacyName')
                        Valid = False
                        break
                    else:
                        PharmacyID.append(self.request.get(Key2))
                if(OrderType != None or OrderType != ""):
                    if(Valid == True):
                        CartData.Quantity = Quantity
                        CartData.PharmacyID = PharmacyID
                        CartData.OrderType = OrderType
                        CartData.put()
                        self.redirect('/ConfirmOrder?userEmail='+UserDetails.user_Email)
                else:
                    self.redirect('/ShoppingCart?userEmail='+UserDetails.user_Email+'&notification=InvalidOrderType')
        else:
            self.redirect('/UserSignIn')

app = webapp2.WSGIApplication([
    ('/ShoppingCart',ShoppingCart),
], debug=True)
