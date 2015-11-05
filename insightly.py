#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#
# Python client library for v2.1/v2.2 Insightly API
# Supports both Python v2.7 and 3.x
# Brian McConnell <brian@insight.ly>
#
import base64
import datetime
import json
import mimetypes
import string
import sys
import urllib
import zlib

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
    
def lowercase(text):
    try:
        lc = text.lower()
    except:
        lc = string.lower(text)
    return lc

class Insightly():
    """
    Insightly Python library for Insightly API v2.2
    Brian McConnell <brian@insight.ly>
   
    This library provides user friendly access to the versions 2.2 of the REST API for Insightly. The library provides several services, including:
   
    * HTTPS request generation
    * Data type validation
   
    The library is built using Python standard libraries (no third party tools required, so it will run out of the box on most Python
    environments, including Google App Engine). The wrapper functions return native Python objects, typically dictionaries, or lists of
    dictionaries, so working with them is easily done using built in functions.
    
    The version 2.2 API adds several new endpoints which make it easy to make incremental changes to existing Insightly objects, such
    as to add a phone number to a contact, and also more closely mirrors the functionality available in the web app (such as the
    ability to follow and unfollow objects.s)
    
    API DOCUMENTATION
    
    Full API documentation and an interactive sandbox is available at https://api.insight.ly/v2.2/Help
    
    IMPORTANT NOTE
    
    This version of the client library is not backward compatible with the previous version. In order to simplify the code base, and
    enable better test coverage, this library is organized around a small number of general purpose methods that implement create,
    read, update and delete functionality generically. The previous version of the library has one method per endpoint, per HTTP method,
    which grew unwieldy with the addition of many new endpoints in v2.1
    
    INSTALLATION
    
    Just copy the files in this project into your working directory, if you don't plan to run test suites, you only need the insightly.py
    file. insightlytest.py and apollo17.jpg are used for testing. The file insightlyexamples.py will be used to highlight short examples
    of simple integrations. 
   
    USAGE
    
    If you are working with very large recordsets, you should use ODATA filters to access data in smaller chunks. This is a good idea in
    general to minimize server response times. This is no longer an issue with version 2.2, which returns paginated results that you
    can page through using the optional top and skip parameters.
   
    BASIC USE PATTERNS:
    
    i = Insightly(apikey = 'foozlebarzle', version=2.1)
    projects = i.read('projects', top=50, filters={'email':'foo@bar.com'})
    print 'Found ' + str(len(projects)) + ' projects'
    
    The create() function enables you to create an Insightly object, call it as follows:
        object_graph = i.create(endpoint, object_graph)
        where object graph is a dictionary
        for example:
        
        contact = i.create('contacts',{'FIRST_NAME':'Foo','LAST_NAME':'Bar'})
    
    The create_child() function enables you to add a child object, for example to add an address to a contact, use it as follows:
        object_graph = i.create_child(endpoint, object_graph)
        for example:
        
        address = i.create_child('contacts',contact_id,'addresses',{'CITY':'San Francisco','STATE':'CA','ADDRESS_TYPE':'Home'})

    The delete() function enables you to delete Insightly objects and child objects, use it as follows:
        success = i.delete('contacts', contact_id)
        success = i.delete('contacts', contact_id, sub_type='addresses', sub_type_id=address_id)

    The read() function enables you to get/find Insightly objects, with optional pagination and search terms, use as follows:
        contacts = i.read('contacts')
        contacts = i.read('contacts', top=100, skip=500) # get 100 records after skipping 500
        contacts = i.read('contacts', filters={'email':'brian@insightly.com'}) # apply an optional filter to search records
    
    The update() function enables you to update an existing Insightly object, use this as follows:
        project = i.update('projects', project)        # where project is a dictionary containing the object graph
    
    The upload() function enables you to upload a file to endpoints that accept file attachments, use this as follows:
        upload('opportunities', opportunity_id, 'apollo17.jpg')
    
    The upload_image() function enables you to upload an image for a contact, organization, project or opportunity
        upload('contacts', contact_id, 'apollo17.jpg')
        
    ENDPOINTS
    
    The helper functions work with all endpoints in the API documentation. For example, to get a list of pipelines, you'd call
    
    pipelines = i.read('pipelines')
    
    See insightlytest.py for examples of how the endpoints are called (the automated test suite covers nearly all endpoints in the API)

    AUTOMATED TEST SUITE
    
    The library includes a comprehensive automated test suite, which can be found in insightlytest.py
    
    To run a test suite, using the following code:
    
        from insightlytest import test
        test()
    
    The program will test most API endpoints with sample data and report results to the console, as well as write
    them out to the file testresults.txt
    
    INTERACTIVE DOCUMENTATION
    
    Use Python's built in help() function to pull up documentation for individual methods.
    
    For API documentation and interactive sandbox, go to https://api.insight.ly/v2.2/Help
    
    TROUBLESHOOTING TIPS
    
    One of the main issues API users run into during write/update operations is a 400 error (bad request) due to missing required fields.
    If you are unclear about what the server is expecting, a good way to troubleshoot this is to do the following:
    
    * Using the web interface, create the object in question (contact, project, team, etc), and add sample data and child elements to it
    * Use the corresponding read() method to get this object
    * Inspect the object's contents and structure (it will be returned as a Python dictionary)
    
    If you get stuck, we highly recommend downloading the Postman extension for Chrome. You can use it to manually generate requests
    and view the server response. It is very helpful in troubleshooting REST API integrations with systems like ours.
    
    Read operations via the API are generally quite straightforward, so if you get struck on a write operation, this is a good workaround,
    as you are probably just missing a required field or using an invalid element ID when referring to something such as a link to a contact.
    
    """
    def __init__(self, apikey='', version='2.2', dev=None, gzip=True, debug=True, test=False):
        
        """
        Instantiates the class, logs in, and fetches the current list of users. Also identifies the account owner's user ID, which
        is a required field for some actions. This is stored in the property Insightly.owner_id
        
        gzip compression is enabled by default, the client library will try to decompress return results, with fallback to plaintext
        if the server is ignoring compression requests (this reduces payload size by about 10:1 when active)

        Raises an exception if login or call to getUsers() fails, most likely due to an invalid or missing API key
        """
        
        self.debug = debug
        if gzip:
            self.gzip = True
        else:
            self.gzip = False
        if test:
            self.test = True
        else:
            self.test = False
        
        self.version = str(version)
        if dev:
            self.domain = 'https://api.insightly' + dev + '.com/v'
        else:
            self.domain = 'https://api.insight.ly/v'
        self.filehandle = open('testresults.txt','w')
        self.baseurl = self.domain + self.version
        self.baseurlv21 = self.domain + '2.1'
        self.baseurlv22 = self.domain + '2.2'
        self.test_data = dict()
        self.test_failures = list()
        if len(apikey) < 1:
            try:
                f = open('apikey.txt', 'r')
                apikey = f.read()
                if self.debug:        print('API Key read from disk as ' + apikey)
            except:
                raise Exception('No API provided on instantiation, and apikey.txt file not found in project directory.')
        version = str(version)
        self.version = version
        self.swagger = None
        if version == '2.2' or version == '2.1':
            self.alt_header = 'Basic '
            self.apikey = apikey
            self.tests_run = 0
            self.tests_passed = 0
            self.users = self.read('users')
            self.version = version
            if self.debug:        print('CONNECTED: found ' + str(len(self.users)) + ' users')
            for u in self.users:
                if u.get('ACCOUNT_OWNER', False):
                    self.owner_email = u.get('EMAIL_ADDRESS','')
                    self.owner_id = u.get('USER_ID', None)
                    self.owner_name = u.get('FIRST_NAME','') + ' ' + u.get('LAST_NAME','')
                    if self.debug:        print('The account owner is ' + self.owner_name + ' [' + str(self.owner_id) + '] at ' + self.owner_email)
                    break
        else:
            raise Exception('Python library only supports v2.1 or v2.2 APIs. We recommend using v2.2.')
        
    def create(self, object_type, object_graph, id = None, sub_type = None):
        """
        This is a general purpose write method that can be used to create (POST)
        Insightly objects.
        
        USAGE:
        
        i = Insightly()
        new_lead = {'first_name':'foo','last_name':'bar'}
        lead = i.create('leads',new_lead)
        print str(lead)
        
        """
        test = self.test
        object_type = lowercase(object_type)
        if type(object_graph) is dict:
            data = json.dumps(object_graph)
            url = '/' + object_type
            if id is not None:
                url += '/' + str(id)
                if sub_type is not None:
                    url += '/' + sub_type
            if test:
                self.tests_run += 1
                try:
                    self.generateRequest(url, 'POST', data, alt_auth = 'borkborkborkborkbork')
                    self.printline('FAIL: POST w/ bad auth ' + url)
                except:
                    self.tests_passed += 1
                    self.printline('PASS: POST w/ bad auth ' + url)
            if test:
                self.tests_run += 1
                try:
                    try:
                        text = self.generateRequest(url, 'POST', data).decode()
                    except:
                        text = self.generateRequest(url, 'POST', data)
                    data = json.loads(text)
                    self.tests_passed += 1
                    self.printline('PASS: POST ' + url)
                    return data
                except:
                    self.printline('FAIL: POST ' + url)
                    self.printline(str(sys.exc_info()))
            else:
                try:
                    text = self.generateRequest(url, 'POST', data).decode()
                except:
                    text = self.generateRequest(url, 'POST', data)
                data = json.loads(text)
                return data
        else:
            raise Exception('object_graph must be a Python dictionary')
        
    def create_child(self, object_type, id, sub_type, object_graph):
        """
        This method is used to append a child element, such as a link, to an existing object
        
        USAGE:
        
        i = Insightly()
        link = {'LEAD_ID':lead_id,'TASK_ID':task_id}
        i.create_child('tasks', task_id, 'tasklinks', link)
        """
        test = self.test
        object_type = lowercase(object_type)
        if type(object_graph) is dict:
            data = json.dumps(object_graph)
            url = '/' + object_type + '/' + str(id) + '/' + sub_type
            if test:
                self.tests_run += 1
                try:
                    try:
                        text = self.generateRequest(url, 'POST', data).decode()
                    except:
                        text = self.generateRequest(url, 'POST', data)
                    self.tests_passed += 1
                    self.printline('PASS: POST ' + url)
                    data = json.loads(text)
                    return data
                except:
                    self.printline('FAIL: POST ' + url)
            else:
                try:
                    text = self.generateRequest(url, 'POST', data).decode()
                except:
                    text = self.generateRequest(url, 'POST', data)
                data = json.loads(text)
                return data
        else:
            raise Exception('object graph must be a Python dictionary')
        
    def delete(self, object_type, id, sub_type=None, sub_type_id = None):
        """
        This is a general purpose delete method that will allow the user to delete Insightly
        objects (e.g. contacts) and sub_objects (e.g. delete a contact_info linked to an object)
        
        USAGE:
        
        i = Insightly()
        lead_id = 123456
        success = i.delete('leads', lead_id)
        if success:
            print 'Deleted lead number ' + str(lead_id)
        """
        test = self.test
        object_type = lowercase(object_type)
        url = '/' + object_type
        if id is not None:
            url += '/' + str(id)
            if sub_type is not None:
                url += '/' + sub_type
                if sub_type_id is not None:
                    url += '/' + str(sub_type_id)
        if test:
            self.tests_run += 1
            try:
                self.generateRequest(url, 'DELETE', '', alt_auth = 'borkborkborkborkbork')
                self.printline('FAIL: DELETE w/ bad auth ' + url)
            except:
                self.tests_passed += 1
                self.printline('PASS: DELETE w/ bad auth ' + url)
        if test:
            self.tests_run += 1
            try:
                text = self.generateRequest(url, 'DELETE', '')
                self.printline('PASS: DELETE ' + url)
                self.tests_passed += 1
            except:
                self.printline('FAIL: DELETE ' + url)
        else:
            text = self.generateRequest(url, 'DELETE', '')
            return True
        
    def dictToList(self, data):
        """
        This helper function checks to see if the returned data is a list or a lone dict, string, int or float.
        If it is a lone item, it is appended to a list.
        
        Use case: a function may return a list of dictionaries, or a single dictionary, or a nullset. This function
        standardizes this to a list of dictionaries, or in the case of a null set, an empty list.
        """
        if type(data) is list:
            return data
        elif type(data) is dict or type(data) is str or type(data) is int or type(data) is float:
            l = list()
            l.append(data)
            return l
        elif data is None:
            return
        else:
            return list()
        
    def findUser(self, email):
        """
        Client side function to quickly look up Insightly users by email. Returns a dictionary containing
        user details or None if not found. This is useful when you need to find the user ID for someone but
        only know their email addresses, for example when creating and assigning a new project or task. 
        """
        for u in self.users:
            if u.get('EMAIL_ADDRESS','') == email:
                return u

    def generateRequest(self, url, method, data, alt_auth=None, test=False, headers=None):
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
        # generate full URL from base url and relative url
        if self.version == '2.1':
            full_url = self.baseurlv21 + url
        elif self.version == '2.2':
            full_url = self.baseurlv22 + url
        else:
            full_url = self.baseurl + url
        # self.printline('URL:  ' + full_url)
        request = urllib2.Request(full_url)
        if self.gzip:
            request.add_header("Accept-Encoding", "gzip")
        if alt_auth is not None:
            request.add_header("Authorization", self.alt_header)
        else:
            try:
                base64string = str(base64.b64encode(self.apikey.encode('ascii')), encoding='ascii')
            except:
                base64string = str(base64.b64encode(self.apikey))
            base64string.replace('\n','')
            header = 'Basic ' + base64string
            request.add_header("Authorization", header)
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
        if self.gzip:
            try:
                # try to decode as gzipped text
                text = zlib.decompress(text, zlib.MAX_WBITS|16)
            except:
                # fall back to plain text (sometimes the server ignores the gzip encoding request, e.g. staging environment)
                pass
        return text
    
    def getMethods(self, test=False):
        """
        Returns a list of the callable methods in this library.
        """
        methods = [method for method in dir(self) if callable(getattr(self, method))]
        return methods
        
    def ODataQuery(self, querystring, top=None, skip=None, orderby=None, filters=None):
        """
        This helper function generates an OData compatible query string. It is used by many
        of the search functions to enable users to filter, page and order recordsets.
        
        NOTE: version 2.2 does not support OData, but does support optional querystring
        parameters. This function will generate the correct query string depending on the
        API version to preserve backward compatibility. Version 2.2 also limits you to
        filtering on a single optional parameters (e.g. phone_number=4155551212) to insure good
        query performance. The orderby option is no longer supported in version 2.2.
        You can do a wildcard search by prepending or appending a % sign to a filter,
        for example, phone = %4155551212 will match for 14155551212 and +14155551212.
        
        See the version 2.2 API documentation for a list of optional parameters that are
        currently supported by each API endpoint.
        """
        #
        # TODO: double check that this has been implemented correctly
        #
        if str(self.version) == '2.2':
            if type(querystring) is str:
                if top is not None:
                    querystring += '?top=' + str(top)
                else:
                    querystring += '?top=100'
                if skip is not None:
                    querystring += '&skip=' + str(skip)
                if filters is not None:
                    if type(filters) is dict:
                        filterkeys = filters.keys()
                        if len(filterkeys) > 1:
                            raise Exception('Only one filter parameter is allowed per query at this time')
                        else:
                            for fk in filterkeys:
                                querystring += '&' + fk + '=' + str(filters[fk])
                return querystring
            else:
                return ''
        else:
            if type(querystring) is str:
                if top is not None:
                    if querystring == '':
                        querystring += '?$top=' + str(top)
                    else:
                        querystring += '&$top=' + str(top)
                if skip is not None:
                    if querystring == '':
                        querystring += '?$skip=' + str(skip)
                    else:
                        querystring += '&$skip=' + str(skip)
                if orderby is not None:
                    if querystring == '':
                        querystring += '?$orderby=' + urllib.quote(orderby)
                    else:
                        querystring += '&$orderby=' + urllib.quote(orderby)
                if type(filters) is list:
                    for f in filters:
                        f = string.replace(f,' ','%20')
                        f = string.replace(f,'=','%20eq%20')
                        f = string.replace(f,'>','%20gt%20')
                        f = string.replace(f,'<','%20lt%20')
                        if querystring == '':
                            querystring += '?$filter=' + f
                        else:
                            querystring += '&$filter=' + f
                return querystring
            else:
                return ''
        
    def printline(self, text):
        if lowercase(text).count('fail') > 0:
            self.test_failures.append(text)
        if self.filehandle is None:
            self.filehandle = open('testresults.txt', 'w')
        if self.debug:        print(text)
        self.filehandle.write(text + '\n')
        
    def read(self, object_type, id = None, sub_type=None, top=None, skip=None, orderby=None, filters=None):
        """
        This is a general purpose read method that will allow the user to easily fetch Insightly objects.
        This will replace the hand built request handlers, which are too numerous to test and support
        adequately.
        
        USAGE:
        
        i = Insightly(version=2.2, apikey='foozlebarzle')
        projects = i.read('projects', filters{'status':'in progress'})
        for p in projects:
            print str(p)
            
        NOTE:
        
        The orderby parameter is no longer supported in version 2.2. If you need to search for records newer than
        a certain date/time, use the filter updated_after_utc
        
        If an optional query parameter is provided in filters (should be a dictionary), this function will query
        /{object_type}/search
        
        """
        test = self.test
        if top is not None or skip is not None or orderby is not None or filters is not None:
            search=True
        else:
            search=False
        object_type = lowercase(object_type)
        url = '/' + object_type
        if id is not None:
            url += '/' + str(id)
            if sub_type is not None:
                url += '/' + sub_type
        elif filters is not None:
            url += '/search'
        else:
            pass
        if search:
            url += self.ODataQuery('',top=top, skip=skip, orderby=orderby, filters=filters)
        if test:
            self.tests_run += 1
            try:
                self.generateRequest(url, 'GET', '', alt_auth = 'borkborkborkborkbork')
                self.printline('FAIL: GET w/ bad auth ' + url)
            except:
                self.tests_passed += 1
                self.printline('PASS: GET w/ bad auth ' + url)
        if test:
            self.tests_run += 1
            try:
                text = self.generateRequest(url,'GET','')
                self.tests_passed += 1
                self.printline('PASS: GET ' + url)
                try:
                    results = self.dictToList(json.loads(text))
                except:
                    results = self.dictToList(json.loads(text.decode('utf-8')))
                return results
            except:
                self.printline('FAIL: GET ' + url)
        else:
            text = self.generateRequest(url, 'GET', '')
            try:
                results = self.dictToList(json.loads(text))
            except:
                results = self.dictToList(json.loads(text.decode('utf-8')))
            return results
        
    def update(self, object_type, object_graph, id = None, sub_type = None):
        """
        This is a general purpose write method that can be used to update (PUT)
        Insightly objects.
        
        USAGE:
        
        i = Insightly()
        lead_id = 123456
        lead = i.read('leads', lead_id)
        if lead is not None:
            lead['first_name'] = 'Foozle'
            lead['last_name'] = 'Barzle
            success = i.update('leads', lead, id = lead_id)
            if success:
                print 'Updated lead number ' + str(lead_id)
        """
        object_type = lowercase(object_type)
        test = self.test
        if type(object_graph) is dict:
            data = json.dumps(object_graph)
            url = '/' + object_type
            if id is not None:
                url += '/' + str(id)
                if sub_type is not None:
                    url += '/' + sub_type
            if test:
                self.tests_run += 1
                try:
                    self.generateRequest(url, 'PUT', data, alt_auth = 'borkborkborkborkbork')
                    self.printline('FAIL: PUT w/ bad auth ' + url)
                except:
                    self.tests_passed += 1
                    self.printline('PASS: PUT w/ bad auth ' + url)
            if test:
                self.tests_run += 1
                try:
                    try:
                        text = self.generateRequest(url, 'PUT', data).decode()    
                    except:
                        text = self.generateRequest(url, 'PUT', data)
                    data = json.loads(text)
                    self.printline('PASS: PUT ' + url)
                    self.tests_passed += 1
                    return data
                except:
                    self.printline('FAIL: PUT ' + url)
            else:
                try:
                    text = self.generateRequest(url, 'PUT', data).decode()    
                except:
                    text = self.generateRequest(url, 'PUT', data)
                data = json.loads(text)
                return data
        else:
            raise Exception('object_graph must be a Python dictionary')
        
    def upload(self, object_type, id, filename):
        test = self.test
        f = open(filename, 'rb')
        value = f.read()
        content_type, body = self.encode_multipart_formdata([(filename + 'xyxyxyxyxyxyxyxyxyx314159', filename, value)])
        headers=dict()
        headers['Content-Type'] = content_type
        headers['Content-Length'] = str(len(body))
        url = '/' + object_type + '/'+ str(id) + '/fileattachments'
        if test:
            self.tests_run += 1
            try:
                try:
                    text = self.generateRequest(url, 'POST', body, headers=headers).decode()
                except:
                    text = self.generateRequest(url, 'POST', body, headers=headers)
                self.printline('PASS: UPLOAD ' + url)
                self.tests_passed += 1
                return json.loads(text)
            except:
                self.printline('FAIL: UPLOAD ' + url)
        else:
            try:
                text = self.generateRequest(url, 'POST', body, headers=headers).decode()
            except:
                text = self.generateRequest(url, 'POST', body, headers=headers)
            return json.loads(text)
    
    def upload_image(self, object_type, id, filename):
        test = self.test
        f = open(filename, 'rb')
        value = f.read()
        # TODO: probably need to clean the filename so it does not have illegal characters
        url = '/' + object_type + '/' + str(id) + '/image/' + filename
        if test:
            self.tests_run += 1
            try:
                self.generateRequest(url, 'PUT', value)
                self.printline('PASS: upload image: ' + url)
                self.tests_passed += 1
            except:
                self.printline('FAIL: upload image: ' + url)
        else:
            return self.generateRequest(url, 'PUT', value)
        
    def encode_multipart_formdata(self, files):
        #
        # NOTE: file attachment uploads do not currently work for Python 3.x, working on this issue
        #
        LIMIT = '----------lImIt_of_THE_fIle_eW_$'
        CRLF = '\r\n'
        L = ''
        #for (key, value) in fields:
        #    L.append('--' + LIMIT)
        #    L.append('Content-Disposition: form-data; name="%s"' % key)
        #    L.append('')
        #    L.append(value)
        for (key, filename, value) in files:
            L += '--' + LIMIT + '--' + CRLF
            L += 'Content-Disposition: form-data; name="' + key + '"; filename="' + filename + '"' + CRLF
            L += 'Content-Type: ' + self.get_content_type(filename) + CRLF
            L += '' + CRLF
            L += str(value) + CRLF
        L += '--' + LIMIT + '--' + CRLF
        L += '' + CRLF
        body = L
        content_type = 'multipart/form-data; boundary=%s' % LIMIT
        return content_type, body
    
    def get_content_type(self,filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'