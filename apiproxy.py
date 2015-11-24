#
# Insightly API Proxy for Python / App Engine
# Brian McConnell <brian@insightly.com>
#
# This utility is designed to act as an API proxy server. It is written in Python 2.7
# and will run without modification on Google App Engine. Just serve your Javascript
# from the /js directory in this project, and AJAX requests should be relayed through
# to the Insightly service. This should also run on any webapp2 compatible server platform
#
# Typical Use Case
#
# Client side Javascript will make calls to endpoints on the API proxy that mirror the API
# server, such as:
#
# GET api.yoursite.com/v2.2/contacts/search?phone=+14155551212
#
# The API server will turn around and relay your request to the Insightly server, and relay
# its response back to the client. 

import base64
import os
import string
import types
import urllib
import urllib2
import webapp2
import wsgiref.handlers

#
# import google app engine libraries, replace these with standard 
#

try:
    from google.appengine.ext import webapp
except:
    # skip Google App Engine webapp library
    pass

base_url = 'https://api.insight.ly/'

def authenticate():
    #
    # add user validation logic here, be careful to do this in a way that does not expose user secrets such as
    # the user API key (this is why we do not allow CORS in the first place)
    #
    
    # hardcoding API key for now
    apikey = 'foozlebarzle'
    return base64.encode(apikey)

def generateRequest(url, method, data, alt_auth=None, test=False, headers=None):
    """
    This method is used by other helper functions to generate HTTPS requests and parse
    server responses. This will minimize the amount of work developers need to do to
    integrate with the Insightly API, and will also eliminate common sources of errors
    such as authentication issues and malformed requests. Uses the urllib2 standard
    library, so it is not dependent on third party libraries like Requests
    """
    if type(url) is not str: raise Exception('url must be a string')
    if type(method) is not str: raise Exception('method must be a string')
    valid_method = False
    response = None
    text = ''
    if method == 'GET' or method == 'PUT' or method == 'DELETE' or method == 'POST':
        valid_method = True
    else:
        raise Exception('parameter method must be GET|DELETE|PUT|UPDATE')
    request = urllib2.Request(url)
    request.get_method = lambda: method
    request.add_header('Content-Type', 'application/json')
    if headers is not None:
        headerkeys = headers.keys()
        for h in headerkeys:
            request.add_header(h, headers[h])
    # open the URL, if an error code is returned it should raise an exception
    if method == 'PUT' or method == 'POST':
        result = urllib2.urlopen(request, data)
    else:
        result = urllib2.urlopen(request)
    text = result.read()
    return text
    
class APIProxyHandler(webapp2.RequestHandler):
    def delete(self):
        apikey = authenticate()
        path_qs = self.request.headers['path_qs']
        url = base_url + path_qs
        headers = {'Authorization','Basic ' + api_key}
        text = generateRequest(url, 'DELETE', None, headers=headers)
        self.response.headers['Content-Type']='application/json'
        self.response.out.write(text)
    def get(self):
        apikey = authenticate()
        path_qs = self.request.headers['path_qs']
        url = base_url + path_qs
        headers = {'Authorization','Basic ' + api_key}
        text = generateRequest(url, 'GET', None, headers=headers)
        self.response.headers['Content-Type']='application/json'
        self.response.out.write(text)
    def post(self):
        body = self.request.headers['body']
        path_qs = self.request.headers['path_qs']
        url = base_url + path_qs
        headers = {'Authorization','Basic ' + api_key}
        text = generateRequest(url, 'POST', body, headers=headers)
        self.response.headers['Content-Type']='application/json'
        self.response.out.write(text)
    def put(self):
        body = self.request.headers['body']
        path_qs = self.request.headers['path_qs']
        url = base_url + path_qs
        headers = {'Authorization','Basic ' + api_key}
        text = generateRequest(url, 'PUT', body, headers=headers)
        self.response.headers['Content-Type']='application/json'
        self.response.out.write(text)
        
app = webapp2.WSGIApplication([("r/(.*)", APIProxyHandler)], debug=True)        # map generic page server request handler