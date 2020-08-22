import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from ProductsDB import ProductsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class TermsOfUse(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

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
        }

        template = JINJA_ENVIRONMENT.get_template('TermsOfUse.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/TermsOfUse',TermsOfUse),
], debug=True)
