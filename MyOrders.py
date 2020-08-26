import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from UsersDB import UsersDB
from OrdersDB import OrdersDB
from ProductsDB import ProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class MyOrders(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get('userEmail')
        notification = self.request.get('notification')
        SignInStatus = ""
        UserDetails = None
        Category = []
        ActiveOrderDetails = []
        Unique_AOD = []
        U_AOD_PharmacyID = []
        CompletedOrderDetails = []
        Unique_COD = []
        U_COD_PharmacyID = []
        Unique_AOD_Length = 0
        Unique_COD_Length = 0

        if(userEmail != ""):
            UserDetails = ndb.Key('UsersDB',userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails != None and UserDetails.IsActive == 1):
                SignInStatus = "SignOut"
                ActiveOrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail and OrdersDB.OrderStatus == "Active").fetch()
                if(ActiveOrderDetails != []):
                    Unique_OrderNumber = []
                    for i in range(0,len(ActiveOrderDetails)):
                        if(ActiveOrderDetails[i].OrderID not in Unique_OrderNumber):
                            Unique_OrderNumber.append(ActiveOrderDetails[i].OrderID)
                    for i in range(0,len(Unique_OrderNumber)):
                        ActiveOrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail and OrdersDB.OrderStatus == "Active" and OrdersDB.OrderID == Unique_OrderNumber[i]).fetch()
                        Unique_AOD.append(ActiveOrderDetails[0])
                        PharmacyID = [Unique_AOD[i].PharmacyID]
                        for k in range(1,len(ActiveOrderDetails)):
                            for j in range(0,len(ActiveOrderDetails[k].ProductID)):
                                PharmacyID.append(ActiveOrderDetails[k].PharmacyID)
                                Unique_AOD[i].ProductID.append(ActiveOrderDetails[k].ProductID[j])
                                Unique_AOD[i].Price.append(ActiveOrderDetails[k].Price[j])
                                Unique_AOD[i].Quantity.append(ActiveOrderDetails[k].Quantity[j])
                        Unique_AOD[i].PharmacyID = ""
                        U_AOD_PharmacyID = PharmacyID
                        Unique_AOD_Length = len(Unique_AOD)
                CompletedOrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail and OrdersDB.OrderStatus == "Completed").fetch()
                if(CompletedOrderDetails != []):
                    Unique_OrderNumber = []
                    for i in range(0,len(CompletedOrderDetails)):
                        if(CompletedOrderDetails[i].OrderID not in Unique_OrderNumber):
                            Unique_OrderNumber.append(CompletedOrderDetails[i].OrderID)
                    for i in range(0,len(Unique_OrderNumber)):
                        CompletedOrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail and OrdersDB.OrderStatus == "Completed" and OrdersDB.OrderID == Unique_OrderNumber[i]).fetch()
                        Unique_COD.append(CompletedOrderDetails[0])
                        PharmacyID = [Unique_COD[i].PharmacyID]
                        for k in range(1,len(CompletedOrderDetails)):
                            for j in range(0,len(CompletedOrderDetails[k].ProductID)):
                                PharmacyID.append(CompletedOrderDetails[k].PharmacyID)
                                Unique_COD[i].ProductID.append(CompletedOrderDetails[k].ProductID[j])
                                Unique_COD[i].Price.append(CompletedOrderDetails[k].Price[j])
                                Unique_COD[i].Quantity.append(CompletedOrderDetails[k].Quantity[j])
                        Unique_COD[i].PharmacyID = ""
                        U_COD_PharmacyID = PharmacyID
                        Unique_COD_Length = len(Unique_COD)
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

        template_values = {
            'SignInStatus' : SignInStatus,
            'UserDetails' : UserDetails,
            'Category' : Category,
            'notification' : notification,
            'Unique_AOD' : Unique_AOD,
            'Unique_COD' : Unique_COD,
            'Unique_AOD_Length' : Unique_AOD_Length,
            'Unique_COD_Length' : Unique_COD_Length,
            'U_AOD_PharmacyID' : U_AOD_PharmacyID,
            'U_COD_PharmacyID' : U_COD_PharmacyID,
        }

        template = JINJA_ENVIRONMENT.get_template('MyOrders.html')
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
            elif(UserDetails != None and UserDetails.IsActive == 1):
                SignInStatus = "SignOut"
        else:
            self.redirect('/UserSignIn')

app = webapp2.WSGIApplication([
    ('/MyOrders',MyOrders),
], debug=True)
