from google.appengine.ext import ndb

class VendorProductsDB(ndb.Model):
    PharmacyID = ndb.StringProperty()
    ProductID = ndb.StringProperty()
    Quantity = ndb.IntegerProperty()
    Price = ndb.FloatProperty()
    AddedOn = ndb.StringProperty()
    AddedBy = ndb.StringProperty()
    LastModifiedOn = ndb.StringProperty()
    LastModifiedBy = ndb.StringProperty()
