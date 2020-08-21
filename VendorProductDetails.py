import webapp2
import jinja2
import os
from datetime import datetime
from google.appengine.ext import ndb
from ProductsDB import ProductsDB
from VendorsDB import VendorsDB
from VendorProductsDB import VendorProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class VendorProductDetails(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get('vendorEmail')
        if(vendorEmail != ""):
            VendorDetails = ndb.Key("VendorsDB",vendorEmail).get()
            if(VendorDetails == None):
                self.redirect('/VendorSignIn')
            else:
                self.redirect('/VendorHomePage?vendorEmail='+vendorEmail)
        else:
            self.redirect('/VendorSignIn')

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get('vendorEmail')
        VendorDetails = None
        Mode = self.request.get('Mode')
        ProductID = self.request.get('ProductID')
        Option = 2
        ProductDetails = []
        Button = self.request.get("Button")
        ImageCount = 1
        ModeURL = ""

        if(Mode == "Add"):
            ModeURL = "/AddProducts"
        elif(Mode == "Edit"):
            ModeURL = "/VendorProductDetails"

        if(vendorEmail == ""):
            self.redirect('/VendorSignIn')
        else:
            VendorDetails = ndb.Key("VendorsDB",vendorEmail).get()
            if(VendorDetails == None):
                self.redirect('/VendorSignIn')
            else:
                ProductDetails = ndb.Key("ProductsDB",ProductID).get()
                VendorProductDetails = ndb.Key("VendorProductsDB",VendorDetails.PharmacyID+ProductID).get()
                ImageCount = len(ProductDetails.Images)
                if(Button == "UpdateProduct"):
                    ProductName = self.request.get('ProductName')
                    Description = self.request.get('Description')
                    Ingredients = self.request.get('Ingredients')
                    Dosage = self.request.get('Dosage')
                    ProductLife = self.request.get('ProductLife')
                    Category = self.request.get('Category')
                    SubCategory = self.request.get('SubCategory')
                    Quantity = int(self.request.get('Quantity'))
                    Price = float(self.request.get('Price'))
                    LastModifiedOn = datetime.now().strftime("%d/%m/%Y at %H:%M:%S")
                    LastModifiedBy = VendorDetails.Email

                    ProductDetails.ProductName = ProductName
                    ProductDetails.Description = Description
                    ProductDetails.Ingredients = Ingredients
                    ProductDetails.Dosage = Dosage
                    ProductDetails.ProductLife = ProductLife
                    ProductDetails.Category = Category
                    ProductDetails.SubCategory = SubCategory

                    VendorProductsDBConnect = ndb.Key("VendorProductsDB",VendorDetails.PharmacyID+ProductID).get()

                    if(Quantity < VendorProductsDBConnect.Quantity):
                        LessQ = VendorProductsDBConnect.Quantity - Quantity
                        ProductDetails.Quantity = ProductDetails.Quantity - LessQ
                    elif(Quantity > VendorProductsDBConnect.Quantity):
                        MoreQ = Quantity - VendorProductsDBConnect.Quantity
                        ProductDetails.Quantity = ProductDetails.Quantity + MoreQ

                    if(ProductDetails.Price > Price):
                        ProductDetails.Price = Price
                    else:
                        AllVendorData = VendorProductsDB.query(VendorProductsDB.ProductID == ProductID).fetch()
                        SmallestPrice = Price
                        for i in AllVendorData:
                            if(i.Price < Price and i.PharmacyID != VendorDetails.PharmacyID):
                                SmallestPrice = i.Price
                        ProductDetails.Price = SmallestPrice

                    VendorProductsDBConnect.LastModifiedBy = LastModifiedBy
                    VendorProductsDBConnect.LastModifiedOn = LastModifiedOn
                    VendorProductsDBConnect.Quantity = Quantity
                    VendorProductsDBConnect.Price = Price

                    ProductDetails.put()
                    VendorProductsDBConnect.put()
                    self.redirect('/VendorHomePage?vendorEmail='+vendorEmail+'&notification=ProductUpdatedSuccessfully')

                elif(Button == "DeleteProduct"):
                    VendorProductsDBConnect = ndb.Key("VendorProductsDB",VendorDetails.PharmacyID+ProductID).get()
                    if(len(ProductDetails.StockedIn) != 1):
                        Position = -1
                        for i in range(0,len(ProductDetails.StockedIn)):
                            if(ProductDetails.StockedIn[i] == VendorDetails.PharmacyID):
                                Position = i
                                break
                        if(Position != -1):
                            ProductDetails.Quantity = ProductDetails.Quantity - VendorProductsDBConnect.Quantity
                            del ProductDetails.StockedIn[Position]
                            AllVendorData = VendorProductsDBConnect.query(VendorProductsDB.ProductID == ProductID).fetch()
                            for i in range(0,len(AllVendorData)):
                                if(AllVendorData[i].PharmacyID != VendorDetails.PharmacyID):
                                    SmallestPrice = AllVendorData[i].Price
                                    break
                            for i in AllVendorData:
                                if(i.Price < SmallestPrice and i.PharmacyID != VendorDetails.PharmacyID):
                                    SmallestPrice = i.Price
                            ProductDetails.Price = SmallestPrice
                            ProductDetails.put()
                    else:
                        ProductDetails.key.delete()
                    VendorProductsDBConnect.key.delete()
                    self.redirect('/VendorHomePage?vendorEmail='+vendorEmail+'&notification=ProductDeletedSuccessfully')

        template_values = {
            'Mode' : Mode,
            'ModeURL' : ModeURL,
            'ImageCount' : ImageCount,
            'Option' : Option,
            'ProductDetails' : ProductDetails,
            'VendorDetails' : VendorDetails,
            'VendorProductDetails' : VendorProductDetails,
        }

        template = JINJA_ENVIRONMENT.get_template('VendorProductDetails.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/VendorProductDetails',VendorProductDetails),
], debug=True)
