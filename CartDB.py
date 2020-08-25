from google.appengine.ext import ndb

class CartDB(ndb.Model):
    userEmail = ndb.StringProperty()
    OrderType = ndb.StringProperty()
    ProductID = ndb.StringProperty(repeated=True)
    Quantity = ndb.IntegerProperty(repeated=True)
    Price = ndb.FloatProperty(repeated=True)
    PharmacyID = ndb.StringProperty(repeated=True)
    DeliveryCharge = ndb.FloatProperty()
    ServiceCharge = ndb.FloatProperty()
    CartTotal = ndb.FloatProperty()
