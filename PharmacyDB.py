from google.appengine.ext import ndb

class PharmacyDB(ndb.Model):
    PharmacyID = ndb.StringProperty()
    PharmacyName = ndb.StringProperty()
    OfficialEmailId = ndb.StringProperty()
    OfficialContact = ndb.StringProperty()
    PhysicalAddress = ndb.StringProperty()
    Latitude = ndb.FloatProperty()
    Longitude = ndb.FloatProperty()
    EmailVerified = ndb.IntegerProperty()
    RegisteredBy = ndb.StringProperty()
    IsActive = ndb.IntegerProperty()
