from google.appengine.ext import ndb

class ContactUsDB(ndb.Model):
    FirstName = ndb.StringProperty()
    LastName = ndb.StringProperty()
    userEmail = ndb.StringProperty()
    Contact = ndb.StringProperty()
    Query = ndb.StringProperty()
    FormSubmittedOn = ndb.StringProperty()
