import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from CartCount import getCartCount
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
        CompletedOrderDetails = []

        if(userEmail != ""):
            UserDetails = ndb.Key('UsersDB',userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails != None and UserDetails.IsActive == 1):
                SignInStatus = "SignOut"
                CartCount = getCartCount(self,userEmail)
                OrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail, OrdersDB.OrderStatus == "Active").fetch()
                if(OrderDetails != []):
                    UON = []
                    for i in range(0,len(OrderDetails)):
                        if(OrderDetails[i].OrderID not in UON):
                            UON.append(OrderDetails[i].OrderID)
                    for i in range(0,len(UON)):
                        OrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail, OrdersDB.OrderStatus == "Active", OrdersDB.OrderID == UON[i]).fetch()
                        ActiveOrderDetails.append(OrderDetails[0])
                        if(len(OrderDetails) > 1):
                            for j in range(1,len(OrderDetails)):
                                if(ActiveOrderDetails[i].OrderSubStatus != "Reviewing" and OrderDetails[j].OrderSubStatus == "Reviewing"):
                                    ActiveOrderDetails[i].OrderSubStatus = OrderDetails[j].OrderSubStatus
                OrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail, OrdersDB.OrderStatus == "Completed").fetch()
                if(OrderDetails != []):
                    UON = []
                    for i in range(0,len(OrderDetails)):
                        if(OrderDetails[i].OrderID not in UON):
                            UON.append(OrderDetails[i].OrderID)
                    for i in range(0,len(UON)):
                        OrderDetails = OrdersDB.query(OrdersDB.userEmail == userEmail, OrdersDB.OrderID == UON[i]).fetch()
                        if(len(OrderDetails)>1):
                            OSS = OrderDetails[0].OrderStatus
                            for j in range(1,len(OrderDetails)):
                                if(OSS != OrderDetails[j].OrderStatus):
                                    OSS = OrderDetails[j]
                            if(OSS == "Completed"):
                                CompletedOrderDetails.append(OrderDetails[0])
                        else:
                            if(OrderDetails[0].OrderStatus == "Completed"):
                                CompletedOrderDetails.append(OrderDetails[0])
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
            'CartCount' : CartCount,
            'ActiveOrderDetails' : ActiveOrderDetails,
            'CompletedOrderDetails' : CompletedOrderDetails,
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
                self.redirect('/?userEmail='+userEmail)
        else:
            self.redirect('/UserSignIn')

app = webapp2.WSGIApplication([
    ('/MyOrders',MyOrders),
], debug=True)
