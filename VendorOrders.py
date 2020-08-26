import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from VendorsDB import VendorsDB
from OrdersDB import OrdersDB
from ProductsDB import ProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class VendorOrders(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get('vendorEmail')
        notification = self.request.get('notification')
        SignInStatus = ""
        VendorDetails = None
        Category = []
        ActiveOrderDetails = []
        AOD_Length = 0
        CompletedOrderDetails = []
        COD_Length = 0

        if(vendorEmail != ""):
            VendorDetails = ndb.Key('VendorsDB',vendorEmail).get()
            if(VendorDetails != None and VendorDetails.IsActive == 0):
                self.redirect('/VendorSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(VendorDetails == None):
                self.redirect('/VendorSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(VendorDetails != None and VendorDetails.IsActive == 1):
                SignInStatus = "SignOut"
                ActiveOrderDetails = OrdersDB.query(OrdersDB.PharmacyID == VendorDetails.PharmacyID, OrdersDB.OrderStatus == "Active").fetch()
                AOD_Length = len(ActiveOrderDetails)
                CompletedOrderDetails = OrdersDB.query(OrdersDB.PharmacyID == VendorDetails.PharmacyID, OrdersDB.OrderStatus == "Completed").fetch()
                COD_Length = len(CompletedOrderDetails)
        else:
            self.redirect('/VendorSignIn')

        ProductsData = ProductsDB.query().fetch()
        if(ProductsData == []):
            ProductsData = None
        else:
            for i in range(0,len(ProductsData)):
                if(ProductsData[i].Category not in Category):
                    Category.append(ProductsData[i].Category)
        Category.sort()

        template_values = {
            'SignInStatus' : SignInStatus,
            'VendorDetails' : VendorDetails,
            'Category' : Category,
            'notification' : notification,
            'ActiveOrderDetails' : ActiveOrderDetails,
            'AOD_Length' : AOD_Length,
            'CompletedOrderDetails' : CompletedOrderDetails,
            'COD_Length' : COD_Length,
        }

        template = JINJA_ENVIRONMENT.get_template('VendorOrders.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get("vendorEmail")
        if(vendorEmail != ""):
            VendorDetails = ndb.Key('VendorsDB',vendorEmail).get()
            if(VendorDetails != None and VendorDetails.IsActive == 0):
                self.redirect('/VendorSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(VendorDetails == None):
                self.redirect('/VendorSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(VendorDetails != None and VendorDetails.IsActive == 1):
                SignInStatus = "SignOut"
        else:
            self.redirect('/VendorSignIn')

app = webapp2.WSGIApplication([
    ('/VendorOrders',VendorOrders),
], debug=True)
