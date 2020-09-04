from google.appengine.ext import ndb

class ProductsDB(ndb.Model):
    ProductID = ndb.StringProperty()
    ProductName = ndb.StringProperty()
    Description = ndb.StringProperty()
    Ingredients = ndb.StringProperty()
    Dosage = ndb.StringProperty()
    ProductLife = ndb.StringProperty()
    Category = ndb.StringProperty()
    Quantity = ndb.IntegerProperty()
    Price = ndb.FloatProperty()
    PrescriptionRequired = ndb.IntegerProperty()
    Images = ndb.StringProperty(repeated = True)
    StockedIn = ndb.StringProperty(repeated = True)
