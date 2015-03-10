#
# NOTE: the version 2.2 API is NOT in production yet, use the v2.1 library in the default branch. We are making this branch available
# for beta testers, but it is not ready for production use yet.
#
# NOTE to .NET developers, it is best if you edit this file in a Python aware IDE. Komodo IDE is a good choice. .NET tends to break
# indentation in Python fields, which will cause bugs.
#
# Python client library for v2.1 Insightly API
# Brian McConnell <brian@insight.ly>
#

import base64
import json
import string
import urllib
import urllib2

class Insightly():
    """
    Insightly Python library for Insightly API v2.2
    Brian McConnell <brian@insight.ly>
   
    This library provides user friendly access to the version 2.2 REST API for Insightly. The library provides several services, including:
   
    * HTTPS request generation
    * Data type validation
    * Required field validation
   
    The library is built using Python standard libraries (no third party tools required, so it will run out of the box on most Python
    environments, including Google App Engine). The wrapper functions return native Python objects, typically dictionaries, or lists of
    dictionaries, so working with them is easily done using built in functions.
    
    The version 2.2 API adds several new endpoints which make it easy to make incremental changes to existing Insightly objects, such
    as to add a phone number to a contact, and also more closely mirrors the functionality available in the web app (such as the
    ability to follow and unfollow objects.s)
   
    USAGE:
   
    Simply include insightly.py in your project file, then do the following for to run a test suite:
   
    from insightly import Insightly
    i = Insightly(apikey='your API key')
    users = i.test()
   
    This will run an automatic test suite against your Insightly account. If the methods you need all pass, you're good to go!
   
    If you are working with very large recordsets, you should use ODATA filters to access data in smaller chunks. This is a good idea in
    general to minimize server response times.
   
    BASIC USE PATTERNS:
   
    CREATE/UPDATE ACTIONS
   
    These methods expect a dictionary containing valid data fields for the object. They will return a dictionary containing the object
    as stored on the server (if successful) or raise an exception if the create/update request fails. You indicate whether you want to
    create a new item by setting the record id to 0 or omitting it.
   
    To obtain sample objects, you can do the following:
   
    contact = i.addContact('sample')
    event = i.addEvent('sample')
    organization = i.addOrganization('sample')
    project = i.addProject('sample')
   
    This will return a random item from your account, so you can see what fields are required, along with representative field values.
   
    SEARCH ACTIONS
   
    These methods return a list of dictionaries containing the matching items. For example to request a list of all contacts, you call:
    i = Insightly(apikey='your API key')
    contacts = i.getContacts()
   
    SEARCH ACTIONS USING ODATA
   
    Search methods recognize top, skip, orderby and filters parameters, which you can use to page, order and filter recordsets.
   
    contacts = i.getContacts(top=200) # returns the top 200 contacts
    contacts = i.getContacts(orderby='FIRST_NAME desc', top=200) # returns the top 200 contacts, with first name descending order
    contacts = i.getContacts(top=200, skip=200) # return 200 records, after skipping the first 200 records
    contacts = i.getContacts(filters=['FIRST_NAME=\'Brian\''])    # get contacts where FIRST_NAME='Brian'
   
    IMPORTANT NOTE: when using OData filters, be sure to include escaped quotes around the search term, otherwise you will get a
    400 (bad request) error
   
    These methods will raise an exception if the lookup fails, or return a list of dictionaries if successful, or an empty list if no
    records were found.
   
    READ ACTIONS (SINGLE ITEM)
   
    These methods will return a single dictionary containing the requested item's details.
    e.g. contact = i.getContact(123456)
   
    DELETE ACTIONS
   
    These methods will return True if successful, or raise an exception.
    e.g. success = i.deleteContact(123456)
   
    IMAGE AND FILE ATTACHMENT MANAGEMENT
   
    The API calls to manage images and file attachments have not yet been implemented in the Python library. However you can access
    these directly via our REST API
   
    ISSUES TO BE AWARE OF
   
    This library makes it easy to integrate with Insightly, and by automating HTTPS requests for you, eliminates the most common causes
    of user issues. That said, the service is picky about rejecting requests that do not have required fields, or have invalid field values
    (such as an invalid USER_ID). When this happens, you'll get a 400 (bad request) error. Your best bet at this point is to consult the
    API documentation and look at the required request data.
   
    Write/update methods also have a dummy feature that returns sample objects that you can use as a starting point. For example, to
    obtain a sample task object, just call:
   
    task = i.addTask('sample')
   
    This will return one of the tasks from your Insightly account, so you can get a sense of the fields and values used.
   
    If you are working with large recordsets, we strongly recommend that you use ODATA functions, such as top and skip to page through
    recordsets rather than trying to fetch entire recordsets in one go. This both improves client/server communication, but also minimizes
    memory requirements on your end.
    
    TROUBLESHOOTING TIPS
    
    One of the main issues API users run into during write/update operations is a 400 error (bad request) due to missing required fields.
    If you are unclear about what the server is expecting, a good way to troubleshoot this is to do the following:
    
    * Using the web interface, create the object in question (contact, project, team, etc), and add sample data and child elements to it
    * Use the corresponding getNNNN() method to retrieve this object via the web API
    * Inspect the object's contents and structure
    
    Read operations via the API are generally quite straightforward, so if you get struck on a write operation, this is a good workaround,
    as you are probably just missing a required field or using an invalid element ID when referring to something such as a link to a contact.
    """
    def __init__(self, apikey='', version='2.2'):
	"""
	Instantiates the class, logs in, and fetches the current list of users. Also identifies the account owner's user ID, which
	is a required field for some actions. This is stored in the property Insightly.owner_id

	Raises an exception if login or call to getUsers() fails, most likely due to an invalid or missing API key
	"""
        if version == '2.2' or version == '2.1':
            self.alt_header = 'Basic '
            self.apikey = apikey
            self.baseurl = 'https://api.insight.ly/' + version
            self.users = self.getUsers()
            self.version = version
            self.tests_run = 0
            self.tests_passed = 0
            print 'CONNECTED: found ' + str(len(self.users)) + ' users'
            for u in self.users:
                if u.get('ACCOUNT_OWNER', False):
                    self.owner_email = u.get('EMAIL_ADDRESS','')
                    self.owner_id = u.get('USER_ID', None)
                    self.owner_name = u.get('FIRST_NAME','') + ' ' + u.get('LAST_NAME','')
                    print 'The account owner is ' + self.owner_name + ' [' + str(self.owner_id) + '] at ' + self.owner_email
                    break
        else:
            raise Exception('Python library only supports v2.1 or v2.2 (default) APIs')
                
    def getMethods(self):
        """
        Returns a list of the callable methods in this library.
        """
        methods = [method for method in dir(self) if callable(getattr(self, method))]
        return methods
    
    def test(self, top=None):
        """
        TODO: make this a lot less verbose, move test script into methods themselves
        
        This helper function runs a test suite against the API to verify the API and client side methods are working normally. This may not reveal all corner cases, but will do a basic sanity check against the system.
        
        USAGE:
        
        i = Insightly()
        i.test(top=500)         # run test suite, limit search methods to return first 500 records
        i.test(top=None)        # run test suite, with no limit on number of records returned by search functions   
        """
        
        print "Testing API ....."
        
        print "Testing authentication"
        
        passed = 0
        failed = 0
        
        currencies = self.getCurrencies()
        if len(currencies) > 0:
            print "Authentication passed... "
            passed += 1
        else:
            failed += 1
        # Test getUsers(), /v2.2/Users, also get root user to use in testing write/update calls
        # Test getUsers(), /v2.2/Users
        try:
            users = self.getUsers()
            user = users[0]
            user_id = user['USER_ID']
            print "PASS: getUsers(), found " + str(len(users)) + " users."
            passed += 1
        except:
            user = None
            users = None
            user_id = None
            print "FAIL: getUsers()"
            failed += 1
        
        # getAccount
        accounts = self.getAccount(test = True)
        
        #
        # getContacts
        try:
            contacts = self.getContacts(orderby='DATE_UPDATED_UTC desc', top=top)
            contact = contacts[0]
            print 'PASS: getContacts(), found ' + str(len(contacts)) + ' contacts.'
        except:
            contact = None
            print 'FAIL: getContacts()'
        if contact is not None:
            contact_id = contact['CONTACT_ID']
            try:
                emails = self.getContactEmails(contact_id)
                print 'PASS: getContactEmails(), found ' + str(len(emails)) + ' emails for random contact.'
            except:
                print 'FAIL: getContactEmails()'
                
            try:
                notes = self.getContactNotes(contact_id)
                print 'PASS: getContactNotes(), found ' + str(len(notes)) + ' notes for random contact.'
            except:
                print 'FAIL: getContactNotes()'
                
            try:
                tasks = self.getContactTasks(contact_id)
                print 'PASS: getContactTasks(), found ' + str(len(tasks)) + ' tasks for random contact.'
            except:
                print 'FAIL: getContactTasks()'
            
        # Test addContact(), /v2.2/Contacts
        try:
            contact = dict(
                SALUTATION = 'Mr',
                FIRST_NAME = 'Testy',
                LAST_NAME = 'McTesterson',
            )
            contact = self.addContact(contact)
            print "PASS: addContact()"
            try:
                self.deleteContact(contact['CONTACT_ID'])
                print 'PASS: deleteContact()'
            except:
                print 'FAIL: deleteContact()'
        except:
            contact = None
            print "FAIL: addContact()"
                    
        # Test getCountries(), /v2.2/Countries
        try:
            countries = self.getCountries()
            print 'PASS: getCountries(), found ' + str(len(countries)) + ' countries.'
        except:
            print 'FAIL: getCountries()'
            
        # Test getCurrencies(), /v2.2/Currencies
        try:
            currencies = self.getCurrencies()
            print 'PASS: getCurrencies(), found ' + str(len(currencies)) + ' currencies.'
        except:
            print 'FAIL: getCurrencies()'
            
        # Test getCustomFields(), /v2.2/CustomFields
        try:
            customfields = self.getCustomFields()
            print 'PASS: getCustomFields(), found ' + str(len(customfields)) + ' custom fields.'
        except:
            print 'FAIL: getCustomFields()'
            
        # Test getEmails(), /v2.2/Emails
        try:
            emails = self.getEmails(top=top)
            print 'PASS: getEmails(), found ' + str(len(emails)) + ' emails.'
        except:
            print 'FAIL: getEmails()'
            
        # Try getEmail(), /v2.2/Emails/{id}
        pass
    
        # Test getEvents(), /v2.2/Events
        try:
            events = self.getEvents(top=top)
            print 'PASS: getEvents(), found ' + str(len(events)) + ' events.'
        except:
            print 'FAIL: getEvents()'
        
        # Test addEvent(), /2.1/Events
        try:
            event = dict(
                TITLE = 'Test Event',
                LOCATION = 'Somewhere',
                DETAILS = 'Details',
                START_DATE_UTC = '2014-07-12 12:00:00',
                END_DATE_UTC = '2014-07-12 13:00:00',
                OWNER_USER_ID = user_id,
                ALL_DAY = False,
                PUBLICLY_VISIBLE = True,
            )
            event = self.addEvent(event)
            print 'PASS: addEvent()'
        except:
            event = None
            print 'FAIL: addEvent()'
            
        # Test deleteEvent(), /v2.2/Events
        if event is not None:
            try:
                self.deleteEvent(event['EVENT_ID'])
                print "PASS: deleteEvent()"
            except:
                print "FAIL: deleteEvent()"
                
        # Test getFileCategories(), /v2.2/FileCategories
        try:
            categories = self.getFileCategories()
            print 'PASS: getFileCategories(), found ' + str(len(categories)) + ' file categories.'
        except:
            print 'FAIL: getFileCategories()'
            
        # Test addFileCategory()
        try:
            category = dict(
                CATEGORY_NAME = 'Test Category',
                ACTIVE = True,
                BACKGROUND_COLOR = '000000',
            )
            category = self.addFileCategory(category)
            print 'PASS: addFileCategory()'
        except:
            category = None
            print 'FAIL: addFileCategory()'
            
        try:
            if category is not None:
                self.deleteFileCategory(category['CATEGORY_ID'])
                print 'PASS: deleteFileCategory()'
        except:
            print 'FAIL: deleteFileCategory()'
        
        # Test getNotes(), /v2.2/Notes
        try:
            notes = self.getNotes()
            print 'PASS: getNotes(), found ' + str(len(notes)) + ' notes.'
        except:
            print 'FAIL: getNotes()'
            
            
        # Test getOpportunities(), /v2.2/Opportunities
        try:
            opportunities = self.getOpportunities(orderby='DATE_UPDATED_UTC desc', top=top)
            print 'PASS: getOpportunities(), found ' + str(len(opportunities)) + ' opportunities.'
            opportunity = opportunities[0]
        except:
            opportunity = None
            print 'FAIL: getOpportunities()'
            
        # Test getOpportunityCategories(), /v2.2/OpportunityCategories
        try:
            categories = self.getOpportunityCategories()
            print 'PASS: getOpportunityCategories(), found ' + str(len(categories)) + ' categories.'
        except:
            print 'FAIL: getOpportunityCategories()'
            
        # Test addOpportunityCategory()
        try:
            category = dict(
                CATEGORY_NAME = 'Test Category',
                ACTIVE = True,
                BACKGROUND_COLOR = '000000',
            )
            category = self.addOpportunityCategory(category)
            print 'PASS: addOpportunityCategory()'
            self.deleteOpportunityCategory(category['CATEGORY_ID'])
            print 'PASS: deleteOpportunityCategory()'
        except:
            print 'FAIL: addOpportunityCategory()'
            print 'FAIL: deleteOpportunityCategory()'
        
        # Test getOpportunityEmails()
        if opportunity is not None:
            try:
                emails = self.getOpportunityEmails(opportunity['OPPORTUNITY_ID'])
                print 'PASS: getOpportunityEmails(), found ' + str(len(emails)) + ' emails for random opportunity.'
            except:
                print 'FAIL: getOpportunityEmails()'
                
            # Test getOpportunityNotes()
            
            try:
                notes = self.getOpportunityNotes(opportunity['OPPORTUNITY_ID'])
                print 'PASS: getOpportunityNotes(), found ' + str(len(notes)) + ' notes for random opportunity.'
            except:
                print 'FAIL: getOpportunityNotes()'
        
            # Test getOpportunityTasks()
            try:
                tasks = self.getOpportunityTasks(opportunity['OPPORTUNITY_ID'])
                print 'PASS: getOpportunityTasks(), found ' + str(len(tasks)) + ' tasks for random opportunity.'
            except:
                print 'FAIL: getOpportunityTasks()'
        
            # Test getOpportunityStateHistory(), /v2.2/OpportunityStates
            try:
                states = self.getOpportunityStateHistory(opportunity['OPPORTUNITY_ID'])
                print 'PASS: getOpportunityStateHistory(), found ' + str(len(states)) + ' states in history.'
            except:
                print 'FAIL: getOpportunityStateHistory()'
            
        # Test getOpportunityStateReasons(), /v2.2/OpportunityStateReasons
        try:
            reasons = self.getOpportunityStateReasons()
            print 'PASS: getOpportunityStateReasons(), found ' + str(len(reasons)) + ' reasons.'
        except:
            print 'FAIL: getOpportunityStateReasons()'
            
        # Test getOrganizations(), /v2.2/Organizations
        
        try:
            organizations = self.getOrganizations(top=top, orderby='DATE_UPDATED_UTC desc')
            organization = organizations[0]
            print 'PASS: getOrganizations(), found ' + str(len(organizations))
            
            # Test getOrganizationEmails()
            try:
                emails = self.getOrganizationEmails(organization['ORGANISATION_ID'])
                print 'PASS: getOrganizationEmails(), found ' + str(len(emails)) + ' emails for most recent organization.'
            except:
                print 'FAIL: getOrganizationEmails()'
            # Test getOrganizationNotes()
            try:
                notes = self.getOrganizationNotes(organization['ORGANISATION_ID'])
                print 'PASS: getOrganizationNotes(), found ' + str(len(notes)) + ' notes for most recent organization.'
            except:
                print 'FAIL: getOrganizationNotes()'
            # Test getOrganizationTasks()
            try:
                tasks = self.getOrganizationTasks(organization['ORGANISATION_ID'])
                print 'PASS: getOrganizationTasks(), found ' + str(len(tasks)) + ' tasks for most recent organization.'
            except:
                print 'FAIL: getOrganizationTasks()'
        except:
            print 'FAIL: getOrganizations()'
            
        # Test addOrganization()
        try:
            organization = dict(
                ORGANISATION_NAME = 'Foo Corp',
                BACKGROUND = 'Details',
            )
            organization = self.addOrganization(organization)
            print 'PASS: addOrganization()'
            try:
                self.deleteOrganization(organization['ORGANISATION_ID'])
                print 'PASS: deleteOrganization()'
            except:
                print 'FAIL: deleteOrganization()'
        except:
            print 'FAIL: addOrganization()'\
            
        # Test getPipelines(), /v2.2/Pipelines
        try:
            pipelines = self.getPipelines()
            print 'PASS: getPipelines(), found ' + str(len(pipelines)) + ' pipelines'
        except:
            print 'FAIL: getPipelines()'
            
        try:
            stages = self.getPipelineStages()
            print 'PASS: getPipelineStages(), found ' + str(len(stages)) + ' pipeline stages'
        except:
            print 'FAIL: getPipelineStages()'
        
        # Test getProjects(), /v2.2/Projects
        try:
            projects = self.getProjects(top=top, orderby='DATE_UPDATED_UTC desc')
            project = projects[0]
            project_id = project['PROJECT_ID']
            print 'PASS: getProjects(), found ' + str(len(projects)) + ' projects.'
            # Test getProjectEmails()
            try:
                emails = self.getProjectEmails(project_id)
                print 'PASS: getProjectEmails(), found ' + str(len(emails)) + ' emails for most recent project.'
            except:
                print 'FAIL: getProjectEmails()'
            # Test getProjectNotes()
            try:
                notes = self.getProjectNotes(project_id)
                print 'PASS: getProjectNotes(), found ' + str(len(notes)) + ' notes for most recent project.'
            except:
                print 'FAIL: getProjectNotes()'
            # Test getProjectTasks()
            try:
                tasks = self.getProjectTasks(project_id)
                print 'PASS: getProjectTasks(), found ' + str(len(tasks)) + ' tasks for most recent project.'
            except:
                print 'FAIL: getProjectTasks()'
        except:
            print 'FAIL: getProjects()'
            
        # Test getProjectCategories(), /v2.2/ProjectCategories
        try:
            categories = self.getProjectCategories()
            print 'PASS: getProjectCategories(), found ' + str(len(categories)) + ' categories.'
        except:
            print 'FAIL: getProjectCategories()'
            
        # Test addProjectCategory()
        try:
            category = dict(
                CATEGORY_NAME = 'Test Category',
                ACTIVE = True,
                BACKGROUND_COLOR = '000000',
            )
            category = self.addProjectCategory(category)
            print 'PASS: addProjectCategory()'
            self.deleteProjectCategory(category['CATEGORY_ID'])
            print 'PASS: deleteProjectCategory()'
        except:
            print 'FAIL: addProjectCategory()'
            print 'FAIL: deleteProjectCategory()'
            
        # Test getRelationships(), /v2.2/Relationships
            
        try:
            relationships = self.getRelationships()
            print 'PASS: getRelationships(), found ' + str(len(relationships)) + ' relationships.'
        except:
            print 'FAIL: getRelationships()'
        
        # Test getTasks(), /v2.2/Tasks
        try:
            tasks = self.getTasks(top=top, orderby='DUE_DATE desc')
            print 'PASS: getTasks(), found ' + str(len(tasks)) + ' tasks.'
        except:
            print 'FAIL: getTasks()'
            
        # Test getTeams
        try:
            teams = self.getTeams()
            team = teams[0]
            print 'PASS: getTeams(), found ' + str(len(teams)) + ' teams.'
            # Test getTeamMembers
            try:
                team_members = self.getTeamMembers(team['TEAM_ID'])
                print 'PASS: getTeamMembers(), found ' + str(len(team_members)) + ' team members.'
            except:
                print 'FAIL: getTeamMembers()'
        except:
            print 'FAIL: getTeams()'
        
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
	
    def findUser(self, email):
	"""
	Client side function to quickly look up Insightly users by email. Returns a dictionary containing
	user details or None if not found. This is useful when you need to find the user ID for someone but
	only know their email addresses, for example when creating and assigning a new project or task. 
	"""
	for u in self.users:
	    if u.get('EMAIL_ADDRESS','') == email:
		return u
	    
    def generateRequest(self, url, method, data, alt_auth=None):
        """
        This method is used by other helper functions to generate HTTPS requests and parse
        server responses. This will minimize the amount of work developers need to do to
        integrate with the Insightly API, and will also eliminate common sources of errors
        such as authentication issues and malformed requests
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
        full_url = self.baseurl + url
        
        request = urllib2.Request(full_url)
        if alt_auth is not None:
            request.add_header("Authorization", self.alt_header)
        else:
            base64string = base64.encodestring('%s:%s' % (self.apikey, '')).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)   
        request.get_method = lambda: method
        # open the URL, if an error code is returned it should raise an exception
        if method == 'PUT' or method == 'POST':
            request.add_header('Content-Type', 'application/json')
            result = urllib2.urlopen(request, data)
        else:
            result = urllib2.urlopen(request)
        if result.status_code == 200 or result.status_code == 201:
            text = result.read()
            return text
        elif result.status_code == 400:
            raise Exception('400 : Bad request')
        elif result.status_code == 401:
            raise Exception('401 : Authentication error')
        elif result.status_code == 403:
            raise Exception('403 : Forbidden / permission denied')
        elif result.status_code == 404:
            raise Exception('404 : Object not found')
        elif result.status_code == 405:
            raise Exception('405 : Method not supported')
        elif result.status_code == 500:
            raise Exception('500 : System error')
        else:
            raise Exception('Unknown error')
    
    def ODataQuery(self, querystring, top=None, skip=None, orderby=None, filters=None):
        """
        This helper function generates an OData compatible query string. It is used by many
        of the search functions to enable users to filter, page and order recordsets.
        """
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
        
    def getAccount(self, email=None, test=False):
        """
        Find which account is associated with the current API key, this endpoint will most likely be renamed to Instance
        """
        if test:
            try:
                text = self.generateRequest('/Accounts', 'GET', '')
                accounts = json.loads(text)
                print 'PASS getAccount() : Found ' + len(accounts) + ' linked to this instance'
                self.tests_run += 1
                self.tests_passed += 1
            except:
                print 'FAIL getAccount()'
                self.tests_run += 1
        else:
            if email is not None:
                text = self.generateRequest('/Accounts?email=' + email, 'GET','', alt_auth=self.alt_header)
            else:
                text = self.generateRequest('/Accounts', 'GET', '')
            return json.loads(text)
    
    def deleteComment(self, id):
        """
        Delete a comment, expects the comment's ID (unique record locator).
        """
        text = self.generateRequest('/Comments/' + str(id), 'DELETE','')
        return True

    def getComments(self, id):
        """
        Gets comments for an object. Expects the parent object ID.
        """
        #
        # HTTP GET api.insight.ly/v2.2/Comments
        #
        text = self.generateRequest('/Comments/' + str(id), 'GET', '')
        return json.loads(text)
    
    def updateComment(self, body, owner_user_id, comment_id=None):
        """
        Creates or updates a comment. If you are updating an existing comment, be sure to include the comment_id
        """
        if len(body) < 1:
            raise Exception('Comment body cannot be empty')
            return
        if type(owner_user_id) is not int:
            raise Exception('owner_user_id must be an integer, and must be a valid user id')
        data = dict(
            BODY = body,
            OWNER_USER_ID = owner_user_id,
        )
        if comment_id is not None and type(comment_id) is int:
            data['COMMENT_ID'] = comment_id
        urldata = urllib.urlencode(data)
        text = self.generateRequest('/Comments', 'PUT', urldata)
        return json.loads(text)
    
    def addContact(self,  contact):
        """
        Add/update a contact on Insightly. The parameter contact should be a dictionary containing valid data fields
        for a contact, or the string 'sample' to request a sample object. When submitting a new contact, set the
        CONTACT_ID field to 0 or omit it.
        """
        if type(contact) is str:
            if contact == 'sample':
                contacts = self.getContacts(top=1)
                return contacts[0]
            else:
                raise Exception('contact must be a dictionary with valid contact data fields, or the string \'sample\' to request a sample object')
        else:
            if type(contact) is dict:
                if contact.get('CONTACT_ID', 0) > 0:
                    text = self.generateRequest('/Contacts', 'PUT', json.dumps(contact))
                else:
                    text = self.generateRequest('/Contacts', 'POST', json.dumps(contact))
                return json.loads(text)
            else:
                raise Exception('contact must be a dictionary with valid contact data fields, or the string \'sample\' to request a sample object')
            
    def addContactAddress(self, contact_id, address):
        """
        Add/update an address linked to a contact in Insightly.
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        if type(address) is dict:
            # validate data
            at = string.lower(address.get('TYPE',''))
            if at == 'work' or at == 'home' or at == 'postal' or at == 'other':
                address_id = address.get('ADDRESS_ID', None)
                if address_id is not None:
                    text = self.generateRequest('/Contacts/' + str(contact_id) + '/Addresses', 'PUT', json.dumps(address))
                else:
                    text = self.generateRequest('/Contacts/' + str(contact_id) + '/Addresses', 'POST',json.dumps(address))
                return json.loads(text)
            else:
                raise Exception('TYPE must be home, work, postal or other')
        else:
            raise Exception('address must be a dictionary')
    
    def addContactContactInfo(self, contact_id, contactinfo):
        """
        Add/update a contact info linked to a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for v2.2 API')
        if type(contactinfo) is dict:
            # validate data
            ct = string.lower(contactinfo.get('TYPE',''))
            if ct == 'phone' or ct == 'email' or ct == 'pager' or ct == 'fax' or ct == 'website' or ct == 'other':
                contact_info_id = contactinfo.get('CONTACT_INFO_ID', None)
                if contact_info_id is not None:
                    text = self.generateRequest('/Contacts/' + str(contact_id) + '/ContactInfos', 'PUT', json.dumps(contactinfo))
                else:
                    text = self.generateRequest('/Contacts/' + str(contact_id) + '/ContactInfos', 'POST', json.dumps(contactinfo))
                return json.loads(text)
            else:
                raise Exception('TYPE must be phone, email, pager, fax, website or other')
        else:
            raise Exception('contactinfo must be a dictionary')
        
    def addContactEvent(self, contact_id, event):
        """
        Add an event to a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        if type(event) is dict:
            event_id = event.get('EVENT_ID', None)
            if event_id is not None:
                text = self.generateRequest('/Contacts/' + str(contact_id) + '/Events', 'PUT', json.dumps(event))
            else:
                text = self.generateRequest('/Contacts/' + str(contact_id) + '/Events', 'POST', json.dumps(event))
        else:
            raise Exception('event must be a dictionary')
        
    def addContactFileAttachment(self, contact_id, file_attachment):
        """
        Add/update a file attachment for a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        if type(file_attachment) is dict:
            file_attachment_id = file_attachment.get('FILE_ATTACHMENT_ID', None)
            if file_attachment_id is not None:
                text = self.generateRequest('/Contacts/' + str(contact_id) + '/FileAttachments', 'PUT', json.dumps(file_attachment))
            else:
                text = self.generateRequest('/Contacts/' + str(contact_id) + '/FileAttachments', 'POST', json.dumps(file_attachment))
            return json.loads(text)
        else:
            raise Exception('file_attachment must be a dictionary')
        
    def addContactFollow(self, contact_id):
        """
        Start following a contact
        """
        if self.version != '2.2':
            raise Exception('method only support for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Follow', 'POST', '')
        return True
    
    def addContactTags(self, contact_id, tags):
        """
        Delete a tag(s) from a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        if type(tags) is list:
            pass
        elif type(tags) is str:
            tags = string.split(tags,',')
        else:
            raise Exception('tags must either be a string or a list of strings')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Tags', 'POST', json.dumps(tags))
        return json.loads(text)
        
    def deleteContact(self, contact_id):
        """
        Deletes a comment, identified by its record id
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id), 'DELETE', '')
        return True
    
    def deleteContactAddress(self, contact_id, address_id):
        """
        Delete an address linked to a contact in Insightly.
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(xcontact_id) + '/Addresses/' + str(address_id), 'DELETE', '')
        return True
    
    def deleteContactContactInfo(self, contact_id, contact_info_id):
        """
        Delete a contact info from a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/ContactInfos/' + str(contact_info_id), 'DELETE', '')
        return True
    
    def deleteContactEvent(self, contact_id, event_id):
        """
        Delete an event from a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Events/' + str(event_id), 'DELETE', '')
        return True
    
    def deleteContactFileAttachment(self, contact_id, file_attachment_id):
        """
        Delete a file attachment from a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/FileAttachments/' + str(file_attachment_id), 'DELETE', '')
        return True
    
    def deleteContactFollow(self, contact_id):
        """
        Stop following a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Follow', 'DELETE','')
        return True
    
    def deleteContactTags(self, contact_id, tag):
        """
        Delete tags from a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        pass
    
    def getContacts(self, ids=None, email=None, tag=None, filters=None, top=None, skip=None, orderby=None):
        """
        Get a list of matching contacts, expects the following optional parameters:
        
        ids = list of contact IDs
        email = user's email address
        tag = tag or keyword
        
        In addition, this method also supports OData operators:
        
        top = return only the first N records in the recordset
        skip = skip the first N records in the recordset
        orderby = e.g. 'LAST_NAME desc'
        filters = a list of filter statements
        
        Example:
        
        i = Insightly()
        contacts = i.getContacts(top=200,filters=['FIRST_NAME=\'Brian\''])
        
        It returns a list of dictionaries or raises an exception in the case of a malformed server response
        """
        if ids is not None and type(ids) is not list:
            raise Exception('parameter ids must be a list')
        if email is not None and type(email) is not str:
            raise Exception('parameter email must be a string')
        if tag is not None and type(tag) is not str:
            raise Exception('parameter tag must be a string')
        if filters is not None and type(filters) is not list:
            raise Exception('parameter filters must be a list')
        querystring = self.ODataQuery('', top=top, skip=skip, orderby=orderby, filters=filters)
        if email is not None:
            querystring += '?email=' + email
        if tag is not None:
            if querystring == '':
                querystring += '?tag=' + tag
            else:
                querystring += '&tag=' + tag
        if ids is not None and len(ids) > 0:
            if querystring == '':
                querystring += '?ids='
            else:
                querystring += '&ids='
            for i in ids:
                querystring += i + ','
        text = self.generateRequest('/Contacts' + querystring, 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getContact(self, contact_id):
        """
        Gets a specific contact, identified by its record id
        """
        # Do lazy exception handling, returns True if all goes well, otherwise raises whatever exception caused the issue
        text = self.generateRequest('/Contacts/' + str(contact_id), 'GET','')
        return json.loads(text)
        
    def getContactAddresses(self, contact_id):
        """
        Get addresses linked to a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Addresses', 'GET', '')
        return json.loads(text)
    
    def getContactContactInfos(self, contact_id):
        """
        Get ContactInfos linked to a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/ContactInfos', 'GET', '')
        return json.loads(text)
        
    def getContactEmails(self, contact_id):
        """
        Gets emails for a contact, identified by its record locator, returns a list of dictionaries
        """
        #
        # Get a contact's emails
        #
        # HTTP GET api.insight.ly/v2.2/Contacts/{id}/Emails
        #
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Emails', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getContactEvents(self, contact_id):
        """
        Gets events linked to a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Events', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getContactFileAttachments(self, contact_id):
        """
        Gets files attached to a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/FileAttachments', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getContactNotes(self, contact_id):
        """
        Gets a list of the notes attached to a contact, identified by its record locator. Returns a list of dictionaries.
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Notes', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getContactTags(self, contact_id):
        """
        Gets a list of tags linked to a contact
        """
        if self.version != '2.2':
            raise Exception('method only supported for version 2.2 API')
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Tags', 'GET', '')
        return self.dictToList(json.loads(text))
        
    def getContactTasks(self, contact_id):
        """
        Gets a list of the tasks attached to a contact, identified by its record locator. Returns a list of dictionaries.
        """
        text = self.generateRequest('/Contacts/' + str(contact_id) + '/Tasks', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getCountries(self):
        """
        Gets a list of countries recognized by Insightly. Returns a list of dictionaries.
        """
        text = self.generateRequest('/Countries', 'GET', '')
        countries = json.loads(text)
        return countries
    
    def getCurrencies(self):
        """
        Gets a list of currencies recognized by Insightly. Returns a list of dictionaries.
        """
        text = self.generateRequest('/Currencies', 'GET', '')
        currencies = json.loads(text)
        return currencies
    
    def getCustomFields(self):
        """
        Gets a list of custom fields, returns a list of dictionaries
        """
        text = self.generateRequest('/CustomFields', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getCustomField(self, id):
        """
        Gets details for a custom field, identified by its record id. Returns a dictionary
        """
        text = self.generateRequest('/CustomFields/' + str(id), 'GET', '')
        return json.loads(text)
    
    def getEmails(self, top=None, skip=None, orderby=None, filters=None):
        """
        Returns a list of emails for a resource id.
        
        This search method supports the OData operators: top, skip, orderby and filters
        """
        querystring = self.ODataQuery('', top=top, skip=skip, orderby=orderby, filters=None)
        text = self.generateRequest('/Emails' + querystring, 'GET','')
        return self.dictToList(json.loads(text))
        
    def getEmail(self, id):
        """
        Returns an invidivual email, identified by its record locator id
        
        Returns a dictionary as a response or raises an exception
        """
        text = self.generateRequest('/Emails/' + str(id), 'GET', '')
        return json.loads(text)
        
    def deleteEmail(self,id):
        """
        Deletes an individual email, identified by its record locator id
        
        Returns True or raises an exception
        """
        text = self.generateRequest('/Emails/' + str(id), 'DELETE', '')
        return True
    
    def getEmailComments(self, id):
        """
        Returns the comments attached to an email, identified by its record locator id
        """
        text = self.generateRequest('/Emails/' + str(id) + '/Comments')
        return self.dictToList(json.loads(text))
        
    def addCommentToEmail(self, id, body, owner_user_id):
        """
        Adds a comment to an existing email, identified by its record locator id.
        
        The comment parameter is a dictionary containing the following fields:
        
        TODO: getting 400 responses, needed to debug
        """
        data = dict(
            BODY = body,
            OWNER_USER_ID = owner_user_id,
        )
        urldata = json.dumps(data)
        text = self.generateRequest('/Emails/' + str(id) + '/Comments', 'POST', urldata)
        return json.loads(text)
    
    def addEvent(self, event):
        """
        Add/update an event in the calendar.
        
        NOTE: owner_user_id is required, and must point to a valid Insightly user id, if not you will get
        a 400 (bad request) error.
        """
        if type(event) is str:
            if event == 'sample':
                events = self.getEvents(top=1)
                return events[0]
        elif type(event) is dict:
            if event.get('EVENT_ID',0) > 0:
                text = self.generateRequest('/v2.2/Events', 'PUT', json.dumps(event))
            else:
                text = self.generateRequest('/v2.2/Events', 'POST', json.dumps(event))
            return json.loads(text)
        else:
            raise Exception('The parameter event should be a dictionary with valid fields for an event object, or the string \'sample\' to request a sample object.')
    
    def deleteEvent(self, id):
        """
        Deletes an event, identified by its record id
        """
        text = self.generateRequest('/Events/' + str(id), 'DELETE', '')
        return True
        
    def getEvents(self, top=None, skip=None, orderby=None, filters=None):
        """
        Gets a calendar of upcoming events.
        
        This method supports OData filters:
        
        top = return first N records
        skip = skip the first N records
        orderby = order results, e.g.: orderby='START_DATE_UTC desc'
        filters = list of filters, e.g.: ['FIRST_NAME=\'Brian\'','LAST_NAME=\'McConnell\'']
        
        List is returned as a list of dictionaries.
        """
        querystring = self.ODataQuery('', top = top, skip=skip, orderby = orderby, filters = filters)
        text = self.generateRequest('/Events' + querystring, 'GET', '')
        return self.dictToList(json.loads(text))
        
    def getEvent(self, id):
        """
        gets an individual event, identified by its record id
        
        Returns a dictionary
        """
        text = self.generateRequest('/Events/' + str(id))
        json.loads(text)
    
    def addFileCategory(self, category, dummy=False):
        """
        Add/update a file category to your account. Expects a dictionary containing the category details.
        
        You can also call addFileCategory('sample') to request a sample object. 
        """
        if type(category) is str:
            if category == 'sample':
                categories = self.getFileCategories()
                return categories[0]
        if type(category) is not dict:
            raise Exception('category must be a dict')
        urldata = json.dumps(category)
        if category.get('CATEGORY_ID',None) is not None:
            text = self.generateRequest('/FileCategories', 'PUT', urldata)
        else:
            text = self.generateRequest('/FileCategories', 'POST', urldata)
        return json.loads(text)
    
    def deleteFileCategory(self, id):
        """
        Delete a file category, identified by its record id
        
        Returns True if successful or raises an exception
        """
        text = self.generateRequest('/FileCategories/' + str(id), 'DELETE', '')
        return True
    
    def getFileCategories(self):
        """
        Gets a list of file categories
        
        Returns a list of dictionaries
        """
        text = self.generateRequest('/FileCategories', 'GET', '')
        return self.dictToList(json.loads(text))
        
    def getFileCategory(self, id):
        """
        Gets a file category, identified by its record id
        
        Returns a dictionary
        """
        text = self.generateRequest('/FileCategories/' + str(id), 'GET', '')
        json.loads(text)
    
    def addNote(self, note):
        """
        Add/update a note, where the parameter note is a dictionary withthe required fields. To obtain a sample object, just call
        
        addNote('sample')
        
        The method returns a dictionary containing the object as it is stored on the server, or raises an exception if the update
        failed. If you receive a 400 (bad request) error it is probably because you are missing a required field, or are linking to
        another record improperly. 
        """
        if type(note) is str:
            if note == 'sample':
                note = self.getNotes(top=1)
                return note[0]
            else:
                raise Exception('note must be a dictionary with valid fields, or the string \'sample\' to request a sample object')
        else:
            if type(note) is dict:
                if note.get('NOTE_ID',0) > 0:
                    text = self.generateRequest('/Notes', 'PUT', json.dumps(note))
                else:
                    text = self.generateRequest('/Notes', 'POST', json.dumps(note))
                return json.loads(text)
    
    def deleteNote(self, id):
        """
        Delete a note, identified by its record locator.
        """
        text = self.generateRequest('/Notes/' + str(id), 'DELETE', '')
        return True
    
    def getNotes(self, top=None, skip=None, orderby=None, filters=None):
        """
        Gets a list of notes created by the user, returns a list of dictionaries
        
        This method supports the ODATA operators:
        
        top = return first N records
        skip = skip first N records
        orderby = order by statement (e.g. 'DATE_CREATED_UTC desc')
        filters = list of filter statements
        """
        querystring = self.ODataQuery('', top=top, skip=skip, orderby=orderby, filters=filters)
        text = self.generateRequest('/Notes' + querystring, 'GET', '')
        return self.dictToList(json.loads(text))
        
    def getNote(self, id):
        """
        Gets a note, identified by its record id. Returns a dictionary or raises an error.
        """
        text = self.generateRequest('/Notes/' + str(id), 'GET', '')
        try:
            return json.loads(text)
        except:
            raise Exception(error_invalid_server_json)
            return
    
    def getNoteComments(self, id):
        """
        Gets the comments attached to a note, identified by its record id. Returns a list of dictionaries.
        """
        text = self.generateRequest('/Notes/' + str(id) + '/Comments', 'GET', '')
        return self.dictToList(json.loads(text))
        
    def addNoteComment(self, id, comment):
        """
        Method not implemented yet
        """
        if type(comment) is str:
            if comment == 'sample':
                comment = dict(
                    COMMENT_ID = 0,
                    BODY = 'This is a comment.',
                    OWNER_USER_ID = 1,
                    DATE_CREATED_UTC = '2014-07-15 16:40:00',
                    DATE_UPDATED_UTC = '2014-07-15 16:40:00',
                )
                return comment
            else:
                raise Exception('The parameter comment should be a dictionary with the required fields, or the string \'sample\' to request a sample object.')
        elif type(comment) is dict:
            text = self.generateRequest('/' + str(id) +'/Comments', 'POST', json.dumps(comment))
            return json.loads(text)
        else:
            raise Exception('The parameter comment should be a dictionary with the required fields, or the string \'sample\' to request a sample object.')
    
    def addOpportunity(self, opportunity):
        """
        Add/update an opportunity in Insightly. This method expects a dictionary containing valid fields for an opportunity, or the string 'sample' to request a sample object. 
        """
        if type(opportunity) is str:
            if opportunity == 'sample':
                opportunities = self.getOpportunities(top=1)
                return opportunities[0]
            else:
                raise Exception('The parameter opportunity must be a dictionary with valid fields for an opportunity, or the string \'sample\' to request a sample object.')
        elif type(opportunity) is dict:
            if opportunity.get('OPPORTUNITY_ID',0) > 0:
                text = self.generateRequest('/Opportunities', 'PUT', json.dumps(opportunity))
            else:
                text = self.generateRequest('/Opportunities', 'POST', json.dumps(opportunity))
            return json.loads(text)
        else:
            raise Exception('The parameter opportunity must be a dictionary with valid fields for an opportunity, or the string \'sample\' to request a sample object.')
    
    def deleteOpportunity(self, id):
        """
        Deletes an opportunity, identified by its record id. Returns True if successful, or raises an exception
        """
        text = self.generateRequest('/Opportunities/' + str(id), 'DELETE', '')
        return True
    
    def getOpportunities(self, ids=None, tag=None, top=None, skip=None, orderby=None, filters=None):
        """
        Gets a list of opportunities
        
        This method recognizes the OData operators:
        top = return the first N records
        skip = skip the first N records
        orderby = orderby clause, e.g.: orderby='DATE_UPDATED_UTC desc'
        filters = list of OData filter statements
        """
        querystring = self.ODataQuery('', top=top, skip=skip, orderby=orderby, filters=filters)
        text = self.generateRequest('/Opportunities' + querystring, 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getOpportunity(self, id):
        """
        Gets an opportunity's details, identified by its record id, returns a dictionary
        """
        text = self.generateRequest('/Opportunities/' + str(id), 'GET', '')
        return json.loads(text)
    
    def getOpportunityStateHistory(self, id):
        """
        Gets the history of states and reasons for an opportunity.
        """
        text = self.generateRequest('/Opportunities/' + str(id) + '/StateHistory', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getOpportunityEmails(self, id):
        """
        Gets the emails linked to an opportunity
        """
        text = self.generateRequest('/Opportunities/' + str(id) + '/Emails', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getOpportunityNotes(self, id):
        """
        Gets the notes linked to an opportunity
        """
        text = self.generateRequest('Opportunities/' + str(id) + '/Notes', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getOpportunityTasks(self, id):
        """
        Gets the tasks linked to an opportunity
        """
        text = self.generateRequest('Opportunities/' + str(id) + '/Tasks', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def addOpportunityCategory(self, category):
        """
        Add/update an opportunity category.
        """
        if type(category) is str:
            if category == 'sample':
                categories = self.getOpportunityCategories()
                return categories[0]
            else:
                raise Exception('category must be a dictionary, or \'sample\' to request a sample object')
        else:
            if category.get('CATEGORY_ID', 0) > 0:
                text = self.generateRequest('OpportunityCategories', 'PUT', json.dumps(category))
            else:
                text = self.generateRequest('OpportunityCategories', 'POST', json.dumps(category))
            return json.loads(text)
    
    def deleteOpportunityCategory(self, id):
        """
        Deletes an opportunity category. Returns True or raises an exception.
        """
        text = self.generateRequest('/OpportunityCategories/' + str(id), 'DELETE', '')
        return True
    
    def getOpportunityCategory(self, id):
        """
        Gets an opportunity category, identified by its record id.
        """
        text = self.generateRequest('/OpportunityCategories/' + str(id), 'GET', '')
        return json.loads(text)
    
    def getOpportunityCategories(self):
        """
        Gets a list of opportunity categories.
        """
        text = self.generateRequest('/OpportunityCategories', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getOpportunityStateReasons(self):
        """
        Gets a list of opportunity state reasons, returns a list of dictionaries
        """
        text = self.generateRequest('OpportunityStateReasons', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def addOrganization(self, organization):
        """
        Add/update an organization.
        
        Expects a dictionary with valid fields for an organization. Returns a dictionary containing the item as stored on the server, or raises an exception.
        
        To request a sample item, call addOrganization('sample')
        """
        if type(organization) is str:
            if organization == 'sample':
                organizations = self.getOrganizations(top=1)
                return organizations[0]
            else:
                raise Exception('The parameter organization must be a dictionary with valid fields for an organization, or the string \'sample\' to request a sample object.')
        elif type(organization) is dict:
            if organization.get('ORGANIZATION_ID', 0) > 0:
                text = self.generateRequest('/Organisations', 'PUT', json.dumps(organization))
            else:
                text = self.generateRequest('/Organisations', 'POST', json.dumps(organization))
            return json.loads(text)
        else:
            raise Exception('The parameter organization must be a dictionary with valid fields for an organization, or the string \'sample\' to request a sample object.')
    
    def deleteOrganization(self, id):
        """
        Delete an organization, identified by its record locator
        """
        text = self.generateRequest('/Organisations/' + str(id), 'DELETE', '')
        return True
    
    def getOrganizations(self, ids=None, domain=None, tag=None, top=None, skip=None, orderby=None, filters=None):
        """
        Gets a list of organizations, returns a list of dictionaries
        
        This method recognizes the OData operators:
        
        top = return the first N filters
        skip = skip the first N filters
        orderby = orderby clause, e.g. orderby='DATE_UPDATED_UTC desc'
        filters = list of OData filter statements
        """
        querystring = ''
        if domain is not None:
            querystring += '?domain=' + urllib.quote_plus(domain)
        if tag is not None:
            if len(querystring) > 0:
                querystring += '&tag=' + urllib.quote_plus(tag)
            else:
                querystring += '?tag=' + urllib.quote_plus(tag)
        if ids is not None:
            ids = string.replace(ids,' ','')
            if len(querystring) > 0:
                querystring += '?ids=' + ids
            else:
                querystring += '&ids=' + ids
        querystring = self.ODataQuery(querystring, top=top, skip=skip, orderby=orderby, filters=filters)
        text = self.generateRequest('/Organisations' + querystring, 'GET', '')
        return self.dictToList(json.loads(text))
        
    def getOrganization(self, id):
        """
        Gets an organization, identified by its record id, returns a dictionary
        """
        text = self.generateRequest('/Organisations/' + str(id), 'GET', '')
        return json.loads(text)
    
    def getOrganizationEmails(self, id):
        """
        Gets a list of emails attached to an organization, identified by its record id, returns a list of dictionaries
        """
        text = self.generateRequest('/Organisations/' + str(id) + '/Emails', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getOrganizationNotes(self, id):
        """
        Gets a list of notes attached to an organization, identified by its record id, returns a list of dictionaries
        """
        text = self.generateRequest('/Organisations/' + str(id) + '/Notes', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getOrganizationTasks(self, id):
        """
        Gets a list of tasks attached to an organization, identified by its record id, returns a list of dictionaries
        """
        text = self.generateRequest('/Organisations/' + str(id) + '/Tasks', 'GET', '')
        return self.dictToList(json.loads(text))
    
    #
    # Following are methods for pipelines
    #
    
    def getPipelines(self):
        """
        Gets a list of pipelines
        """
        text = self.generateRequest('/Pipelines', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getPipeline(self, id):
        """
        Gets details for a pipeline, identified by its unique record id
        """
        text = self.generateRequest('/Pipelines/' + str(id))
        return json.loads(text)
    
    #
    # Following are methods for obtaining pipeline stages
    #
    
    def getPipelineStages(self):
        """
        Gets a list of pipeline stages
        """
        text = self.generateRequest('/PipelineStages','GET','')
        return self.dictToList(json.loads(text))
    
    def getPipelineStage(self, id):
        """
        Gets a pipeline stage, identified by its unique record id
        """
        text = self.generateRequest('/PipelineStages/' + str(id), 'GET','')
        return json.loads(text)
    
    #
    # Following are methods for managing project categories
    #
    
    def getProjectCategories(self):
        """
        Gets a list of project categories
        """
        text = self.generateRequest('/ProjectCategories', 'GET','')
        return self.dictToList(json.loads(text))
    
    def getProjectCategory(self, id):
        """
        Gets a project category, identified by its unique record id
        """
        text = self.generateRequest('/ProjectCategories/' + str(id), 'GET', '')
        return json.loads(text)
    
    def addProjectCategory(self, category):
        """
        Add/update a project category. The parameter category should be a dictionary containing the project category details, or
        the string 'sample' to request a sample object. To add a new project category, just set the CATEGORY_ID to 0 or omit it. 
        """
        if type(category) is str:
            if category == 'sample':
                categories = self.getProjectCategories()
                return categories[0]
            else:
                raise Exception('category must be a dictionary, or \'sample\' to request a sample object')
        else:
            if category.get('CATEGORY_ID', 0) > 0:
                text = self.generateRequest('/ProjectCategories', 'PUT', json.dumps(category))
            else:
                text = self.generateRequest('/ProjectCategories', 'POST', json.dumps(category))
            return json.loads(text)
    
    def deleteProjectCategory(self, id):
        """
        Deletes a project category, returns True if successful or raises an exception
        """
        text = self.generateRequest('/ProjectCategories/' + str(id), 'DELETE', '')
        return True
    
    #
    # Following are methods use to list and manage Insightly projects
    # 
    
    def addProject(self, project):
        """
        Add update a project. The parameter project should be a dictionary containing the project details, or
        the string 'sample', to request a sample object. 
        """
        if type(project) is str:
            if project == 'sample':
                projects = self.getProjects(top=1)
                return projects[0]
            else:
                raise Exception('project must be a dictionary containing valid project data fields, or the string \'sample\' to request a sample object')
        else:
            if project.get('PROJECT_ID', 0) > 0:
                text = self.generateRequest('/Projects', 'PUT', json.dumps(project))
            else:
                text = self.generateRequest('/Projects', 'POST', json.dumps(project))
            return json.loads(text)
    
    def deleteProject(self, id):
        """
        Deletes a project, identified by its record id. Returns True if successful, or raises an exception.
        """
        text = self.generateRequest('/Projects/' + str(id), 'DELETE', '')
        return True
    
    def getProject(self, id):
        """
        Gets a project's details, identified by its record id, returns a dictionary
        """
        text = self.generateRequest('/Projects/' + str(id), 'GET', '')
        return json.loads(text)
    
    def getProjects(self, top=None, skip=None, orderby=None, filters=None):
        """
        Gets a list of projects, returns a list of dictionaries. This method supports the OData operators:
        
        top = return the first N records
        skip = skip the first N records
        orderby = orderby clause, eg. orderby='DATE_UPDATED_UTC desc'
        filters = list of OData filter statements
        """
        querystring = self.ODataQuery('', top=top, skip=skip, orderby=orderby, filters=filters)
        text = self.generateRequest('/Projects' + querystring, 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getProjectEmails(self, id):
        """
        Gets a list of emails attached to a project, identified by its record id, returns a list of dictionaries
        """
        text = self.generateRequest('/Projects/' + str(id) + '/Emails', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getProjectNotes(self, id):
        """
        Gets a list of notes attached to a project, identified by its record id, returns a list of dictionaries
        """
        text = self.generateRequest('/Projects/' + str(id) + '/Notes', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getProjectTasks(self, id):
        """
        Gets a list of tasks attached to a project, identified by its record id, returns a list of dictionaries
        """
        text = self.generateRequest('/Projects/' + str(id) + '/Tasks', 'GET', '')
        return self.dictToList(json.loads(text))
    
    #
    # Following are methods related to relationships between contacts and organizations
    #
    
    def getRelationships(self):
        """
        Gets a list of relationships.
        """
        text = self.generateRequest('/Relationships', 'GET', '')
        return self.dictToList(json.loads(text))
        
    #
    # Following are methods related to tags
    #
    
    def getTags(self, id):
        """
        Gets a list of tags for a parent object
        """
        text = self.generateRequest('/Tags/' + str(id), 'GET', '')
        self.dictToList(json.loads(text))
        
    #
    # Following are methods related to tasks, and items attached to them
    #
    
    def addTask(self, task):
        """
        Add/update a task on Insightly. Submit the task details as a dictionary.
        
        To get a sample dictionary, call addTask('sample')
        
        To add a new task to Insightly, set the TASK_ID to 0. 
        """
        if type(task) is str:
            if task == 'sample':
                tasks = self.getTasks(top=1)
                return tasks[0]
            else:
                raise Exception('task must be a dictionary with valid task data fields, or the string \'sample\' to request a sample object')
        else:
            if task.get('TASK_ID',0) > 0:
                text = self.generateRequest('/Tasks', 'PUT', json.dumps(task))
            else:
                text = self.generateRequest('/Tasks', 'POST', json.dumps(task))
            return json.loads(text)
    
    def deleteTask(self, id):
        """
        Deletes a task, identified by its record ID, returns True if successful or raises an exception
        """
        text = self.generateRequest('/Tasks/' + str(id), 'DELETE', '')
        return True

    def getTasks(self, ids=None, top=None, skip=None, orderby=None, filters=None):
        """
        Gets a list of tasks, expects the optional parameter ids, which contains a list of task ids
        
        This method also recognizes the OData operators:
        
        top = return the first N records
        skip = skip the first N records
        orderby = orderby statement, example 'TITLE desc'
        filters = list of filter statements, example ['TITLE=\'Foo\'', 'BODY=\'Bar\'']
        """
        querystring = self.ODataQuery('', top=top, skip=skip, orderby=orderby, filters=filters)
        if ids is not None:
            if type(ids) is not list:
                raise Exception('Parameter ids must be a list')
                return
            else:
                querystring += '?ids='
                for i in ids:
                    querystring += i + ','
        text = self.generateRequest('/Tasks' + querystring, 'GET', '')
        return self.dictToList(json.loads(text))
    
    def getTask(self, id):
        """
        Gets a task, identified by its record id
        """
        text = self.generateRequest('/Tasks/' + str(id), 'GET', '')
        return json.loads(text)
    
    def getTaskComments(self, id):
        """
        Gets a list of comments attached to a task, identified by its record id, returns a list of dictionaries
        """
        text = self.generateRequest('/Tasks/' + str(id) + '/Comments', 'GET', '')
        return self.dictToList(json.loads(text))
    
    def addTaskComment(self, id, comment):
        """
        Adds a comment to a task, the comment dictionary should have the following fields:
        
        COMMENT_ID = 0
        BODY = comment text
        OWNER_USER_ID = the comment author's Insightly user ID (numeric)
        
        NOTE: this function is not yet 100%, going over details of data expected with engineering.
        """
        json = json.dumps(comment)
        text = self.generateRequest('/Tasks/' + str(id) + '/Comments', 'POST', json)
        return json.loads(text)
    #
    # Following are methods for managing team members
    #
    
    def getTeamMembers(self, id):
        """
        Gets a list of team members, returns a list of dictionaries
        """
        text = self.generateRequest('/TeamMembers?teamid=' + str(id), 'GET', '')
        return json.loads(text)
    
    def getTeamMember(self, id):
        """
        Gets a team member's details
        """
        text = self.generateRequest('/TeamMembers/' + str(id), 'GET', '')
        return json.loads(text)
    
    def addTeamMember(self, team_member):
        """
        Add a team member.
        
        The parameter team_member should be a dictionary with valid fields, or the string 'sample' to request a sample object.
        """
        if type(team_member) is str:
            if team_member == 'sample':
                team_member = dict(
                    PERMISSION_ID = 1,
                    TEAM_ID=1,
                    MEMBER_USER_ID=1,
                    MEMBER_TEAM_ID=1,
                )
                return team_member
            else:
                raise Exception('team_member must be a dictionary with valid fields, or a string \'sample\' to request a sample object.')
        else:
            if type(team_member) is dict:
                text = self.generateRequest('/TeamMembers', 'POST', json.dumps(team_member))
                return json.loads(text)
            else:
                raise Exception('team_member must be a dictionary with valid fields, or a string \'sample\' to request a sample object.')
    
    def deleteTeamMember(self, id):
        """
        Deletes a team member, identified by their record id. Returns True if successful or raises an exception
        """
        text = self.generateRequest('/TeamMembers/' + str(id), 'DELETE', '')
        return True
    
    def updateTeamMember(self, team_member):
        """
        Update a team member.
        
        team_member should be a dictionary with valid fields, or the string 'sample' to request a sample object
        """
        if type(team_member) is str:
            if team_member == 'sample':
                team_member = dict(
                    PERMISSION_ID = 1,
                    TEAM_ID=1,
                    MEMBER_USER_ID=1,
                    MEMBER_TEAM_ID=1,
                )
                return team_member
            else:
                raise Exception('team_member must be a dictionary with valid fields, or a string \'sample\' to request a sample object.')
        else:
            if type(team_member) is dict:
                text = self.generateRequest('/TeamMembers', 'PUT', json.dumps(team_member))
                return json.loads(text)
            else:
                raise Exception('team_member must be a dictionary with valid fields, or a string \'sample\' to request a sample object.')
    
    # 
    # Following are methods related to Teams 
    # 
    
    def getTeams(self, top=None, skip=None, orderby=None, filters=None):
        """
        Gets a list of teams, returns a list of dictionaries
        """
        querystring = self.ODataQuery('', top=top, skip=skip, orderby=orderby, filters=filters)
        text = self.generateRequest('/Teams' + querystring, 'GET', '')
        return json.loads(text)

    def getTeam(self, id):
        """
        Gets a team, returns a dictionary
        """
        text = self.generateRequest('/Teams/' + str(id), 'GET', '')
        return json.loads(text)
    
    def addTeam(self, team):
        """
        Add/update a team on Insightly.
        
        The parameter team is a dictionary containing the details and team members. To get a sample object to work with
        just call addTeam('sample')
        
        NOTE: you will get a 400 error (bad request) if you do not include a valid list of team members
        """
        if type(team) is str:
            if string.lower(team) == 'sample':
                teams = self.getTeams(top=1)
                return teams[0]
            else:
                raise Exception('team must be a dictionary or \'sample\' (to obtain a sample object)')
        else:
            if type(team) is dict:
                urldata = json.dumps(team)
                if team.get('TEAM_ID',0) > 0:
                    text = self.generateRequest('/Teams', 'PUT', urldata)
                else:
                    text = self.generateRequest('/Teams', 'POST', urldata)
                return json.loads(text)
            else:
                raise Exception('team must be a dictionary or \'sample\' (to obtain a sample object)')
    
    def deleteTeam(self, id):
        """
        Deletes a team, returns True if successful, or raises an exception
        """
        text = self.generateRequest('/Teams/' + str(id), 'DELETE', '')
        return True
        
    #
    # Following is a list of methods for accessing user information. These methods are read-only. 
    #
    
    def getUsers(self, test = True):
        """
        Gets a list of users for this account, returns a list of dictionaries
        """
        if test:
            try:
                text = self.generateRequest('/Users', 'GET', '')
                users = json.loads(text)
                print 'PASS: getUsers() : found ' + len(users)
                self.tests_run += 1
                self.tests_passed += 1
            except:
                print 'FAIL: getUsers()'
                self.tests_run += 1
        else:
            text = self.generateRequest('/Users', 'GET', '')
            return json.loads(text)
    
    def getUser(self, id):
        """
        Gets an individual user's details
        """
        text = self.generateRequest('/Users/' + str(id), 'GET', '')
        return json.loads(text)