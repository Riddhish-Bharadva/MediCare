from google.appengine.ext import ndb

class UsersDB(ndb.Model):
    user_FirstName = ndb.StringProperty()
    user_LastName = ndb.StringProperty()
    user_Email = ndb.StringProperty()
    user_Password = ndb.StringProperty()
    user_Contact = ndb.StringProperty()
    user_Address = ndb.StringProperty()
    user_Gender = ndb.StringProperty()
    user_DOB = ndb.StringProperty()
