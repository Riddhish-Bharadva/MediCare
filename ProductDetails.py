import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from CartCount import getCartCount
from UsersDB import UsersDB
from ProductsDB import ProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class ProductDetails(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get('userEmail')
        if(userEmail != ""):
            UserDetails = ndb.Key("UsersDB",userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            else:
                self.redirect('/?userEmail='+userEmail)
        else:
            self.redirect('/UserSignIn')

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get('userEmail')
        ProductID = self.request.get('ProductID')
        UserDetails = None
        Category = []

        if(userEmail != ""):
            UserDetails = ndb.Key("UsersDB",userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            SignInStatus = "SignOut"
            CartCount = getCartCount(self,userEmail)
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

        ProductDetails = ndb.Key("ProductsDB",ProductID).get()
        if(ProductDetails != None):
            ImageCount = len(ProductDetails.Images)
        elif(UserDetails != None):
            self.redirect("/?userEmail="+userEmail)
        else:
            self.redirect("/")

        template_values = {
            'SignInStatus' : SignInStatus,
            'Category' : Category,
            'CartCount' : CartCount,
            'UserDetails' : UserDetails,
            'ProductDetails' : ProductDetails,
            'ImageCount' : ImageCount,
        }

        template = JINJA_ENVIRONMENT.get_template('ProductDetails.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/ProductDetails',ProductDetails),
], debug=True)
