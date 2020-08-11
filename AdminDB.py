from google.appengine.ext import ndb

class AdminDB(ndb.Model):
    AdminEmail = ndb.StringProperty()
    AdminPassword = ndb.StringProperty()
