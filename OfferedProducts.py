import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from ProductsDB import ProductsDB
from VendorsDB import VendorsDB
from VendorProductsDB import VendorProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class OfferedProducts(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get('vendorEmail')
        Query = self.request.get('Query')
        VendorDetails = []
        ProductDetails = []
        VendorProducts = []

        if(vendorEmail != ""):
            VendorDetails = ndb.Key("VendorsDB",vendorEmail).get()
            if(VendorDetails == None):
                self.redirect('/VendorSignIn')
            else:
                if(Query == "True"):
                    SearchKeyword = self.request.get('SearchKeyword')
                    Product = []
                    AllProducts = ProductsDB.query().fetch()
                    if(AllProducts != None):
                        for i in range(0,len(AllProducts)):
                            ProdName = AllProducts[i].ProductName.lower()
                            ProdDescription = AllProducts[i].Description.lower()
                            ProdIngredients = AllProducts[i].Ingredients.lower()
                            if(ProdName.find(SearchKeyword.lower()) != -1):
                                Product.append(AllProducts[i])
                            elif(ProdDescription.find(SearchKeyword.lower()) != -1):
                                Product.append(AllProducts[i])
                            elif(ProdIngredients.find(SearchKeyword.lower()) != -1):
                                Product.append(AllProducts[i])
                    if(Product != []):
                        for i in range(0,len(Product)):
                            if((ndb.Key("VendorProductsDB",VendorDetails.PharmacyID+Product[i].ProductID).get()) != None):
                                ProductDetails.append(Product[i])
                                VendorProducts.append(ndb.Key("VendorProductsDB",VendorDetails.PharmacyID+Product[i].ProductID).get())
                else:
                    VendorProducts = VendorProductsDB.query(VendorProductsDB.PharmacyID == VendorDetails.PharmacyID).fetch()
                    for i in VendorProducts:
                        ProductDetails.append(ndb.Key("ProductsDB",i.ProductID).get())
        else:
            self.redirect('/VendorSignIn')

        template_values = {
            'VendorDetails' : VendorDetails,
            'VendorProducts' : VendorProducts,
            'ProductDetails' : ProductDetails,
        }

        template = JINJA_ENVIRONMENT.get_template('OfferedProducts.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get('vendorEmail')
        if(vendorEmail != ""):
            VendorDetails = ndb.Key("VendorsDB",vendorEmail).get()
            if(VendorDetails != None):
                Button = self.request.get('Button')
                if(Button == "Search"):
                    SearchBar = self.request.get('SearchBar')
                    self.redirect('/OfferedProducts?vendorEmail='+vendorEmail+'&Query=True&SearchKeyword='+SearchBar)
            else:
                self.redirect('/VendorSignIn')
        else:
            self.redirect('/VendorSignIn')

app = webapp2.WSGIApplication([
    ('/OfferedProducts',OfferedProducts),
], debug=True)
