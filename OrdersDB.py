from google.appengine.ext import ndb

class OrdersDB(ndb.Model):
    userEmail = ndb.StringProperty()
    OrderID = ndb.StringProperty()
    PrescriptionRequired = ndb.IntegerProperty()
    PrescriptionImage = ndb.StringProperty()
    OrderType = ndb.StringProperty()
    PharmacyID = ndb.StringProperty()
    ProductID = ndb.StringProperty(repeated=True)
    ProductName = ndb.StringProperty(repeated=True)
    Quantity = ndb.IntegerProperty(repeated=True)
    Price = ndb.FloatProperty(repeated=True)
    DeliveryCharge = ndb.FloatProperty()
    ServiceCharge = ndb.FloatProperty()
    OrderTotal = ndb.FloatProperty()
    OrderPlacedOn = ndb.StringProperty()