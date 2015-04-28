#
# NOTE: the version 2.2 API is NOT in production yet, use the v2.1 library in the default branch. We are making this branch available
# for beta testers, but it is not ready for production use yet.
#
# NOTE to .NET developers, it is best if you edit this file in a Python aware IDE. Komodo IDE is a good choice. .NET tends to break
# indentation in Python fields, which will cause bugs.
#
# Python client library for v2.1/v2.2 Insightly API
# Brian McConnell <brian@insight.ly>
#

import base64
import datetime
import json
import string
import urllib
import urllib2

class Insightly():
    """
    Insightly Python library for Insightly API v2.1/v2.2
    Brian McConnell <brian@insight.ly>
   
    This library provides user friendly access to the versions 2.1 and 2.2 of the REST API for Insightly. The library provides several services, including:
   
    * HTTPS request generation
    * Data type validation
   
    The library is built using Python standard libraries (no third party tools required, so it will run out of the box on most Python
    environments, including Google App Engine). The wrapper functions return native Python objects, typically dictionaries, or lists of
    dictionaries, so working with them is easily done using built in functions.
    
    The version 2.2 API adds several new endpoints which make it easy to make incremental changes to existing Insightly objects, such
    as to add a phone number to a contact, and also more closely mirrors the functionality available in the web app (such as the
    ability to follow and unfollow objects.s)
    
    IMPORTANT NOTE
    
    This version of the client library is not backward compatible with the previous version. In order to simplify the code base, and
    enable better test coverage, this library is organized around a small number of general purpose methods that implement create,
    read, update and delete functionality generically. The previous version of the library has one method per endpoint, per HTTP method,
    which grew unwieldy with the addition of many new endpoints in v2.1
   
    USAGE:
   
    Simply include insightly.py in your project file, then do the following for to run a test suite:
   
    from insightly import Insightly
    i = Insightly(apikey='your API key', version='2.2')
    users = i.test()
    
    NOTE: you can also store your API key in a text file named apikey.txt that is placed in the working directory along with insightly.py
   
    This will run an automatic test suite against your Insightly account. If the methods you need all pass, you're good to go!
   
    If you are working with very large recordsets, you should use ODATA filters to access data in smaller chunks. This is a good idea in
    general to minimize server response times.
   
    BASIC USE PATTERNS:
    
    i = Insightly(apikey = 'foozlebarzle', version=2.1)
    projects = i.read('projects')
    print 'Found ' + str(len(projects)) + ' projects'
    
    The create() function enables you to create an Insightly object, or append a new sub_object, such as an address, to an object

    The delete() function enables you to delete Insightly objects
    
    The fields() function returns a list of the fields expected for a given object

    The read() function enables you to get/find Insightly objects, with optional OData query terms    
    
    The update() function enables you to update an existing Insightly object
    
    INTERACTIVE DOCUMENTATION
    
    Use Python's built in help() function to pull up documentation for individual methods.
    
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
    def __init__(self, apikey='', version='2.1', dev =None):
	"""
	Instantiates the class, logs in, and fetches the current list of users. Also identifies the account owner's user ID, which
	is a required field for some actions. This is stored in the property Insightly.owner_id

	Raises an exception if login or call to getUsers() fails, most likely due to an invalid or missing API key
	"""
	
	#
	# Define available object types, their endpoints, sample data for POST/PUT tests, etc
	#
	self.object_types = [{'object_type':'contact','endpoint':'contacts','object_id':'CONTACT_ID',
				    'example':{'FIRST_NAME':'Testy','LAST_NAME':'McTesterson','SALUTATION':'Mr'},
				    'v21_sub_types':['emails','notes','tasks','image']},
			    {'object_type':'country','endpoint':'countries','object_id':None},
			    {'object_type':'currency','endpoint':'currencies','object_id':None},
			    {'object_type':'customfield','endpoint':'customfields','object_id':'CUSTOM_FIELD_ID'},
			    {'object_type':'email','endpoint':'emails','object_id':'EMAIL_ID',
				    'v21_sub_types':['comments']},
			    {'object_type':'event','endpoint':'events','object_id':'EVENT_ID','example':{'TITLE':'Example Event','START_DATE_UTC':'2015-08-15 14:30:00','END_DATE_UTC':'2015-08-15 15:30:00','PUBLICLY_VISIBLE':True}},
			    {'object_type':'filecategory','endpoint':'filecategories','object_id':'CATEGORY_ID',
				    'example':{'CATEGORY_NAME':'Foozle','ACTIVE':True,'BACKGROUND_COLOR':'000000'}},
			    {'object_type':'lead','endpoint':'leads','object_id':'LEAD_ID',
				    'example':{'FIRST_NAME':'Foozle','LAST_NAME':'McBarzle'},
				    'v21_sub_types':['emails','notes','tasks']},
			    {'object_type':'leadsource','endpoint':'leadsources','object_id':'LEAD_SOURCE_ID',
				    'example':{'LEAD_SOURCE':'Example Lead Source'}},
			    {'object_type':'leadstatus','endpoint':'leadstatuses','object_id':'LEAD_STATUS_ID',
				    'example':{'LEAD_STATUS':'Example Lead Status'}},
			    {'object_type':'note','endpoint':'notes','object_id':'NOTE_ID'},
			    {'object_type':'opportunity','endpoint':'opportunities','object_id':'OPPORTUNITY_ID'},
			    {'object_type':'opportunitycategory','endpoint':'opportunitycategories','object_id':'CATEGORY_ID'},
			    {'object_type':'opportunitystatereason','endpoint':'opportunitystatereasons','object_id':None},
			    {'object_type':'organisation','endpoint':'organisations','object_id':'ORGANISATION_ID'},
			    {'object_type':'pipeline','endpoint':'pipelines','object_id':'PIPELINE_ID'},
			    {'object_type':'pipelinestage','endpoint':'pipelinestages','object_id':'STAGE_ID'},
			    {'object_type':'projectcategory','endpoint':'projectcategories','object_id':'CATEGORY_ID'},
			    {'object_type':'project','endpoint':'projects','object_id':'PROJECT_ID'},
			    {'object_type':'relationship','endpoint':'relationships','object_id':None},
			    {'object_type':'tag','endpoint':'tags','object_id':None},
			    {'object_type':'task','endpoint':'tasks','object_id':'TASK_ID'},
			    {'object_type':'teammember','endpoint':'teammembers','object_id':'PERMISSION_ID'},
			    {'object_type':'teams','endpoint':'teams','object_id':'TEAM_ID'},
			    {'object_type':'users','endpoint':'users','object_id':'USER_ID'}			    ]
	
	self.sub_types = ['addresses','contactinfos','emails','events','links']
	
        if dev:
            self.domain = 'https://api.insightly' + dev + '.com/v'
        else:
            self.domain = 'https://api.insight.ly/v'
	self.baseurl = self.domain + version
	self.test_data = dict()
        self.testmode = False
        if len(apikey) < 1:
            try:
                f = open('apikey.txt', 'r')
                apikey = f.read()
                print 'API Key read from disk as ' + apikey
            except:
                pass
        version = str(version)
        self.version = version
        if version == '2.2' or version == '2.1':
            self.alt_header = 'Basic '
            self.apikey = apikey
            self.tests_run = 0
            self.tests_passed = 0
            if version == '2.1':
                self.users = self.read('users')
                self.version = version
                print 'CONNECTED: found ' + str(len(self.users)) + ' users'
                for u in self.users:
                    if u.get('ACCOUNT_OWNER', False):
                        self.owner_email = u.get('EMAIL_ADDRESS','')
                        self.owner_id = u.get('USER_ID', None)
                        self.owner_name = u.get('FIRST_NAME','') + ' ' + u.get('LAST_NAME','')
                        print 'The account owner is ' + self.owner_name + ' [' + str(self.owner_id) + '] at ' + self.owner_email
                        break
            else:
                self.version = version
                print 'ASSUME connection proceeded, not all endpoints are implemented yet'
                self.owner_email = ''
                self.owner_id = 0
                self.owner_name = ''
        else:
            raise Exception('Python library only supports v2.1 or v2.2 APIs')
	
    def create(self, object_type, object_graph, id = None, sub_type = None):
	"""
	This is a general purpose write method that can be used to create (POST)
	Insightly objects. 
	"""
	object_type = string.lower(object_type)
	if type(object_graph) is dict:
	    data = json.dumps(object_graph)
	    url = '/' + object_type
	    if id is not None:
		url += '/' + str(id)
		if sub_type is not None:
		    url += '/' + sub_type
	    text = self.generateRequest(url, 'POST', data)
	    data = json.loads(text)
	    return data
	else:
	    raise Exception('object_graph must be a Python dictionary')
	
    def delete(self, object_type, id, sub_type=None, subtype_id = None):
	"""
	This is a general purpose delete method that will allow the user to delete Insightly
	objects (e.g. contacts) and sub_objects (e.g. delete a contact_info linked to an object)
	"""
	object_type = string.lower(object_type)
	url = '/' + object_type
	if id is not None:
	    url += '/' + str(id)
	    if sub_type is not None:
		url += '/' + sub_type
		if sub_type_id is not None:
		    url += '/' + str(sub_type_id)
	object_type = string.lower(object_type)
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
            return list()
        else:
            return list()
	
    def fields(self, object_type):
	"""
	This function returns a list of the fields associated with an Insightly object.
	See the documentation at https://api.insight.ly/v2.2/Help for full documentation
	on required fields, formats, etc. 
	"""
	object_type = string.lower(object_type)
	url = '/' + object_type
	text = self.generateRequest(url, 'GET', '')
	results = json.loads(text)
	fieldlist = list()
	if len(results) > 0:
	    result = results[0]
	    keys = result.keys()
	    return keys
	
    def findUser(self, email):
	"""
	Client side function to quickly look up Insightly users by email. Returns a dictionary containing
	user details or None if not found. This is useful when you need to find the user ID for someone but
	only know their email addresses, for example when creating and assigning a new project or task. 
	"""
	for u in self.users:
	    if u.get('EMAIL_ADDRESS','') == email:
		return u

    def generateRequest(self, url, method, data, alt_auth=None, test=False):
        """
        This method is used by other helper functions to generate HTTPS requests and parse
        server responses. This will minimize the amount of work developers need to do to
        integrate with the Insightly API, and will also eliminate common sources of errors
        such as authentication issues and malformed requests. Uses the urllib2 standard
        library, so it is not dependent on third party libraries like Requests
        """
        if self.testmode:
            self.tests_run += 1
            # run a series of sanity checks to verify authentication, etc
            try:
                self.generateTestRequest(url, method, data, alt_auth = 'borkborkborkborkbork')
                print 'FAIL: bad auth credentials not detected for ' + url
            except:
                self.tests_passed += 1
                print 'PASS: bad auth credentials detected for ' + url
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
        full_url = self.baseurl + url
        if self.version == '2.2':
            print 'URL: ' + full_url
        request = urllib2.Request(full_url)
        if alt_auth is not None:
            request.add_header("Authorization", self.alt_header)
        else:
            base64string = base64.encodestring('%s:%s' % (self.apikey, '')).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)   
        request.get_method = lambda: method
        request.add_header('Content-Type', 'application/json')
        # open the URL, if an error code is returned it should raise an exception
        if method == 'PUT' or method == 'POST':
            result = urllib2.urlopen(request, data)
        else:
            result = urllib2.urlopen(request)
        text = result.read()
        return text
    
    def generateTestRequest(self, url, method, data, alt_auth=None, content_type = None):
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
        full_url = self.baseurl + url
        if self.version == '2.2':
            print 'URL: ' + full_url
        request = urllib2.Request(full_url)
        if alt_auth is not None:
            request.add_header("Authorization", self.alt_header)
        else:
            base64string = base64.encodestring('%s:%s' % (self.apikey, '')).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
        request.get_method = lambda: method
        if content_type is not None:
            request.add_header('Content-Type', content_type)
        else:
            request.add_header('Content-Type', 'application/json')
        # open the URL, if an error code is returned it should raise an exception
        if method == 'PUT' or method == 'POST':
            result = urllib2.urlopen(request, data)
        else:
            result = urllib2.urlopen(request)
        text = result.read()
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
        """
        #
        # TODO: double check that this has been implemented correctly
        #
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
	
    def read(self, object_type, id = None, sub_type=None, top=None, skip=None, orderby=None, filters=None):
	"""
	This is a general purpose read method that will allow the user to easily fetch Insightly objects.
	This will replace the hand built request handlers, which are too numerous to test and support
	adequately.
	
	USAGE:
	
	i = Insightly(version=2.1, api_key='foozlebarzle')
	projects = i.read('projects')
	for p in projects:
	    print str(p)
	"""
	object_type = string.lower(object_type)
	url = '/' + object_type
	if id is not None:
	    url += '/' + str(id)
	    if sub_type is not None:
		url += '/' + sub_type
	object_type = string.lower(object_type)
	url += self.ODataQuery('',top=top, skip=skip, orderby=orderby, filters=filters)
	text = self.generateRequest(url, 'GET', '')
	return self.dictToList(json.loads(text))
    
    def test(self, section=None):
        """
        This helper function runs a test suite against the API to verify the API and client side methods are working normally.
        This may not reveal all corner cases, but will do a basic sanity check against the system.
        
        USAGE:
        
        i = Insightly()
        i.test()        # run test suite, with no limit on number of records returned by search functions   
        """
	
	endpoints = self.object_types
	self.tests_run = 0
	
	# do basic get all query for each object type
	
	if section is None or section == 'get':
	
	    print "Test v2.1 GET Endpoints"
	    
	    skip_endpoints = ['comments','fileattachments','tags']
	    
	    for e in endpoints:
		if e['object_type'] not in skip_endpoints:
		    self.tests_run += 1
		    try:
			data = self.read(e['endpoint'])
			self.tests_passed += 1
			print 'PASS: GET ' + self.baseurl + '/' + e['endpoint']
			if len(data) > 0:
			    data = data[0]
			if e['object_id'] is not None:
			    self.tests_run += 1
			    id = data[e['object_id']]
			    try:
				data = self.read(e['endpoint'], id)
				self.tests_passed += 1
				print 'PASS: GET ' + self.baseurl + '/' + e['endpoint'] + '/' + str(id)
				v21_sub_types = e.get('v21_sub_types', None)
				if v21_sub_types is not None:
				    for s in v21_sub_types:
					self.tests_run += 1
					try:
					    data = self.read(e['endpoint'], id, s)
					    print 'PASS: GET ' + self.baseurl + '/' + e['endpoint'] + '/' + str(id) + '/' + s
					    self.tests_passed += 1
					except:
					    print 'FAIL: GET ' + self.baseurl + '/' + e['endpoint'] + '/' + str(id) + '/' + s
			    except:
				print 'FAIL: GET ' + self.baseurl + '/' + e['endpoint'] + '/' + str(id)
		    except:
			print 'FAIL: GET ' + self.baseurl + '/' + e['endpoint']
			
	if section is None or section == 'post':
	    
	    print "Test v2.1 POST endpoints"
	    
	    for e in self.object_types:
		data = e.get('example',None)
		if data is not None:
		    endpoint = e.get('endpoint',None)
		    if endpoint is not None:
			self.tests_run += 1
			url = endpoint
			data = self.create(endpoint, data)
			self.tests_passed += 1
			print 'PASS: POST ' + self.baseurl + '/' + url
			if data is not None:
			    id = data.get(e['object_id'], None)
			    if id is not None:
				self.tests_run += 1
				self.delete(endpoint, id)
				print 'PASS: DELETE ' + self.baseurl + '/' + url + '/' + endpoint + '/' + str(id)
				self.tests_passed += 1
				#except:
				#    print 'FAIL: DELETE ' + self.baseurl + url + '/' + endpoint + '/' + str(id)
			#except:
			#    print 'FAIL: POST ' + self.baseurl + '/' + url
	print str(self.tests_passed) + ' of ' + str(self.tests_run) + ' tests passed'
	
    def update(self, object_type, object_graph, id = None, sub_type = None):
	"""
	This is a general purpose write method that can be used to update (PUT)
	Insightly objects. 
	"""
	object_type = string.lower(object_type)
	if type(object_graph) is dict:
	    data = json.dumps(object_graph)
	    url = '/' + object_type
	    if id is not None:
		url += '/' + str(id)
		if sub_type is not None:
		    url += '/' + sub_type
	    text = self.generateRequest(url, 'PUT', data)
	    data = json.loads(text)
	    return data
	else:
	    raise Exception('object_graph must be a Python dictionary')
	