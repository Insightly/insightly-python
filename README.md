Insightly For Python
======

The Insightly Python SDK makes it super easy to integrate Insightly into your Python applications and web services, as easy as:

  from insightly import Insightly
  
  i = Insightly()
  
  contacts = i.read('contacts', orderby='DATE_UPDATED_UTC desc')

The library takes care of authentication and low level communication, so you can focus on building your custom application or service. 
