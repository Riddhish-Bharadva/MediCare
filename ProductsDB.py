from google.appengine.ext import ndb

class ProductsDB(ndb.Model):
    MedicineName = ndb.StringProperty()
    Description = ndb.StringProperty()
    Category = ndb.StringProperty()
    SubCategory = ndb.StringProperty()
    Quantity = ndb.IntegerProperty()
    Price = ndb.FloatProperty()
    Images = ndb.BlobKeyProperty(repeated = True)
