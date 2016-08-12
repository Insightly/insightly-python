#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#
# Python client library for v2.1/v2.2 Insightly API
# Supports both Python v2.7 and 3.x
# Brian McConnell <brian@insight.ly>
#
import os
import base64
import datetime
import json
import mimetypes
import os
import string
import sys
import time
import traceback
import urllib
import zlib

try:
    import urllib.request as urllib2
    from urllib.parse import urlencode
except ImportError:
    import urllib2
    from urllib import urlencode
    
def lowercase(text):
    try:
        lc = text.lower()
    except:
        lc = string.lower(text)
    return lc

def encode_query(text):
    qs = ''
    for t in text:
        c = ord(t)
        if c < 128:
            qs += t
        else:
            h = hex(c).replace('0x','')
            qs += '%u' + h
    return qs

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
        
    The get() function returns a single Python dictionary or None for a specific identified record. Use as follows:
        contact = i.get('contacts', contact_id)

    The read() function enables you to get/find Insightly objects, with optional pagination and search terms, use as follows:
        contacts = i.read('contacts')
        contacts = i.read('contacts', top=100, skip=500) # get 100 records after skipping 500
    
    The search() function is used to do server filtered searches, use as follows:
        contacts = i.search('contacts', 'email=foo.com', top=100, skip=200)
    
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
    def __init__(self, apikey='', version='2.2', dev=None, gzip=True, debug=False, test=False, offline=False, refresh=False):
        
        """
        Instantiates the class, logs in, and fetches the current list of users. Also identifies the account owner's user ID, which
        is a required field for some actions. This is stored in the property Insightly.owner_id
        
        gzip compression is enabled by default, the client library will try to decompress return results, with fallback to plaintext
        if the server is ignoring compression requests (this reduces payload size by about 10:1 when active)

        Raises an exception if login or call to getUsers() fails, most likely due to an invalid or missing API key
        
        To enable offline data processing, set offline=True, and if you want to update the local data store, set refresh=True
        """
        
        if True == debug or True == test:
            self.log_file = open(str(version) + '.txt','w')
        else:
            self.log_file = None

        #
        # Define properties to store locally cached objects, when offline mode is enabled
        #
        
        self.activity_sets = list()
        self.contacts = list()
        self.countries = list()
        self.currencies = list()
        self.custom_fields = list()
        self.emails = list()
        self.events = list()
        self.file_categories = list()
        self.leads = list()
        self.lead_sources = list()
        self.lead_statuses = list()
        self.notes = list()
        self.organisations = list()
        self.opportunities = list()
        self.opportunity_categories = list()
        self.opportunity_state_reasons = list()
        self.pipelines = list()
        self.pipeline_stages = list()
        self.projects = list()
        self.project_categories = list()
        self.relationships = list()
        self.tasks = list()
        self.task_categories = list()
        self.teams = list()
        
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
        if dev is not None:
            self.domain = dev
            self.baseurl = dev
        else:
            if version == 'mobile':
                self.domain = 'https://mobileapi.insightly.com'
                self.baseurl = self.domain
            else:
                self.domain = 'https://api.insight.ly/v'
                self.baseurl = self.domain + self.version
        if True == test:
            self.filehandle = open('testresults.txt','w')
        else:
            self.filehandle = None
        self.test_data = dict()
        self.test_failures = list()
        self.slow_endpoints = list()
        if len(apikey) < 1:
            try:
                f = open('apikey.txt', 'r')
                apikey = f.read().rstrip()
                f.close()
                if self.debug:        print('API Key read from disk as ' + apikey)
            except:
                raise Exception('No API provided on instantiation, and apikey.txt file not found in project directory.')
        version = str(version)
        self.version = version
        self.swagger = None
        if version == '2.2' or version == '2.1' or version == 'mobile':
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
                    self.contact_id = u.get('CONTACT_ID', None)
                    self.email_dropbox = '%s-%s@mailbox.insight.ly' % (u.get('FIRST_NAME', '').lower(),
                                                                       u.get('EMAIL_DROPBOX_IDENTIFIER', ''))
                    if self.debug:        print('The account owner is ' + self.owner_name + ' [' + str(self.owner_id) + '] at ' + self.owner_email)
                    break
            if offline and self.version == '2.2':
                self.sync(refresh=refresh)
                # add more object types once contacts are debugged
        else:
            raise Exception('Python library only supports v2.1 or v2.2 APIs. We recommend using v2.2.')
        
    def check_difference(self, new, old):
        """
        This function checks to see if the list of keys in a new object graph differs
        from the list in the old object graph. This is used to detect situations where
        a field is not saved or updated for some reason.
        """
        if type(new) is dict and type(old) is dict:
            diff_keys=list()
            oldkeys = old.keys()
            newkeys = new.keys()
            for k in oldkeys:
                if new.get(k,'') != old[k]:
                    diff_keys.append(k)
            if len(diff_keys) > 0:
                self.printline('    DELTA:  ' + str(diff_keys) + ' fields mismatch')
                self.printline('    POSTED: ' + str(old))
                self.printline('    RECVD:  ' + str(new))
            return diff_keys
        return []
    
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
                start_time = datetime.datetime.now()
                try:
                    try:
                        text = self.generateRequest(url, 'POST', data).decode()
                    except:
                        text = self.generateRequest(url, 'POST', data)
                    data = json.loads(text)
                    self.tests_passed += 1
                    end_time = datetime.datetime.now()
                    td = end_time - start_time
                    elapsed_time = td.total_seconds()
                    self.printline('PASS: POST ' + url)
                    self.log(True, url, 'POST', str(elapsed_time))
                    delta = self.check_difference(data, object_graph)
                    return data
                except:
                    end_time = datetime.datetime.now()
                    td = end_time - start_time
                    elapsed_time = td.total_seconds()
                    self.log(False, url, 'POST', str(elapsed_time))
                    self.printline('FAIL: POST ' + url)
                    self.printline('    TRACE: ' + traceback.format_exc())
            else:
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
        start_time = datetime.datetime.now()
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
                    end_time = datetime.datetime.now()
                    td = end_time - start_time
                    elapsed_time = td.total_seconds()
                    self.log(True, url, 'POST', str(elapsed_time))
                    self.tests_passed += 1
                    self.printline('PASS: POST ' + url)
                    data = json.loads(text)
                    return data
                except:
                    end_time = datetime.datetime.now()
                    td = end_time - start_time
                    elapsed_time = td.total_seconds()
                    self.log(False, url, 'POST', str(elapsed_time))
                    self.printline('FAIL: POST ' + url)
                    self.printline('    TRACE: ' + traceback.format_exc())
            else:
                text = self.generateRequest(url, 'POST', data)
                data = json.loads(text)
                return data
        else:
            raise Exception('object graph must be a Python dictionary')
        
    def cruds(self, object_type, object_id, object_graph, repetitions=10, file_handle=None):
        """
        This is a test method which goes through the create, update, read, delete cycle for
        an object. It repeats the process N times, and logs the average response time for
        each endpoint. 
        """
        r = 0
        timer = dict()
        
        print('TESTING ' + object_type + ' v' + self.version)
        
        while r < repetitions:
            # test read method
            st = datetime.datetime.now()
            self.tests_run += 1
            try:
                self.tests_passed += 1
                objects = self.read(object_type)
            except:
                pass
            et = datetime.datetime.now()
            td = et - st
            timer['read'] = timer.get('read',0.0) + td.total_seconds()
            
            st = datetime.datetime.now()
            self.tests_run += 1
            try:
                object_graph = self.create(object_type, object_graph)
                self.tests_passed += 1
            except:
                pass
            et = datetime.datetime.now()
            td = et - st
            timer['create'] = timer.get('create', 0.0) + td.total_seconds()

            st = datetime.datetime.now()
            self.tests_run += 1
            try:
                object_graph = self.update(object_type, object_graph)
                self.tests_passed += 1
            except:
                pass
            et = datetime.datetime.now()
            td = et - st
            timer['update'] = timer.get('update', 0.0) + td.total_seconds()

            st = datetime.datetime.now()
            self.tests_run += 1
            try:
                self.delete(object_type, object_graph[object_id])
                self.tests_passed += 1
            except:
                pass
            et = datetime.datetime.now()
            td = et - st
            timer['delete'] = timer.get('delete', 0.0) + td.total_seconds()
            
            r += 1
        
        tkeys = timer.keys()
        for k in tkeys:
            timer[k] = timer[k] / float(repetitions)
            if file_handle is not None:
                line = '"' + str(self.version) + '","' + object_type + '","' + k + '","' + str(timer[k]) + '"\n'
                file_handle.write(line)
        
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
        start_time = datetime.datetime.now()
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
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(True, url, 'DELETE', str(elapsed_time))
                self.printline('PASS: DELETE ' + url)
                self.tests_passed += 1
            except:
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(False, url, 'DELETE', str(elapsed_time))
                self.printline('FAIL: DELETE ' + url)
                self.printline('    TRACE: ' + traceback.format_exc())
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

    def generateRequest(self, url, method, data, alt_auth=None, test=False, headers=None, response='body'):
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
        text = ''
        if method == 'GET' or method == 'PUT' or method == 'DELETE' or method == 'POST':
            valid_method = True
        else:
            raise Exception('parameter method must be GET|DELETE|PUT|UPDATE')
        # generate full URL from base url and relative url
        full_url = self.baseurl + url
        # self.printline('URL:  ' + full_url)
        request = urllib2.Request(full_url)
        if self.gzip:
            request.add_header("Accept-Encoding", "gzip")
        if alt_auth is not None:
            request.add_header("Authorization", self.alt_header)
        else:
            if self.version == 'mobile':
                base64string = str(base64.b64encode(self.apikey + ':FromInsightlyMobileApp'))
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
        if response == 'headers':
            return result.info().headers
        else:
            return text
        
    def get(self, object_type, id, sub_type=None, test=False):
        """
        Returns a single Insightly object, for example to call /contacts/{id} to get a single
        contact. Returns a Python dictionary
        """
        start_time = datetime.datetime.now()
        url = '/' + object_type + '/' + str(id)
        if sub_type is not None:
            url += '/' + sub_type
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
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.tests_passed += 1
                self.printline('PASS: GET ' + url)
                self.log(True, url, 'GET', str(elapsed_time))
                try:
                    results = json.loads(text)
                except:
                    results = json.loads(text.decode('utf-8'))
                return results
            except:
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(False, url, 'GET', str(elapsed_time))
                self.printline('FAIL: GET ' + url)
                self.printline('    TRACE: ' + traceback.format_exc())
        else:
            text = self.generateRequest(url, 'GET', '')
            try:
                results = json.loads(text)
            except:
                results = json.loads(text.decode('utf-8'))
            return results
        
    def get_all(self, object_type, updated_after_utc='', ids_only=True):
        """
        Iterates through the entire recordset for an object type, optionally filtered by updated_after_utc,
        returns a list of object IDs if ids_only is True
        """
        if self.version == '2.2':
            done = False
            skip = 0
            top = 500
            results = list()
            updated_after_utc = string.replace(updated_after_utc,' ','+')
            while not done:
                if updated_after_utc != '':
                    records = self.search(object_type, 'updated_after_utc=' + updated_after_utc, top=top, skip=skip)
                else:
                    records = self.read(object_type, '', top=top, skip=skip)
                if self.debug:
                    print('Search top ' + str(top) + ' ' + object_type + ' after ' + str(skip) + ' since ' + updated_after_utc + ' found ' + str(len(records)))
                skip += top
                for r in records:
                    if ids_only:
                        if object_type == 'contacts':
                            object_id = r['CONTACT_ID']
                        elif object_type == 'emails':
                            object_id = r['EMAIL_ID']
                        elif object_type == 'events':
                            object_id = r['EVENT_ID']
                        elif object_type == 'leads':
                            object_id = r['LEAD_ID']
                        elif object_type == 'notes':
                            object_id = r['NOTE_ID']
                        elif object_type == 'opportunities':
                            object_id = r['OPPORTUNITY_ID']
                        elif object_type == 'organisations':
                            object_id = r['ORGANISATION_ID']
                        elif object_type == 'projects':
                            object_id = r['PROJECT_ID']
                        elif object_type == 'tasks':
                            object_id = r['TASK_ID']
                        elif object_type == 'users':
                            object_id = r['USER_ID']
                        else:
                            object_id = None
                        if object_id is not None:
                            if object_id not in results:
                                results.append(object_id)
                    else:
                        results.append(r)
                if len(records) < 1:
                    done = True
            return results
        else:
            raise Exception('get_all() is only supported for version 2.2 and mobile APIs')
    
    def getMethods(self, test=False):
        """
        Returns a list of the callable methods in this library.
        """
        methods = [method for method in dir(self) if callable(getattr(self, method))]
        return methods
    
    def load(self, object_type, refresh=False):
        """
        Loads objects into memory, either from a local file (JSON) or reloads all objects from
        the Insightly server, to allow offline processing.
        
        # TODO: add logic to do partial updates using the most recent date_updated_utc timestamp
        """
        if refresh:
            records = self.get_all(object_type, ids_only = False)
            try:
                os.mkdir('insightly_data')
            except:
                pass
            f = open('insightly_data/' + object_type + '.json', 'w')
            f.write(json.dumps(records))
            f.close()
        else:
            f = open(object_type + '.json', 'r')
            records = json.loads(f.read())
            f.close()
        return records
    
    def log(self, success, url, method, duration):
        if self.log_file is not None:
            f = self.log_file
            if success:
                success = 'PASS'
            else:
                success = 'FAIL'
            f.write('"' + success + '","' + url + '","' + method + '","' + duration + '"\n')
        
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
        if str(self.version) == '2.2' or self.version == 'mobile':
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
                            querystring += '&' + urlencode(filters)
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

    def offline_query(self, object_type, filters):
        """
        This function is used to query the offline data store (if you instantiate the Insightly class with offline=True, it will
        download a copy of all Insightly objects and cache them in memory)
        
        It is called as follows:
        offline_query(object_type, filters)
        
        Example:
        
        i = Insightly(offline=True)
        records = i.offline_query('contacts',[('FIRST_NAME','contains','foo'),('LAST_NAME','contains','bar')])
        for r in records:
            do_something_with(r)
        
        Note:
        
        Filter expressions are tuples in the form (parm, operator, value)
        
        The following operators are recognized:
        
        = : parm=value
        contains : parm contains value
        < : less than
        > : greater than
        
        You can pass in a single filter, or a list of multiple filters
        
        You can also search to see if any field in a record contains a string with the filter expression:
        
        ('any','contains','foo')
        
        """
        if type(object_type) is str:
            object_type = string.lower(object_type)
        else:
            raise Exception('parameter object_type must be a string')
        if type(filters) is tuple:
                if len(filters) == 3:
                    filters = [filters]
                else:
                    raise Exception('filters tuple length must be 3, expected (parm, operator, value)')
        elif type(filters) is list:
            for f in filters:
                if type(f) is tuple:
                    if len(f) != 3:
                        raise Exception('all filter expressions must be a tuple in (parm, operator, value) form')
                else:
                    raise Exception('all filter expressions must be a tuple in (parm, operator, value) form')
        else:
            raise Exception('filters should be passed in either as a tuple in (parm, operator, value) form, or list of tuples')
        
        if object_type == 'contacts' or object_type == 'contact':
            data = self.contacts
        elif object_type == 'events' or object_type == 'event':
            data = self.events
        elif object_type == 'leads' or object_type == 'lead':
            data = self.leads
        elif object_type == 'organisations' or object_type == 'organisation' or object_type == 'organizations' or object_type == 'organization':
            data = self.organisations
        elif object_type == 'opportunities' or object_type == 'opportunity':
            data = self.opportunities
        elif object_type == 'projects' or object_type == 'project':
            data = self.projects
        elif object_type == 'tasks' or object_type == 'task':
            data = self.tasks
        else:
            raise Exception('Invalid object type')
        
        results = list()
        for d in data:
            matches = 0
            for f in filters:
                parm = f[0]
                operator = f[1]
                value = f[2]
                if string.lower(parm) == 'any':
                    field = str(d)
                else:
                    field = d.get(parm, None)
                if field is not None:
                    if operator == 'contains':
                        if string.count(string.lower(field), string.lower(value)) > 0:
                            matches +=1
                    elif operator == '=':
                        if string.lower(field) == string.lower(value):
                            matches += 1
                    elif operator == '>':
                        if string.lower(field) > string.lower(value):
                            matches += 1
                    elif operator == '<':
                        if string.lower(field) > string.lower(value):
                            matches += 1
                    else:
                        pass
            if matches == len(filters):
                results.append(d)
        return results
        
    def ownerinfo(self):
        """
        :return: dictionary of information about the account owner
        """
        return {
            'name': self.owner_name,
            'email': self.owner_email,
            'contact_id': self.contact_id,
            'email_dropbox': self.email_dropbox,
        }
            
    def printline(self, text):
        if lowercase(text).count('fail') > 0:
            self.test_failures.append(text)
        if self.debug:        print(text)
        if self.test:         self.filehandle.write(text + '\n')
        
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
                start_time = datetime.datetime.now()
                text = self.generateRequest(url,'GET','')
                self.tests_passed += 1
                self.printline('PASS: GET ' + url)
                try:
                    results = self.dictToList(json.loads(text))
                except:
                    results = self.dictToList(json.loads(text.decode('utf-8')))
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(True, url, 'GET', str(elapsed_time))
                return results
            except:
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(False, url, 'GET', str(elapsed_time))
                self.printline('FAIL: GET ' + url)
                self.printline('    TRACE: ' + traceback.format_exc())
        else:
            text = self.generateRequest(url, 'GET', '')
            try:
                results = self.dictToList(json.loads(text))
            except:
                results = self.dictToList(json.loads(text.decode('utf-8')))
            return results
        
    def record_count(self, object_type, id=None, sub_type=None):
        if object_type == 'comments':
            record_id = 'COMMENT_ID'
        elif object_type == 'contacts':
            record_id = 'CONTACT_ID'
        elif object_type == 'emails':
            record_id = 'EMAIL_ID'
        elif object_type == 'events':
            record_id = 'EVENT_ID'
        elif object_type == 'leads':
            record_id = 'LEAD_ID'
        elif object_type == 'notes':
            record_id = 'NOTE_ID'
        elif object_type == 'organisations':
            record_id = 'ORGANISATION_ID'
        elif object_type == 'opportunities':
            record_id = 'OPPORTUNITY_ID'
        elif object_type == 'projects':
            record_id = 'PROJECT_ID'
        elif object_type == 'tasks':
            record_id = 'TASK_ID'
        else:
            record_id = 'ID'
        num_records = 0
        url = '/' + object_type + '?count_total=true'
        headers = self.generateRequest(url, 'GET', None, response='headers')
        for h in headers:
            pv = string.split(h, ':')
            if len(pv) > 1:
                parm = pv[0]
                value = pv[1]
                if string.count(parm, 'Total-Count') > 0:
                    num_records = int(string.strip(value))
        if num_records > 0:
            skip = 0
            records_found = 0
            last_id = 0
            if self.version == 'mobile':
                done = False
                while not done:
                    if skip > 0:
                        url = '/' + object_type + '?top=500&id_after=' + str(last_id)
                    else:
                        url = '/' + object_type + '?top=500'
                    response = self.generateRequest(url, 'GET', None)
                    records = json.loads(response)
                    records_found += len(records)
                    if len(records) < 1:
                        done = True
                    else:
                        skip += 500
                        last_id = records[len(records) - 1][record_id]
                self.printline('FOUND ' + str(records_found) + ' of ' + str(num_records) + ' expected ' + object_type)
            else:
                return
        
    def search(self, object_type, expression, top=100, skip=0, expect=0):
        """
        This implements an easier to use search function, where before we
        used optional parameters for the read function. This is still supported
        but users are encouraged to use this function instead.
        
        USAGE
        
        contacts = i.search('contacts', 'email=foo@bar.com', top=100, filters={'OWNER_USER_ID':'foo'})
        
        PARAMETERS
        
        expression : a parm=value pair for an allowed server side filter (e.g. phone=415551212)
        top : return the first N entries
        skip : skip N entries (for pagination)
        """
        if self.version != '2.2':
            raise Exception('search() is only supported in v2.2 API')
        start_time = datetime.datetime.now()
        test = self.test
        url = '/' + object_type + '/search?top=' + str(top)
        if skip > 0:
            url += '&skip=' + str(skip)
        if string.count(expression,'=') > 0:
            parms = string.split(expression,'=')
            if len(parms) == 2:
                parm = parms[0]
                parm = parm.encode('ascii','xmlcharrefreplace')
                value = encode_query(parms[1])
                url += '&' + parm + '=' + value
        if test:
            self.tests_run += 1
            try:
                self.generateRequest(url, 'GET', '', alt_auth = 'borkborkborkborkbork')
                self.printline('FAIL: GET/SEARCH w/ bad auth ' + url)
            except:
                self.tests_passed += 1
                self.printline('PASS: GET/SEARCH w/ bad auth ' + url)
        if test:
            self.tests_run += 1
            try:
                text = self.generateRequest(url,'GET','')
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(True, url, 'GET', str(elapsed_time))
                self.printline('PASS: GET/SEARCH ' + url)
                try:
                    results = self.dictToList(json.loads(text))
                except:
                    results = self.dictToList(json.loads(text.decode('utf-8')))
                if expect == 0:
                    if len(results) < 1:
                        raise Exception('No records found, assume search test failed.')
                else:
                    if len(results) != expect:
                        raise Exception('Incorrect number of results found, assume search test failed.')
                self.tests_passed += 1
                return results
            except:
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(False, url, 'GET', str(elapsed_time))
                self.printline('FAIL: GET/SEARCH ' + url)
                self.printline(    'TRACE: ' + traceback.format_exc())
                return []
        else:
            text = self.generateRequest(url, 'GET', '')
            try:
                results = self.dictToList(json.loads(text))
            except:
                results = self.dictToList(json.loads(text.decode('utf-8')))
            return results
        
    def stats(self):
        """
        Returns current record counts (for offline mode)
        """
        return dict(
            activity_sets = len(self.activity_sets),
            contacts = len(self.contacts),
            emails = len(self.emails),
            events = len(self.events),
            file_categories = len(self.file_categories),
            leads = len(self.leads),
            lead_sources = len(self.lead_sources),
            lead_statuses = len(self.lead_statuses),
            notes = len(self.notes),
            organisations = len(self.organisations),
            opportunities = len(self.opportunities),
            opportunity_categories = len(self.opportunity_categories),
            opportunity_state_reasons = len(self.opportunity_state_reasons),
            pipelines = len(self.pipelines),
            pipeline_stages = len(self.pipeline_stages),
            projects = len(self.projects),
            project_categories = len(self.project_categories),
            relationships = len(self.relationships),
            tasks = len(self.tasks),
            task_categories = len(self.task_categories),
            teams = len(self.teams),
        )
        
    def sync(self, refresh=False):
        """
        Does a one-way sync (from Insightly to locale file system) to update the local object store.
        This function creates a JSON file for each object type, which is then used for local filter
        and query operations.
        
        TODO: add incremental update using last update timestamp, but for now just load everything
        """
        #
        # First sync contacts
        #
        
        self.activity_sets = self.load('activitysets', refresh)
        self.contacts = self.load('contacts', refresh)
        self.emails = self.load('emails', refresh)
        self.events = self.load('events', refresh)
        self.file_categories = self.load('filecategories', refresh)
        self.leads = self.load('leads', refresh)
        self.lead_sources = self.load('leadsources', refresh)
        self.lead_statuses = self.load('leadstatuses', refresh)
        self.notes = self.load('notes', refresh)
        self.organisations = self.load('organisations')
        self.opportunities = self.load('opportunities')
        self.opportunity_categories = self.load('opportunitycategories', refresh)
        self.opportunity_state_reasons = self.load('opportunitystatereasons', refresh)
        self.pipelines = self.load('pipelines', refresh)
        self.pipeline_stages = self.load('pipelinestages', refresh)
        self.projects = self.load('projects')
        self.project_categories = self.load('projectcategories', refresh)
        self.relationships = self.load('relationships', refresh)
        self.tasks = self.load('tasks', refresh)
        self.task_categories = self.load('taskcategories', refresh)
        self.teams = self.load('teams', refresh)
        
        return True
        
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
        start_time = datetime.datetime.now()
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
                try:
                    self.tests_run += 1
                    date_updated_utc = object_graph['DATE_UPDATED_UTC']
                except:
                    date_updated_utc = None
                self.tests_run += 1
                try:
                    try:
                        text = self.generateRequest(url, 'PUT', data).decode()    
                    except:
                        text = self.generateRequest(url, 'PUT', data)
                    end_time = datetime.datetime.now()
                    td = end_time - start_time
                    elapsed_time = td.total_seconds()
                    self.log(True, url, 'PUT', str(elapsed_time))
                    data = json.loads(text)
                    self.printline('PASS: PUT ' + url)
                    self.tests_passed += 1
                    if date_updated_utc is not None:
                        try:
                            if date_updated_utc != data['DATE_UPDATED_UTC']:
                                self.tests_passed += 1
                                self.printline('PASS: ' + object_type + ' DATE_UPDATED_UTC updated')
                            else:
                                self.printline('FAIL: ' + object_type + ' DATE_UPDATED_UTC not updated')
                        except:
                            pass
                    return data
                except:
                    end_time = datetime.datetime.now()
                    td = end_time - start_time
                    elapsed_time = td.total_seconds()
                    self.log(False, url, 'PUT', str(elapsed_time))
                    self.printline('FAIL: PUT ' + url)
                    self.printline(    'TRACE: ' + traceback.format_exc())
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
        start_time = datetime.datetime.now()
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
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(True, url, 'POST', str(elapsed_time))
                self.printline('PASS: UPLOAD ' + url)
                self.tests_passed += 1
                return json.loads(text)
            except:
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(False, url, 'POST', str(elapsed_time))
                self.printline('FAIL: UPLOAD ' + url)
                self.printline(    'TRACE: ' + traceback.format_exc())
        else:
            try:
                text = self.generateRequest(url, 'POST', body, headers=headers).decode()
            except:
                text = self.generateRequest(url, 'POST', body, headers=headers)
            return json.loads(text)
    
    def upload_image(self, object_type, id, filename):
        start_time = datetime.datetime.now()
        test = self.test
        f = open(filename, 'rb')
        value = f.read()
        # TODO: probably need to clean the filename so it does not have illegal characters
        url = '/' + object_type + '/' + str(id) + '/image/' + os.path.basename(filename)
        if test:
            self.tests_run += 1
            try:
                self.generateRequest(url, 'PUT', value)
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(True, url, 'PUT', str(elapsed_time))
                self.printline('PASS: UPLOAD IMAGE: ' + url)
                self.tests_passed += 1
            except:
                end_time = datetime.datetime.now()
                td = end_time - start_time
                elapsed_time = td.total_seconds()
                self.log(False, url, 'PUT', str(elapsed_time))
                self.printline('FAIL: UPLOAD IMAGE: ' + url)
                self.printline(    'TRACE: ' + traceback.format_exc())
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
