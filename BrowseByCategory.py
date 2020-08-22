import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from UsersDB import UsersDB
from ProductsDB import ProductsDB
from UserSignIn import UserSignIn
from ProductDetails import ProductDetails

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class BrowseByCategory(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get('userEmail')
        BrowseByCategory = self.request.get('Category')
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

        ProductDetails = ProductsDB.query(ProductsDB.Category == BrowseByCategory).fetch()

        template_values = {
            'SignInStatus' : SignInStatus,
            'UserDetails' : UserDetails,
            'ProductDetails' : ProductDetails,
            'Category' : Category,
            'BrowseByCategory' : BrowseByCategory,
        }

        template = JINJA_ENVIRONMENT.get_template('BrowseByCategory.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/BrowseByCategory',BrowseByCategory),
], debug=True)
