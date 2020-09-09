import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from EmailModule import SendEmail
from UsersDB import UsersDB
from OrdersDB import OrdersDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class WebView(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        SignInAs = self.request.get("SignInAs")
        Function = self.request.get("Function")
        userEmail = self.request.get('userEmail')
        OrderID = self.request.get('OrderID')
        notification = self.request.get('notification')
        SubTotalPrice = 0.0
        DC = 0.0
        UserDetails = None
        OrderDetails = None
        ReUploadPrescription = 0
        PaymentRequired = 0

        if(Function == "ShoppingCart"):
            abc = 0
        elif(Function == "MakePayment"):
            if(userEmail != ""):
                UserDetails = ndb.Key("UsersDB",userEmail).get()
                if(UserDetails != None and UserDetails.IsActive == 1):
                    OrderData = OrdersDB.query(OrdersDB.OrderID == OrderID).fetch()
                    if(OrderData == []):
                        notification = "NoDataInOrder"
                    else:
                        OrderDetails = OrderData[0]
                        DC = DC + OrderData[0].DeliveryCharge
                        for i in range(0,len(OrderDetails.ProductID)):
                            SubTotalPrice = SubTotalPrice + (OrderDetails.Quantity[i] * OrderDetails.Price[i])
                        if(OrderData[0].OrderSubStatus == "ReUploadPrescription"):
                            ReUploadPrescription = 1
                            PaymentRequired = 0
                        elif(OrderData[0].OrderSubStatus == "PaymentRequired"):
                            ReUploadPrescription = 0
                            PaymentRequired = 1
                        elif(OrderData[0].OrderSubStatus == "CancelledByVendor" and len(OrderData) > 1):
                            ReUploadPrescription = 0
                            PaymentRequired = 1
                        else:
                            ReUploadPrescription = 0
                            PaymentRequired = 0
                        for i in range(1,len(OrderData)):
                            DC = DC + OrderData[i].DeliveryCharge
                            if(OrderDetails.VendorComments != None and OrderData[i].VendorComments != None):
                                OrderDetails.VendorComments = OrderDetails.VendorComments + OrderData[i].VendorComments
                            else:
                                OrderDetails.VendorComments = OrderData[i].VendorComments
                            if(OrderData[i].OrderSubStatus != "CancelledByVendor" and OrderData[i].OrderSubStatus != "CancelledByCustomer" and OrderDetails.ServiceCharge == 0.0):
                                if(OrderData[i].OrderType != "Collection"):
                                    OrderDetails.ServiceCharge = 1.0
                                OrderDetails.OrderTotal = OrderDetails.OrderTotal + OrderData[i].OrderTotal
                            elif(OrderData[i].OrderSubStatus != "CancelledByVendor" and OrderData[i].OrderSubStatus != "CancelledByCustomer" and OrderDetails.ServiceCharge != 0.0):
                                OrderDetails.OrderTotal = OrderDetails.OrderTotal + OrderData[i].OrderTotal - OrderData[i].ServiceCharge
                            OrderDetails.DeliveryCharge = OrderDetails.DeliveryCharge + OrderData[i].DeliveryCharge
                            if(OrderDetails.PrescriptionRequired == 0):
                                OrderDetails.PrescriptionRequired = OrderData[i].PrescriptionRequired
                                if(OrderDetails.PrescriptionRequired == 1):
                                    OrderDetails.PrescriptionImage = OrderData[i].PrescriptionImage
                            for j in range(0,len(OrderData[i].ProductID)):
                                OrderDetails.ProductID.append(OrderData[i].ProductID[j])
                                OrderDetails.Quantity.append(OrderData[i].Quantity[j])
                                OrderDetails.Price.append(OrderData[i].Price[j])
                                SubTotalPrice = SubTotalPrice + (OrderData[i].Quantity[j] * OrderData[i].Price[j])
                            if(OrderData[i].OrderSubStatus == "ReUploadPrescription"):
                                ReUploadPrescription = 1
                                PaymentRequired = 0
                            elif(OrderData[i].OrderSubStatus == "CancelledByVendor" and PaymentRequired == 1):
                                ReUploadPrescription = 0
                                PaymentRequired = 1
                            elif(OrderData[i].OrderSubStatus == "PaymentRequired" and PaymentRequired == 1):
                                ReUploadPrescription = 0
                                PaymentRequired = 1
                            else:
                                PaymentRequired = 0
            else:
                notification = "UserNotLoggedIn"

        template_values = {
            "notification" : notification,
            "SignInAs" : SignInAs,
            "userEmail" : userEmail,
            "UserDetails" : UserDetails,
            "OrderDetails" : OrderDetails,
            "Function" : Function,
            "PaymentRequired" : PaymentRequired,
            "SubTotalPrice" : SubTotalPrice,
            "ReUploadPrescription" : ReUploadPrescription,
        }

        template = JINJA_ENVIRONMENT.get_template('WebView.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        SignInAs = self.request.get('SignInAs')
        Button = self.request.get('Button')
        OrderID = self.request.get('OrderID')
        Function = self.request.get('Function')
        userEmail = self.request.get('userEmail')
        OrderDetails = OrdersDB.query(OrdersDB.OrderID == OrderID, OrdersDB.userEmail == userEmail).fetch()
        for i in range(0,len(OrderDetails)):
            if(OrderDetails[i].OrderStatus != "Completed"):
                OrderDetails[i].OrderSubStatus = "PaymentSuccessful"
                OrderDetails[i].put()
                self.redirect("/WebView?SignInAs="+SignInAs+"&Function="+Function+"&userEmail="+userEmail+"&OrderID="+OrderID+"&notification=PaymentSuccessful")

app = webapp2.WSGIApplication([
    ('/WebView',WebView),
], debug=True)
