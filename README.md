Insightly For Python
======

The Insightly Python SDK makes it super easy to integrate Insightly into your Python applications and web services, as easy as:

  from insightly import Insightly
  
  i = Insightly()
  
  contacts = i.read('contacts', top=100, skip=100, filters={'city':'perth'})

The library takes care of authentication and low level communication, so you can focus on building your custom application or service.

The library has been tested with both Python versions 2.7 and 3.x

MAJOR CHANGES IN VERSION 2.2
============================

Version 2.2 of the Insightly API provides a substantial improvement in both performance and functionality. We strongly recommend that users migrate to this version of the API at their earliest convenience, although we will continue to provide access to version 2.1. Among the improvements and new features in version 2.2:

* Pagination for search results (use the top and skip parameters to page through large recordsets, version 2.1 would return the entire recordset, which led to excessively large responses and slow performance)
* Support for incremental updates to existing objects. For example, to add an address to an existing contact, you just PUT/POST the updated address to a contact without touching the parent object graph (this reduces the potential for data loss as it was easy for users to forget part of the object graph in the version 2.1 API)
* Support for predefined filters (in version 2.2 we have replaced OData with a list of predefined, optional query parameters when fetching lists of contacts, emails, leads, notes, organisations, opportunities and projects). These queries have also be optimized for performance.
* Swagger documentation and interactive sandbox for testing GET operations. See api.insight.ly/v2.2/Help (you can also auto-generate client SDKs using the Swagger toolkit if you are using a language we do not provide an SDK for)
* Support for activity sets, follows, pipelines, and more, so the web API is in close alignment with the interactions supported via the web application.

NOTE: version 2.2 is now available for beta testing, and can be accessed at https://api.insight.ly/v2.2/Help while version 2.1 can be reached at https://api.insight.ly/v2.1/Help

ABOUT THIS LIBRARY
==================

The Python library has a small footprint (< 1000 lines of code), and uses only standard libraries, so it should run in any Python 2.7
environment.

To install the library, simply copy insightly.py into your project directory and follow the instructions below.

USAGE
=====

First, you'll need to instantiate the Insightly class, which you do with the following statement:

i = Insightly(apikey='yourapikey',version='2.1|2.2',test=False)

Note, if you omit the apikey, it will look for it in a text file named apikey.txt in the working directory. If you omit the version number it will default to v2.2. Use the test mode to log success/fail events to the console and to testresults.txt

Once you have instantiated the Insightly class, you can create, read, update and delete Insightly objects using the create, delete, read and update methods.

FETCHING AND SEARCHING INSIGHTLY OBJECTS
========================================

Use the read() method for these operations. It is invoked as follows:

To get a list of currently supported endpoints:

endpoints = i.endpoints()

To search for a list of records:

  contacts = i.read('contacts',top=100,filters={'city':'perth'})

  emails = i.read('emails',top=100,filters={'email_from':'foo@bar.com'})

  projects = i.read('projects',top=100,filters={'status':'in progress'})

To fetch an individual record:

  contact = i.read('contacts',id=123456)
  
  opportunity = i.read('opportunities',id=123456)

DELETING AN INSIGHTLY OBJECT
============================

  success = i.delete('contacts',id=123456)

CREATING AN INSIGHTLY OBJECT
============================

  lead = {'first_name':'foo','last_name':'bar'}

  success = i.create('leads', lead)
  
  address = {'address_type':'home','city':'San Francisco','state':'CA','country':'United States'}
  
  success = i.create_child('contacts', contact_id, 'addresses', address)

UPDATING AN INSIGHTLY OBJECT
============================

  lead['first_name'] = 'Foozle'

  success = i.update('leads',lead)

