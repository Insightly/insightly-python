from insightly import Insightly

def main():
    i = Insightly()
    contact_ids = i.get_all('contacts')
    for c in contact_ids:
        contact = i.get('contacts', c)
        dummy(contact)
        
def dummy(contact):
    # do something with the contact data, such as check external system
    # to see if this contact has been imported, and if not, import it
    return True