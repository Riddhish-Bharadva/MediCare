import webapp2
import jinja2
import os
from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url
from ProductsDB import ProductsDB
from VendorsDB import VendorsDB
from VendorProductsDB import VendorProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class AddProducts(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get('vendorEmail')
        Query = self.request.get('Query')
        notification = self.request.get('notification')
        Category = []
        CategoryCount = 0
        SubCategory = []
        SubCategoryCount = 0
        ImageUploadURL = "/AddProducts?vendorEmail="+vendorEmail
        QueryProducts = []
        ProductsData = None

        if(vendorEmail != None):
            VendorDetails = ndb.Key("VendorsDB",vendorEmail).get()
            if(VendorDetails == None):
                self.redirect('/VendorSignIn')
            else:
                if(Query == "True"):
                    QueryProductName = self.request.get('SearchBar')
                    AllProducts = ProductsDB.query().fetch()
                    if(AllProducts != None):
                        for i in range(0,len(AllProducts)):
                            ProdName = AllProducts[i].ProductName.lower()
                            ProdDescription = AllProducts[i].Description.lower()
                            ProdIngredients = AllProducts[i].Ingredients.lower()
                            if(ProdName.find(QueryProductName.lower()) != -1):
                                QueryProducts.append(AllProducts[i])
                            elif(ProdDescription.find(QueryProductName.lower()) != -1):
                                QueryProducts.append(AllProducts[i])
                            elif(ProdIngredients.find(QueryProductName.lower()) != -1):
                                QueryProducts.append(AllProducts[i])
                else:
                    ImageUploadURL = blobstore.create_upload_url("/AddProducts")

                ProductsData = ProductsDB.query().fetch()
                if(ProductsData == []):
                    ProductsData = None
                else:
                    for i in range(0,len(ProductsData)):
                        if(ProductsData[i].Category not in Category):
                            Category.append(ProductsData[i].Category)
                            CategoryCount = CategoryCount + 1
                        if(ProductsData[i].SubCategory not in SubCategory):
                            SubCategory.append(ProductsData[i].SubCategory)
                            SubCategoryCount = SubCategoryCount + 1
        else:
            self.redirect('/VendorSignIn')

        template_values = {
            'VendorDetails' : VendorDetails,
            'Category' : Category,
            'CategoryCount' : CategoryCount,
            'SubCategory' : SubCategory,
            'SubCategoryCount' : SubCategoryCount,
            'ProductsData' : ProductsData,
            'ImageUploadURL' : ImageUploadURL,
            'notification' : notification,
            'QueryProducts' : QueryProducts,
        }

        template = JINJA_ENVIRONMENT.get_template('AddProducts.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        vendorEmail = self.request.get('vendorEmail')
        if(vendorEmail == ""):
            self.redirect('/VendorSignIn')
        else:
            VendorDetails = ndb.Key("VendorsDB",vendorEmail).get()
            Option = self.request.get('Option')
            if(Option == "1"):
                ProductID = datetime.now().strftime("%Y%m%d%H%M%S")
                AddedOn = datetime.now().strftime("%d/%m/%Y at %H:%M:%S")
                LastModifiedOn = AddedOn
                ProductName = self.request.get('ProductName')
                Description = self.request.get('Description')
                Ingredients = self.request.get('Ingredients')
                Dosage = self.request.get('Dosage')
                ProductLife = self.request.get('ProductLife')
                Category = self.request.get('Category')
                if(Category == "Select Category"):
                    Category = self.request.get('NewCategory')
                if(Category == ""):
                    Category = "Medicine"
                SubCategory = self.request.get('SubCategory')
                if(SubCategory == "Select Sub Category"):
                    SubCategory = self.request.get('NewSubCategory')
                if(SubCategory == ""):
                    SubCategory = self.request.get('NewSubCategory')
                if(SubCategory == "Select Sub Category"):
                    SubCategory = "General"
                Quantity = self.request.get('Quantity')
                Price = self.request.get('Price')
                Images = self.get_uploads()

                ProductsDBConnect = ProductsDB.query(ProductsDB.ProductName == ProductName).get()
                if(ProductsDBConnect == None or ProductsDBConnect == []):
                    ProductsDBConnect = ProductsDB(id = ProductID)
                    ProductsDBConnect.ProductID = ProductID
                    ProductsDBConnect.ProductName = ProductName
                    ProductsDBConnect.Description = Description
                    ProductsDBConnect.Ingredients = Ingredients
                    ProductsDBConnect.Dosage = Dosage
                    ProductsDBConnect.ProductLife = ProductLife
                    ProductsDBConnect.Category = Category
                    ProductsDBConnect.SubCategory = SubCategory
                    ProductsDBConnect.Quantity = int(Quantity)
                    ProductsDBConnect.Price = float(Price)
                    for i in Images:
                        ProductsDBConnect.Images.append(get_serving_url(i.key()))
                    ProductsDBConnect.StockedIn.append(VendorDetails.PharmacyID)

                    VendorProductsDBConnect = VendorProductsDB(id=VendorDetails.PharmacyID+ProductID)
                    VendorProductsDBConnect.PharmacyID = VendorDetails.PharmacyID
                    VendorProductsDBConnect.ProductID = ProductID
                    VendorProductsDBConnect.Quantity = int(Quantity)
                    VendorProductsDBConnect.Price = float(Price)
                    VendorProductsDBConnect.AddedOn = AddedOn
                    VendorProductsDBConnect.AddedBy = vendorEmail
                    VendorProductsDBConnect.LastModifiedOn = AddedOn
                    VendorProductsDBConnect.LastModifiedBy = vendorEmail
                    ProductsDBConnect.put()
                    VendorProductsDBConnect.put()
                    self.redirect('/VendorHomePage?vendorEmail='+vendorEmail+'&notification=ProductRegisteredSuccessfully')
                else:
                    self.redirect('/AddProducts?vendorEmail='+vendorEmail+'&notification=ProductAlreadyRegistered')

            elif(Option == "2"):
                ProductID = self.request.get('ProductID')
                Quantity = self.request.get('Quantity')
                Price = self.request.get('Price')
                LastModifiedOn = datetime.now().strftime("%d/%m/%Y at %H:%M:%S")

                ProductsDBConnect = ndb.Key("ProductsDB",ProductID).get()
                ProductsDBConnect.Quantity = ProductsDBConnect.Quantity + int(Quantity)
                if(len(ProductsDBConnect.StockedIn) == 1 and VendorDetails.PharmacyID == ProductsDBConnect.StockedIn[0]):
                    ProductsDBConnect.Price = float(Price)
                else:
                    if(ProductsDBConnect.Price > float(Price)):
                        ProductsDBConnect.Price = float(Price)
                if(VendorDetails.PharmacyID not in ProductsDBConnect.StockedIn):
                    ProductsDBConnect.StockedIn.append(VendorDetails.PharmacyID)

                VendorProductsDBConnect = ndb.Key("VendorProductsDB",VendorDetails.PharmacyID+ProductID).get()
                if(VendorProductsDBConnect == None):
                    VendorProductsDBConnect = VendorProductsDB(id=VendorDetails.PharmacyID+ProductID)
                    VendorProductsDBConnect.PharmacyID = VendorDetails.PharmacyID
                    VendorProductsDBConnect.ProductID = ProductID
                    VendorProductsDBConnect.Quantity = int(Quantity)
                    VendorProductsDBConnect.Price = float(Price)
                    VendorProductsDBConnect.AddedOn = LastModifiedOn
                    VendorProductsDBConnect.AddedBy = vendorEmail
                    VendorProductsDBConnect.LastModifiedOn = LastModifiedOn
                    VendorProductsDBConnect.LastModifiedBy = vendorEmail
                else:
                    VendorProductsDBConnect.Quantity = VendorProductsDBConnect.Quantity + int(Quantity)
                    VendorProductsDBConnect.Price = float(Price)
                    VendorProductsDBConnect.LastModifiedOn = LastModifiedOn
                    VendorProductsDBConnect.LastModifiedBy = vendorEmail
                ProductsDBConnect.put()
                VendorProductsDBConnect.put()
                self.redirect('/VendorHomePage?vendorEmail='+vendorEmail+'&notification=ProductRegisteredSuccessfully')

app = webapp2.WSGIApplication([
    ('/AddProducts',AddProducts),
], debug=True)
