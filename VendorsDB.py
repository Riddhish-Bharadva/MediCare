from google.appengine.ext import ndb

class VendorsDB(ndb.Model):
    PharmacyID = ndb.StringProperty()
    FirstName = ndb.StringProperty()
    LastName = ndb.StringProperty()
    Email = ndb.StringProperty()
    Password = ndb.StringProperty()
    Contact = ndb.StringProperty()
    Address = ndb.StringProperty()
    Gender = ndb.StringProperty()
    DOB = ndb.StringProperty()
    RegisteredAs = ndb.StringProperty()
    EmailVerified = ndb.IntegerProperty()
    ResetPasswordLinkSent = ndb.IntegerProperty()
    IsActive = ndb.IntegerProperty()
