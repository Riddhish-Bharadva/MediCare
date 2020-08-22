import webapp2
import jinja2
import os
from datetime import datetime
from google.appengine.ext import ndb
from EmailModule import SendEmail
from ProductsDB import ProductsDB
from ContactUsDB import ContactUsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class ContactUs(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        notification = self.request.get("notification")
        Category = []
        ProductsData = ProductsDB.query().fetch()
        if(ProductsData == []):
            ProductsData = None
        else:
            for i in range(0,len(ProductsData)):
                if(ProductsData[i].Category not in Category):
                    Category.append(ProductsData[i].Category)
        Category.sort()

        template_values = {
            'Category' : Category,
            'notification' : notification,
        }

        template = JINJA_ENVIRONMENT.get_template('ContactUs.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        ButtonName = self.request.get('Button')
        FirstName = self.request.get('FirstName')
        LastName = self.request.get('LastName')
        userEmail = self.request.get('userEmail')
        Contact = self.request.get('Contact')
        Query = self.request.get('Query')
        FormSubmittedOn = datetime.now().strftime("%d/%m/%Y at %H:%M:%S")

        ContactUsDBConnect = ContactUsDB(userEmail=userEmail)
        ContactUsDBConnect.FirstName = FirstName
        ContactUsDBConnect.LastName = LastName
        ContactUsDBConnect.Contact = Contact
        ContactUsDBConnect.Query = Query
        ContactUsDBConnect.FormSubmittedOn = FormSubmittedOn
        ContactUsDBConnect.Replied = 0
        ContactUsDBConnect.put()

        SendEmail(userEmail,"Your query was successfully submitted to MediCare team","""
Dear """+FirstName+""",

This is an automated email sent as a confirmation for your submitted query.

Your query :
"""+Query+"""


Your query has been recorded and sent to the concerned team for further action.
Our team will get back to you regarding the same as soon as possible.

Thanks & regards,
MediCare Team.
        """)
        self.redirect("/ContactUs?notification=FormSubmittedSuccessfully")

app = webapp2.WSGIApplication([
    ('/ContactUs',ContactUs),
], debug=True)
