import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url
from CartCount import getCartCount
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
        Button = self.request.get("Button")
        SignInStatus = ""
        Category = []
        UserDetails = None
        VendorDetails = None
        OrderDetails = []
        ProductDetails = []
        UserData = []
        PharmacyID = []
        PharmacyDetails = []
        PPID = []
        ProductStatus = []
        ProductsCount = 0
        ReUploadPrescription = 0
        PaymentRequired = 0
        ImageUploadURL = ""
        SubTotalPrice = 0.0
        DC = 0.0
        CartCount = 0

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
                    CartCount = getCartCount(self,userEmail)
                    OrderData = OrdersDB.query(OrdersDB.OrderID == OrderID).fetch()
                    if(OrderData == []):
                        self.redirect("/VendorOrders?vendorEmail="+vendorEmail)
                    else:
                        OrderDetails = OrderData[0]
                        DC = DC + OrderData[0].DeliveryCharge
                        PharmacyID.append(OrderData[0].PharmacyID)
                        for i in range(0,len(OrderDetails.ProductID)):
                            PPID.append(OrderData[0].PharmacyID)
                            ProductStatus.append(OrderData[0].OrderSubStatus)
                            SubTotalPrice = SubTotalPrice + (OrderDetails.Quantity[i] * OrderDetails.Price[i])
                            ProductData = ndb.Key("ProductsDB",OrderDetails.ProductID[i]).get()
                            if(ProductData != None):
                                ProductDetails.append(ProductData)
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
                            if(OrderData[i].PharmacyID not in PharmacyID):
                                PharmacyID.append(OrderData[i].PharmacyID)
                            if(OrderData[i].OrderSubStatus != "CancelledByVendor" and OrderData[i].OrderSubStatus != "CancelledByCustomer"):
                                OrderDetails.OrderTotal = OrderDetails.OrderTotal + OrderData[i].OrderTotal - OrderData[i].ServiceCharge
                            OrderDetails.DeliveryCharge = OrderDetails.DeliveryCharge + OrderData[i].DeliveryCharge
                            if(OrderDetails.PrescriptionRequired == 0):
                                OrderDetails.PrescriptionRequired = OrderData[i].PrescriptionRequired
                                if(OrderDetails.PrescriptionRequired == 1):
                                    OrderDetails.PrescriptionImage = OrderData[i].PrescriptionImage
                            for j in range(0,len(OrderData[i].ProductID)):
                                PPID.append(OrderData[i].PharmacyID)
                                OrderDetails.ProductID.append(OrderData[i].ProductID[j])
                                OrderDetails.Quantity.append(OrderData[i].Quantity[j])
                                OrderDetails.Price.append(OrderData[i].Price[j])
                                SubTotalPrice = SubTotalPrice + (OrderData[i].Quantity[j] * OrderData[i].Price[j])
                                ProductStatus.append(OrderData[i].OrderSubStatus)
                                ProductData = ndb.Key("ProductsDB",OrderData[i].ProductID[j]).get()
                                if(ProductData != None):
                                    ProductDetails.append(ProductData)
                            if(OrderData[i].OrderSubStatus == "ReUploadPrescription"):
                                ReUploadPrescription = 1
                                PaymentRequired = 0
                            elif(OrderData[i].OrderSubStatus == "PaymentRequired" and PaymentRequired == 1):
                                ReUploadPrescription = 0
                                PaymentRequired = 1
                            else:
                                PaymentRequired = 0
                        ProductsCount = len(OrderDetails.ProductID)
                        if(ReUploadPrescription == 1):
                            ImageUploadURL = blobstore.create_upload_url("/ViewOrderDetails")
                        for i in PharmacyID:
                            PD = ndb.Key("PharmacyDB",i).get()
                            PharmacyDetails.append(PD)
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
                        self.redirect("/VendorOrders?vendorEmail="+vendorEmail)
                    else:
                        OrderDetails = OrderData[0]
                        for i in range(0,len(OrderDetails.ProductID)):
                            ProductData = ndb.Key("ProductsDB",OrderDetails.ProductID[i]).get()
                            if(ProductData != None):
                                ProductDetails.append(ProductData)
                        ProductsCount = len(OrderDetails.ProductID)
                    UserDetails = ndb.Key("UsersDB", OrderDetails.userEmail).get()
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
            'Category' : Category,
            'SignInAs' : SignInAs,
            'CartCount' : CartCount,
            'UserDetails' : UserDetails,
            'VendorDetails' : VendorDetails,
            'notification' : notification,
            'OrderDetails' : OrderDetails,
            'ProductDetails' : ProductDetails,
            'ProductsCount' : ProductsCount,
            'ProductStatus' : ProductStatus,
            'PaymentRequired' : PaymentRequired,
            'ReUploadPrescription' : ReUploadPrescription,
            'PharmacyID' : PharmacyID,
            'DC' : DC,
            'PPID' : PPID,
            'PharmacyDetails' : PharmacyDetails,
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
                Button = self.request.get('Button')
                PharmacyID = VendorDetails.PharmacyID
                OrderID = self.request.get('OrderID')
                userEmail = self.request.get('userEmail')
                VendorComments = self.request.get("VendorComments")
                OrderDetails = OrdersDB.query(OrdersDB.OrderID == OrderID, OrdersDB.PharmacyID == PharmacyID, OrdersDB.userEmail == userEmail).get()
                if(OrderDetails != None and Button == "SubmitForPayment"):
                    Quantity = []
                    OrderTotal = 0.00
                    for i in range(0,len(OrderDetails.ProductID)):
                        Key = "Quantity"+str(OrderDetails.ProductID[i])
                        Q = self.request.get(Key)
                        Quantity.append(int(Q))
                        OrderTotal = OrderTotal + (int(Q)*OrderDetails.Price[i])
                    OrderTotal = OrderTotal + OrderDetails.DeliveryCharge + OrderDetails.ServiceCharge
                    OrderDetails.Quantity = Quantity
                    OrderDetails.VendorComments = VendorComments
                    OrderDetails.OrderTotal = OrderTotal
                    self.response.write(OrderTotal)
                    if(len(OrderDetails.ProductID) != 0):
                        OrderDetails.OrderSubStatus = "PaymentRequired"
                    OrderDetails.put()
                    SendEmail(OrderDetails.userEmail,"Your order uploaded with Prescreption requires payment","""
Dear """+OrderDetails.userEmail+""",

This is an automated email confirmation sent to you in regards of your placed order at MediCare.

Your order ("""+ OrderDetails.OrderID +""") requires payment to proceed further.
You can make payment by loging into your MediCare account and by viewing the order number.

Thanks & regards,
MediCare Team.
                    """)
                    self.redirect('/ViewOrderDetails?SignInAs=Vendor&vendorEmail='+VendorDetails.Email+'&OrderID='+OrderDetails.OrderID)
                elif(OrderDetails != None and Button == "CancelOrder"):
                    OrderDetails.VendorComments = VendorComments
                    OrderDetails.DeliveryCharge = 0.0
                    OrderDetails.ServiceCharge = 0.0
                    OrderDetails.OrderTotal = 0.0
                    for i in range(0,len(OrderDetails.Quantity)):
                        OrderDetails.Quantity[i] = 0
                    OrderDetails.OrderStatus = "Completed"
                    OrderDetails.OrderSubStatus = "CancelledByVendor"
                    OrderDetails.StatusChangedBy = VendorDetails.Email
                    OrderDetails.put()
                    SendEmail(OrderDetails.userEmail,"Your order has been cancelled by Vendor","""
Dear MediCare User,

This is an automated email confirmation sent to you in regards of your placed order at MediCare.

Your whole order ("""+ OrderDetails.OrderID +""") or a part of this order has been cancelled by vendor. You can view the same in "My Orders" tab after logging into your MediCare account.
In case you are able to view same order id in Active Order, this may be due to the fact few items from the whole order are still under consideration.

Thanks & regards,
MediCare Team.
                    """)
                    self.redirect('/ViewOrderDetails?SignInAs=Vendor&vendorEmail='+VendorDetails.Email+'&OrderID='+OrderDetails.OrderID)
                elif(OrderDetails != None and Button == "MarkPacking"):
                    OrderDetails.VendorComments = VendorComments
                    OrderDetails.OrderSubStatus = "PackingInProgress"
                    OrderDetails.StatusChangedBy = VendorDetails.Email
                    OrderDetails.put()
                    self.redirect('/VendorOrders?vendorEmail='+VendorDetails.Email)
                elif(OrderDetails != None and Button == "MarkPacked"):
                    OrderDetails.VendorComments = VendorComments
                    OrderDetails.OrderSubStatus = "ProductPacked"
                    OrderDetails.StatusChangedBy = VendorDetails.Email
                    OrderDetails.put()
                    self.redirect('/VendorOrders?vendorEmail='+VendorDetails.Email)
                elif(OrderDetails != None and Button == "OutForDelivery" and OrderDetails.OrderType == "Delivery"):
                    OrderDetails.VendorComments = VendorComments
                    OrderDetails.OrderSubStatus = "OutForDelivery"
                    OrderDetails.StatusChangedBy = VendorDetails.Email
                    OrderDetails.put()
                    self.redirect('/VendorOrders?vendorEmail='+VendorDetails.Email)
                elif(OrderDetails != None and Button == "ReadyForCollection" and OrderDetails.OrderType == "Collection"):
                    OrderDetails.VendorComments = VendorComments
                    OrderDetails.OrderSubStatus = "ReadyForCollection"
                    OrderDetails.StatusChangedBy = VendorDetails.Email
                    OrderDetails.put()
                    self.redirect('/VendorOrders?vendorEmail='+VendorDetails.Email)
                elif(OrderDetails != None and (Button == "MarkDelivered" or Button == "MarkCollected")):
                    OrderDetails.VendorComments = VendorComments
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
                elif(OrderDetails != None and Button == "AskUserToUpload"):
                    VendorComments = self.request.get("VendorComments1")
                    OrderDetails.VendorComments = VendorComments
                    OrderDetails.OrderSubStatus = "ReUploadPrescription"
                    OrderDetails.put()
                    self.redirect('/ViewOrderDetails?SignInAs=Vendor&vendorEmail='+VendorDetails.Email+'&OrderID='+OrderDetails.OrderID)
                else:
                    self.redirect('/ViewOrderDetails?SignInAs=Vendor&vendorEmail='+VendorDetails.Email+'&OrderID='+OrderDetails.OrderID)
        elif(SignInAs == "User" and userEmail != ""):
            Button = self.request.get('Button')
            OrderID = self.request.get('OrderID')
            OrderDetails = OrdersDB.query(OrdersDB.OrderID == OrderID, OrdersDB.userEmail == userEmail).fetch()
            if(OrderDetails != [] and Button == "UploadPrescription"):
                PrescriptionImage = self.get_uploads()[0]
                PrescriptionImage = get_serving_url(PrescriptionImage.key())
                for i in range(0,len(OrderDetails)):
                    if(OrderDetails[i].PrescriptionRequired == 1 and OrderDetails[i].OrderSubStatus == "ReUploadPrescription"):
                        OrderDetails[i].PrescriptionImage = PrescriptionImage
                        OrderDetails[i].OrderSubStatus = "Reviewing"
                        OrderDetails[i].put()
                self.redirect('/ViewOrderDetails?SignInAs=User&userEmail='+userEmail+'&OrderID='+OrderDetails[0].OrderID)
            elif(OrderDetails != [] and Button == "CancelOrder"):
                for i in range(0,len(OrderDetails)):
                    OrderDetails[i].DeliveryCharge = 0.0
                    OrderDetails[i].ServiceCharge = 0.0
                    OrderDetails[i].OrderTotal = 0.0
                    for j in range(0,len(OrderDetails[i].Quantity)):
                        OrderDetails[i].Quantity[j] = 0
                    OrderDetails[i].OrderStatus = "Completed"
                    OrderDetails[i].OrderSubStatus = "CancelledByCustomer"
                    OrderDetails[i].put()
                SendEmail(userEmail,"You have cancelled your order at MediCare","""
Dear MediCare User,

This is an automated email confirmation sent to you in regards of your placed order at MediCare.

Your whole order ("""+ OrderDetails.OrderID +""") has been cancelled by you. You can view the same in "My Orders" tab after logging into your MediCare account.

Thanks & regards,
MediCare Team.
                """)
                self.redirect('/MyOrders?userEmail='+userEmail)
            elif(OrderDetails != [] and Button == "Pay"):
                for i in range(0,len(OrderDetails)):
                    OrderDetails[i].OrderSubStatus = "PaymentSuccessful"
                    OrderDetails[i].put()
                self.redirect('/ViewOrderDetails?SignInAs=User&userEmail='+userEmail+'&OrderID='+OrderDetails[0].OrderID)
        else:
            self.redirect('/')

app = webapp2.WSGIApplication([
    ('/ViewOrderDetails',ViewOrderDetails),
], debug=True)
