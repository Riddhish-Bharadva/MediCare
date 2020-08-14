import webapp2
import jinja2
import os
from datetime import datetime
from google.appengine.ext import ndb
from ProductsDB import ProductsDB
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class VendorProducts(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get('vendorEmail')
        Category = []
        CategoryCount = 0
        SubCategory = []
        SubCategoryCount = 0
        ImageUploadURL = ""

        if(vendorEmail == ""):
            self.redirect('/VendorSignIn')
        else:
            ImageUploadURL = blobstore.create_upload_url("/VendorProducts")
            Products = ProductsDB.query().get()
            if(Products != None):
                self.response.write(Products)
                for i in Products:
                    if(Products.Category not in Category.values):
                        Category.append(Products.Category)
                        CategoryCount = CategoryCount + 1
                        self.response.write("Products"+Products)
                    if(Products.SubCategory not in SubCategory.values):
                        SubCategory.append(Products.SubCategory)
                        SubCategoryCount = SubCategoryCount + 1
                        self.response.write("SubCategory"+SubCategory)
            else:
                self.response.write("No products yet!")

        template_values = {
            'vendorEmail' : vendorEmail,
            'Category' : Category,
            'CategoryCount' : CategoryCount,
            'SubCategory' : SubCategory,
            'SubCategoryCount' : SubCategoryCount,
            'Products' : Products,
            'ImageUploadURL' : ImageUploadURL,
        }

        template = JINJA_ENVIRONMENT.get_template('VendorProducts.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        vendorEmail = self.response.get('vendorEmail')
        if(vendorEmail == ""):
            self.redirect('/VendorSignIn')
        else:
            Option = self.request.get('Option')
            if(Option == 1):
                ProductID = datetime.now().strftime("%Y%m%d%H%M%S")
                Images = self.get_uploads()
                self.response.write(Images)
            else:
                do = 0

app = webapp2.WSGIApplication([
    ('/VendorProducts',VendorProducts),
], debug=True)
