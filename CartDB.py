from google.appengine.ext import ndb

class CartDB(ndb.Model):
    userEmail = ndb.StringProperty()
    ProductID = ndb.StringProperty(repeated=True)
    Quantity = ndb.IntegerProperty(repeated=True)
    PharmacyID = ndb.StringProperty(repeated=True)
