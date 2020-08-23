import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from API_MediCare import API_MediCare
from AdminDB import AdminDB
from UsersDB import UsersDB
from PharmacyDB import PharmacyDB
from VendorsDB import VendorsDB
from ProductsDB import ProductsDB
from CartDB import CartDB
from ContactUsDB import ContactUsDB
from EmailModule import SendEmail
from AdminPanel import AdminPanel
from UserSignIn import UserSignIn
from VendorSignIn import VendorSignIn
from VendorHomePage import VendorHomePage
from AddProducts import AddProducts
from VendorProductDetails import VendorProductDetails
from ProductDetails import ProductDetails
from BrowseByCategory import BrowseByCategory
from OfferedProducts import OfferedProducts
from ContactUs import ContactUs
from TermsOfUse import TermsOfUse
from Profile import Profile
from VerifyEmail import VerifyEmail
from ResetPassword import ResetPassword

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class mainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get('userEmail')
        SearchBarText = self.request.get('SearchBarText')
        Button = self.request.get('Button')
        UserDetails = None
        ProductDetails = []
        Category = []

        if(userEmail != ""):
            UserDetails = ndb.Key('UsersDB',userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            SignInStatus = "SignOut"
        else:
            SignInStatus = "SignIn"

        ProductsData = ProductsDB.query().fetch()
        if(ProductsData == []):
            ProductsData = None
        else:
            for i in range(0,len(ProductsData)):
                if(ProductsData[i].Category not in Category):
                    Category.append(ProductsData[i].Category)
        Category.sort()

        if(Button == "Search"):
            if(SearchBarText != ""):
                AllProducts = ProductsDB.query().fetch()
                if(AllProducts != None):
                    for i in range(0,len(AllProducts)):
                        ProdName = AllProducts[i].ProductName.lower()
                        ProdDescription = AllProducts[i].Description.lower()
                        ProdIngredients = AllProducts[i].Ingredients.lower()
                        if(ProdName.find(SearchBarText.lower()) != -1):
                            ProductDetails.append(AllProducts[i])
                        elif(ProdDescription.find(SearchBarText.lower()) != -1):
                            ProductDetails.append(AllProducts[i])
                        elif(ProdIngredients.find(SearchBarText.lower()) != -1):
                            ProductDetails.append(AllProducts[i])
        else:
            ProductDetails = ProductsDB.query().fetch()

        template_values = {
            'SignInStatus' : SignInStatus,
            'UserDetails' : UserDetails,
            'ProductDetails' : ProductDetails,
            'Category' : Category,
        }

        template = JINJA_ENVIRONMENT.get_template('mainPage.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        Button = self.request.get('Button')
        userEmail = self.request.get('userEmail')
        if(Button == "Add To Cart"):
            ProductID = self.request.get('ProductID')
            CartDBStatus = ndb.Key("CartDB",userEmail).get()
            if(CartDBStatus != None):
                if(ProductID not in CartDBStatus.ProductID):
                    CartDBStatus.ProductID.append(ProductID)
            else:
                CartDBStatus = CartDB(id=userEmail)
                CartDBStatus.userEmail = userEmail
                CartDBStatus.ProductID.append(ProductID)
            CartDBStatus.put()
            self.redirect('/?userEmail='+userEmail)
        else:
            self.redirect('/?userEmail='+userEmail)

app = webapp2.WSGIApplication([
    ('/',mainPage),
    ('/ResetPassword',ResetPassword),
    ('/UserSignIn',UserSignIn),
    ('/VendorSignIn',VendorSignIn),
    ('/VendorHomePage',VendorHomePage),
    ('/AddProducts',AddProducts),
    ('/VendorProductDetails',VendorProductDetails),
    ('/ProductDetails',ProductDetails),
    ('/BrowseByCategory',BrowseByCategory),
    ('/ContactUs',ContactUs),
    ('/TermsOfUse',TermsOfUse),
    ('/Profile',Profile),
    ('/OfferedProducts',OfferedProducts),
    ('/VerifyEmail',VerifyEmail),
    ('/AdminPanel',AdminPanel),
    ('/API_MediCare',API_MediCare),
], debug=True)
