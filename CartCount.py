from google.appengine.ext import ndb
from CartDB import CartDB

def getCartCount(self,userEmail):
    CartCount = 0
    CartData = ndb.Key("CartDB",userEmail).get()
    if(CartData != None):
        CartCount = len(CartData.ProductID)
    return CartCount
