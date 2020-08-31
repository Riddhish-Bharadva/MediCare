import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url
from EmailModule import SendEmail
from UsersDB import UsersDB
from VendorsDB import VendorsDB
from OrdersDB import OrdersDB
from ProductsDB import ProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class ViewOrderDetails(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        SignInAs = self.request.get('SignInAs')
        OrderID = self.request.get('OrderID')
        notification = self.request.get('notification')
        SignInStatus = ""
        UserDetails = None
        VendorDetails = None
        ProductsCount = 0
        Category = []
        OrderDetails = []
        ProductDetails = []
        UserData = []
        ProductStatus = []
        Button = self.request.get("Button")
        ImageUploadURL = ""
        SubTotalPrice = 0.0

        if(SignInAs == "User"):
            userEmail = self.request.get('userEmail')
            if(userEmail != ""):
                UserDetails = ndb.Key("UsersDB",userEmail).get()
                if(UserDetails != None and UserDetails.IsActive == 0):
                    self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
                elif(UserDetails == None):
                    self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
                elif(UserDetails != None and UserDetails.IsActive == 1):
                    SignInStatus = "SignOut"
                    OrderData = OrdersDB.query(OrdersDB.OrderID == OrderID, OrdersDB.userEmail == UserDetails.user_Email).fetch()
                    if(OrderData == []):
                        self.redirect("/")
                    else:
                        OrderDetails = OrderData[0]
                        PharmacyID = [OrderData[0].PharmacyID]
                        for i in OrderData[0].ProductID:
                            if(OrderData[0].OrderStatus == "Completed"):
                                ProductStatus.append("Delivered")
                            else:
                                ProductStatus.append("Order In Progress")
                        for i in range(1,len(OrderData)):
                            for j in range(0,len(OrderData[i].ProductID)):
                                if(OrderData[i].OrderStatus == "Completed"):
                                    ProductStatus.append("Delivered")
                                else:
                                    ProductStatus.append("Order In Progress")
                                PharmacyID.append(OrderData[i].PharmacyID)
                                OrderDetails.ProductID.append(OrderData[i].ProductID[j])
                                OrderDetails.Price.append(OrderData[i].Price[j])
                                OrderDetails.Quantity.append(OrderData[i].Quantity[j])
                        for i in range(0,len(OrderDetails.ProductID)):
                            ProductData = ndb.Key("ProductsDB",OrderDetails.ProductID[i]).get()
                            if(ProductData != None):
                                ProductDetails.append(ProductData)
                    if(OrderDetails.PrescriptionRequired == 0):
                        ProductsCount = len(OrderDetails.ProductID)
                    else:
                        ProductsCount = len(OrderDetails.ProductName)
                    if(OrderDetails.OrderSubStatus == "ReuploadPrescription"):
                        ImageUploadURL = blobstore.create_upload_url("/ViewOrderDetails")
                    for i in range(0,len(OrderDetails.Price)):
                        SubTotalPrice = SubTotalPrice + OrderDetails.Quantity[i] * OrderDetails.Price[i]
                    OrderDetails.OrderTotal = SubTotalPrice + OrderDetails.DeliveryCharge + OrderDetails.ServiceCharge
                    OrderDetails.put()
                    if(Button == "RemoveProduct"):
                        index = self.request.get("index")
                        for i in range(0,len(OrderDetails.ProductName)):
                            if(i == int(index)):
                                del OrderDetails.ProductName[int(index)]
                                del OrderDetails.Quantity[int(index)]
                                del OrderDetails.Price[int(index)]
                                break
                        OrderDetails.put()
                        if(len(OrderDetails.ProductName) == 0):
                            OrderDetails.key.delete()
                            self.redirect('/MyOrders?userEmail='+userEmail)
                        else:
                            self.redirect('/ViewOrderDetails?SignInAs=User&userEmail='+UserDetails.user_Email+'&OrderID='+OrderDetails.OrderID)
                    OrderDetails.PharmacyID = ""
            else:
                self.redirect('/UserSignIn')
        elif(SignInAs == "Vendor"):
            vendorEmail = self.request.get('vendorEmail')
            if(vendorEmail != ""):
                VendorDetails = ndb.Key('VendorsDB',vendorEmail).get()
                if(VendorDetails != None and VendorDetails.IsActive == 0):
                    self.redirect('/VendorSignIn?notification=VendorInActive')
                elif(VendorDetails == None):
                    self.redirect('/VendorSignIn?notification=EmailIdNotRegistered')
                elif(VendorDetails != None and VendorDetails.IsActive == 1):
                    SignInStatus = "SignOut"
                    OrderData = OrdersDB.query(OrdersDB.OrderID == OrderID, OrdersDB.PharmacyID == VendorDetails.PharmacyID).fetch()
                    if(OrderData == []):
                        self.redirect("/")
                    else:
                        OrderDetails = OrderData[0]
                        if(OrderDetails.PrescriptionRequired == 0):
                            for i in range(0,len(OrderDetails.ProductID)):
                                ProductData = ndb.Key("ProductsDB",OrderDetails.ProductID[i]).get()
                                if(ProductData != None):
                                    ProductDetails.append(ProductData)
                            ProductsCount = len(OrderDetails.ProductID)
                        else:
                            ProductsCount = len(OrderDetails.ProductName)
                    UserData = ndb.Key("UsersDB", OrderData[0].userEmail).get()
                    if(Button == "RemoveProduct"):
                        index = self.request.get("index")
                        for i in range(0,len(OrderDetails.ProductName)):
                            if(i == int(index)):
                                del OrderDetails.ProductName[int(index)]
                                del OrderDetails.Quantity[int(index)]
                                del OrderDetails.Price[int(index)]
                                break
                        OrderDetails.put()
                        self.redirect('/ViewOrderDetails?SignInAs=Vendor&vendorEmail='+VendorDetails.Email+'&OrderID='+OrderDetails.OrderID)
            else:
                self.redirect('/VendorSignIn')
        else:
            self.redirect('/')

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
            'VendorDetails' : VendorDetails,
            'UserData' : UserData,
            'Category' : Category,
            'notification' : notification,
            'OrderDetails' : OrderDetails,
            'ProductDetails' : ProductDetails,
            'ProductsCount' : ProductsCount,
            'ProductStatus' : ProductStatus,
            'ImageUploadURL' : ImageUploadURL,
            'SubTotalPrice' : SubTotalPrice,
        }

        template = JINJA_ENVIRONMENT.get_template('ViewOrderDetails.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        SignInAs = self.request.get("SignInAs")
        userEmail = self.request.get("userEmail")
        vendorEmail = self.request.get("vendorEmail")
        if(SignInAs == "Vendor" and vendorEmail != ""):
            VendorDetails = ndb.Key('VendorsDB',vendorEmail).get()
            if(VendorDetails != None and VendorDetails.IsActive == 0):
                self.redirect('/VendorSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(VendorDetails == None):
                self.redirect('/VendorSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(VendorDetails != None and VendorDetails.IsActive == 1):
                SignInStatus = "SignOut"
                Button = self.request.get('Button')
                PharmacyID = self.request.get('PharmacyID')
                OrderID = self.request.get('OrderID')
                userData = self.request.get('userData')
                OrderDetails = OrdersDB.query(OrdersDB.OrderID == OrderID, OrdersDB.PharmacyID == PharmacyID, OrdersDB.userEmail == userData).get()
                if(OrderDetails != [] and Button == "MarkPacking"):
                    OrderDetails.OrderSubStatus = "OrderPacking"
                    OrderDetails.StatusChangedBy = VendorDetails.Email
                    OrderDetails.put()
                    self.redirect('/VendorOrders?vendorEmail='+VendorDetails.Email)
                elif(OrderDetails != [] and Button == "OutForDelivery" and OrderDetails.OrderType == "Delivery"):
                    OrderDetails.OrderSubStatus = "OutForDelivery"
                    OrderDetails.StatusChangedBy = VendorDetails.Email
                    OrderDetails.put()
                    self.redirect('/VendorOrders?vendorEmail='+VendorDetails.Email)
                elif(OrderDetails != [] and Button == "ReadyForCollection" and OrderDetails.OrderType == "Collection"):
                    OrderDetails.OrderSubStatus = "ReadyForCollection"
                    OrderDetails.StatusChangedBy = VendorDetails.Email
                    OrderDetails.put()
                    self.redirect('/VendorOrders?vendorEmail='+VendorDetails.Email)
                elif(OrderDetails != [] and (Button == "MarkDelivered" or Button == "MarkCollected")):
                    OrderDetails.OrderSubStatus = "OrderComplete"
                    OrderDetails.OrderStatus = "Completed"
                    OrderDetails.StatusChangedBy = VendorDetails.Email
                    OrderDetails.put()
                    SendEmail(OrderDetails.userEmail,"Your order has been successfully completed","""
Dear MediCare User,

This is an automated email confirmation sent to you in regards of your placed order at MediCare.

Your order ("""+ OrderDetails.OrderID +""") has been successfully complete. You can view the same in "My Orders" tab after logging into your MediCare account.
In case you are able to view same order id in Active Order, this may be due to the fact few items from the whole order are still yet to be delivered.

Thanks & regards,
MediCare Team.
                    """)
                    self.redirect('/VendorOrders?vendorEmail='+VendorDetails.Email)
                elif(OrderDetails != [] and Button == "AddProduct"):
                    ProductName = []
                    Quantity = []
                    Price = []
                    for i in range(0,len(OrderDetails.ProductName)):
                        Key = "ProductName"+str(i)
                        PN = self.request.get(Key)
                        if(PN not in ProductName):
                            ProductName.append(PN)
                            Key1 = "Quantity"+str(i)
                            Q = self.request.get(Key1)
                            Quantity.append(int(Q))
                            Key2 = "Price"+str(i)
                            P = self.request.get(Key2)
                            Price.append(float(P))
                    ProductName.append("New")
                    Quantity.append(0)
                    Price.append(0)
                    OrderDetails.ProductName = ProductName
                    OrderDetails.Quantity = Quantity
                    OrderDetails.Price = Price
                    OrderDetails.put()
                    self.redirect('/ViewOrderDetails?SignInAs=Vendor&vendorEmail='+VendorDetails.Email+'&OrderID='+OrderDetails.OrderID)
                elif(OrderDetails != [] and Button == "SubmitForBilling"):
                    VendorComments = self.request.get("VendorComments")
                    ProductName = []
                    Quantity = []
                    Price = []
                    for i in range(0,len(OrderDetails.ProductName)):
                        Key = "ProductName"+str(i)
                        PN = self.request.get(Key)
                        if(PN not in ProductName):
                            ProductName.append(PN)
                            Key1 = "Quantity"+str(i)
                            Q = self.request.get(Key1)
                            Quantity.append(int(Q))
                            Key2 = "Price"+str(i)
                            P = self.request.get(Key2)
                            Price.append(float(P))
                    OrderDetails.ProductName = ProductName
                    OrderDetails.Quantity = Quantity
                    OrderDetails.Price = Price
                    OrderDetails.VendorComments = VendorComments
                    if(len(OrderDetails.ProductName) != 0):
                        OrderDetails.OrderSubStatus = "BillingRequired"
                    OrderDetails.put()
                    SendEmail(OrderDetails.userEmail,"Your order uploaded with Prescreption requires billing","""
Dear """+OrderDetails.userEmail+""",

This is an automated email confirmation sent to you in regards of your placed order at MediCare.

Your order ("""+ OrderDetails.OrderID +""") requires payment to proceed further.
You can make payment by loging into your MediCare account and by viewing the order number.

Thanks & regards,
MediCare Team.
                    """)
                    self.redirect('/ViewOrderDetails?SignInAs=Vendor&vendorEmail='+VendorDetails.Email+'&OrderID='+OrderDetails.OrderID)
                elif(OrderDetails != [] and Button == "ReuploadPrescription"):
                    OrderDetails.OrderSubStatus = "ReuploadPrescription"
                    OrderDetails.put()
                    self.redirect('/ViewOrderDetails?SignInAs=Vendor&vendorEmail='+VendorDetails.Email+'&OrderID='+OrderDetails.OrderID)
        elif(SignInAs == "User" and userEmail != ""):
            Button = self.request.get('Button')
            OrderID = self.request.get('OrderID')
            OrderDetails = OrdersDB.query(OrdersDB.OrderID == OrderID, OrdersDB.userEmail == userEmail, OrdersDB.PrescriptionRequired == 1).get()
            if(OrderDetails != [] and Button == "Upload"):
                PrescriptionImage = self.get_uploads()[0]
                PrescriptionImage = get_serving_url(PrescriptionImage.key())
                OrderDetails.PrescriptionImage = PrescriptionImage
                OrderDetails.OrderSubStatus = "OrderPlaced"
                OrderDetails.put()
                self.redirect('/ViewOrderDetails?SignInAs=User&userEmail='+userEmail+'&OrderID='+OrderDetails.OrderID)
            elif(OrderDetails != [] and Button == "ProceedToBilling"):
                OrderDetails.OrderSubStatus = "ProceedToBilling"
                OrderDetails.put()
                self.redirect('/ViewOrderDetails?SignInAs=User&userEmail='+userEmail+'&OrderID='+OrderDetails.OrderID)
            elif(OrderDetails != [] and Button == "Pay"):
                OrderDetails.OrderSubStatus = "PaymentSuccessful"
                OrderDetails.put()
                self.redirect('/ViewOrderDetails?SignInAs=User&userEmail='+userEmail+'&OrderID='+OrderDetails.OrderID)
        else:
            self.redirect('/VendorSignIn')

app = webapp2.WSGIApplication([
    ('/ViewOrderDetails',ViewOrderDetails),
], debug=True)
