import webapp2
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class VendorHomePage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        vendorEmail = self.request.get('vendorEmail')
        if(vendorEmail == ""):
            self.redirect('/VendorSignIn')

        template_values = {
            'vendorEmail' : vendorEmail,
        }

        template = JINJA_ENVIRONMENT.get_template('VendorHomePage.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/VendorHomePage',VendorHomePage),
], debug=True)
