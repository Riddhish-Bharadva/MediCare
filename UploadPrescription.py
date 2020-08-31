import webapp2
import jinja2
import os
from datetime import datetime
from math import sin, cos, sqrt, atan2, radians
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url
from UsersDB import UsersDB
from OrdersDB import OrdersDB
from PharmacyDB import PharmacyDB
from ProductsDB import ProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class UploadPrescription(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userEmail = self.request.get('userEmail')
        notification = self.request.get('notification')
        SignInStatus = ""
        ImageUploadURL = ""
        UserDetails = None
        PharmacyDetails = None
        PharmacyDetailsLength = 0
        Category = []
        Distance = {}

        if(userEmail != ""):
            UserDetails = ndb.Key('UsersDB',userEmail).get()
            if(UserDetails != None and UserDetails.IsActive == 0):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails == None):
                self.redirect('/UserSignIn?notification=EmailIdNotRegisteredOrInActive')
            elif(UserDetails != None and UserDetails.IsActive == 1):
                SignInStatus = "SignOut"
                if(notification != "OrderSuccessfullyPlaced"):
                    ImageUploadURL = blobstore.create_upload_url("/UploadPrescription")
                Latitude1 = UserDetails.Latitude
                Longitude1 = UserDetails.Longitude
                PharmacyDetails = PharmacyDB.query().fetch()
                if(PharmacyDetails != None):
                    PharmacyDetailsLength = len(PharmacyDetails)
                    for i in range(0,len(PharmacyDetails)):
                        Latitude2 = PharmacyDetails[i].Latitude
                        Longitude2 = PharmacyDetails[i].Longitude
                        DifferenceInLatitude = radians(Latitude2 - Latitude1)
                        DifferenceInLongitude = radians(Longitude2 - Longitude1)
                        Formula = (sin(DifferenceInLatitude/2)**2) + cos(radians(Latitude1)) * cos(radians(Latitude2)) * (sin(DifferenceInLongitude/2)**2)
                        Result = 6373.0*2*atan2(sqrt(Formula),sqrt(1-Formula))
                        Distance[PharmacyDetails[i].PharmacyID] = round(Result,3)
                    Distance = sorted(Distance.items(), key=lambda x:x[1])
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
            'ImageUploadURL' : ImageUploadURL,
            'UserDetails' : UserDetails,
            'Category' : Category,
            'notification' : notification,
            'PharmacyDetails' : PharmacyDetails,
            'PharmacyDetailsLength' : PharmacyDetailsLength,
            'Distance' : Distance,
        }

        template = JINJA_ENVIRONMENT.get_template('UploadPrescription.html')
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
                PrescriptionImage = self.get_uploads()[0]
                PrescriptionImage = get_serving_url(PrescriptionImage.key())
                OrderID = datetime.now().strftime("%Y%m%d%H%M%S")
                OrderPlacedOn = datetime.now().strftime("%d/%m/%Y at %H:%M:%S")
                PharmacyID = self.request.get('PharmacyID')
                PatientName = self.request.get('PatientName')
                UserComments = self.request.get('UserComments')
                OrderType = self.request.get('OrderType')
                OrderStatus = "Active"
                OrderSubStatus = "OrderPlaced"
                OrdersConnect = OrdersDB(userEmail = userEmail)
                Latitude1 = UserDetails.Latitude
                Longitude1 = UserDetails.Longitude
                PharmacyDetails = ndb.Key("PharmacyDB",PharmacyID).get()
                if(PharmacyDetails != None):
                    Latitude2 = PharmacyDetails.Latitude
                    Longitude2 = PharmacyDetails.Longitude
                    DifferenceInLatitude = radians(Latitude2 - Latitude1)
                    DifferenceInLongitude = radians(Longitude2 - Longitude1)
                    Formula = (sin(DifferenceInLatitude/2)**2) + cos(radians(Latitude1)) * cos(radians(Latitude2)) * (sin(DifferenceInLongitude/2)**2)
                    Result = 6373.0*2*atan2(sqrt(Formula),sqrt(1-Formula))
                    Result = round(Result,3)
                    DeliveryCharge = 0.0
                    ServiceCharge = 0.0
                    if(OrderType == "Delivery"):
                        if(round(Result,3) <= 1.5):
                            DeliveryCharge = DeliveryCharge + 1.0
                        elif(round(Result,3) > 1.5 and round(Result,3) <= 3.0):
                            DeliveryCharge = DeliveryCharge + 2.0
                        elif(round(Result,3) > 3.5 and round(Result,3) <= 4.5):
                            DeliveryCharge = DeliveryCharge + 3.0
                        elif(round(Result,3) > 4.5 and round(Result,3) <= 6.0):
                            DeliveryCharge = DeliveryCharge + 3.0
                        OrdersConnect.DeliveryCharge = DeliveryCharge
                        OrdersConnect.ServiceCharge = 1.0
                    else:
                        OrdersConnect.DeliveryCharge = DeliveryCharge
                        OrdersConnect.ServiceCharge = ServiceCharge
                OrdersConnect.OrderID = OrderID
                OrdersConnect.PrescriptionRequired = 1
                OrdersConnect.PrescriptionImage = PrescriptionImage
                OrdersConnect.OrderType = OrderType
                OrdersConnect.PharmacyID = PharmacyID
                OrdersConnect.OrderPlacedOn = OrderPlacedOn
                OrdersConnect.OrderStatus = OrderStatus
                OrdersConnect.OrderSubStatus = OrderSubStatus
                OrdersConnect.PatientName = PatientName
                OrdersConnect.UserComments = UserComments
                OrdersConnect.put()
                self.redirect("/UploadPrescription?userEmail="+userEmail+"&notification=OrderSuccessfullyPlaced")
        else:
            self.redirect('/UserSignIn')

app = webapp2.WSGIApplication([
    ('/UploadPrescription',UploadPrescription),
], debug=True)
