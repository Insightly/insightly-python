#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Insightly API Test Script
# Brian McConnell <brian@insightly.com>
#
# This Python module implements a test suite against the API. This allows users to create
# whatever test cases they want in addition to the standard set of tests we run against
# API endpoints.
#
# USAGE:
#
# i = Insightly()
# i.test()
#
# NOTE:
#
# If you run the test suite, we recommend running it against a test instance with dummy data,
# as there is the potential for data loss. The test suite is primarily intended for use in
# QA testing. 

from insightly import Insightly

get_endpoints = ['activitysets', 'contacts', 'countries', 'currencies', 'customfieldgroups', 'customfields', 'emails', 'filecategories','follows',
                 'instance','leads','leadsources','leadstatuses','notes','opportunities','opportunitycategories','opportunitystatereasons',
                 'organisations','pipelines','pipelinestages','projectcategories','projects','relationships','taskcategories','tasks','teammembers','teams','users']

def test(apikey='', version='2.2', dev=None):
    i = Insightly(apikey=apikey, version=version, dev=dev, test=True)
    i.tests_run = 0
    i.tests_passed = 0
    # test activity sets
    activity_sets = i.read('activitysets')
    if activity_sets is not None:
        activity_set_id = activity_sets[0]['ACTIVITYSET_ID']
        activity_set = i.read('activitysets', id=activity_set_id)
    # test contacts
    contacts = i.read('contacts')
    if contacts is not None:
        contact_id = contacts[0]['CONTACT_ID']
        contact = i.read('contacts', id=contact_id)
    contact = {'FIRST_NAME':'Test','LAST_NAME':'ミスターマコーネル'}
    contact = i.create('contacts', contact)
    if contact is not None:
        contact['FIRST_NAME'] = 'Foo'
        contact = i.update('contacts', contact)
        contact_id = contact['CONTACT_ID']
        i.upload_image('contacts', contact_id, 'apollo17.jpg')
        address = i.create_child('contacts', contact_id, 'addresses', {'ADDRESS_TYPE':'HOME','CITY':'San Francisco', 'STATE':'CA', 'COUNTRY':'United States'})
        if address is not None:
            address_id = address['ADDRESS_ID']
            i.delete('contacts',contact_id,sub_type='addresses',sub_type_id=address_id)
        contactinfo = i.create_child('contacts', contact_id, 'contactinfos', {'TYPE':'EMAIL','SUBTYPE':'Home','DETAIL':'foo@bar.com'})
        if contactinfo is not None:
            contact_info_id = contactinfo['CONTACT_INFO_ID']
            i.delete('contacts', contact_id, sub_type='contactinfos', sub_type_id = contact_info_id)
        contact_date = {'OCCASION_NAME':'Birthday','OCCASION_DATE':'2016-05-02T12:00:00Z'}
        contact_date = i.create_child('contacts', contact_id, 'dates', contact_date)
        if contact_date is not None:
            date_id = contact_date['DATE_ID']
            i.delete('contacts', contact_id, sub_type='dates', sub_type_id=date_id)
        tag = {'TAG_NAME':'foo'}
        i.create_child('contacts', contact_id, 'tags', tag)
        i.delete('contacts', contact_id,sub_type='tags', sub_type_id = 'foo')
        note = {'TITLE':'Test', 'BODY':'This is the body'}
        note = i.create_child('contacts', contact_id, 'notes', note)
        events = i.read('contacts', contact_id, sub_type='events')
        file_attachments = i.read('contacts', contact_id, sub_type='fileattachments')
        i.upload('contacts', contact_id, 'apollo17.jpg')
        i.create_child('contacts', contact_id, 'follow', {})
        i.delete('contacts', contact_id, sub_type='follow')
        tasks = i.read('contacts', contact_id, sub_type='tasks')
        emails = i.read('contacts', contact_id, sub_type='emails')
        i.delete('contacts', contact_id)
    countries = i.read('countries')
    currencies = i.read('currencies')
    custom_field_groups = i.read('customfieldgroups')
    custom_fields = i.read('customfields')
    if custom_fields is not None:
        custom_field_id = custom_fields[0]['CUSTOM_FIELD_ID']
        custom_field = i.read('customfields', custom_field_id)
    emails = i.read('emails')
    if emails is not None:
        email_id = emails[0]['EMAIL_ID']
        email = i.read('emails', email_id)
        i.create_child('emails', email_id, 'tags', {'TAG_NAME':'foo'})
        i.delete('emails', email_id, sub_type='tags', sub_type_id = 'foo')
        comments = i.read('emails', email_id, sub_type='/comments')
    events = i.read('events')
    file_categories = i.read('filecategories')
    if file_categories is not None:
        file_category_id = file_categories[0]['CATEGORY_ID']
        file_category = i.read('filecategories', file_category_id)
    follows = i.read('follows')    
    instance = i.read('instance')
    leads = i.read('leads')
    if leads is not None:
        lead_id = leads[0]['LEAD_ID']
        lead = i.read('leads', lead_id)
    lead = i.create('leads', {'FIRST_NAME':'foo', 'LAST_NAME':'bar'})
    if lead is not None:
        lead_id = lead['LEAD_ID']
        lead['FIRST_NAME']='foozle'
        lead = i.update('leads', lead)
        i.upload_image('leads', lead_id, 'apollo17.jpg')
        i.delete('leads', lead_id, sub_type='image')
        i.create_child('leads', lead_id, 'tags', {'TAG_NAME':'foo'})
        i.delete('leads', lead_id, sub_type='tags', sub_type_id='foo')
        i.create_child('leads', lead_id, 'follow', {})
        i.delete('leads', lead_id, sub_type='follow')
        notes = i.read('leads', lead_id, sub_type='notes')
        i.create_child('leads', lead_id, 'notes', {'TITLE':'foo','BODY':'This is the body'})
        events = i.read('leads', lead_id, sub_type='events')
        file_attachments = i.read('leads', lead_id, sub_type='fileattachments')
        i.upload('leads', lead_id, 'apollo17.jpg')
        tasks = i.read('leads', lead_id, sub_type='tasks')
        emails = i.read('leads', lead_id, sub_type='emails')
        i.delete('leads', lead_id)
    leadsources = i.read('leadsources')
    lead_source = i.create('leadsources', {'LEAD_SOURCE':'Foozle Barzle'})
    if lead_source is not None:
        lead_source['LEAD_SOURCE'] = 'Barzle Foozle'
        lead_source_id = lead_source['LEAD_SOURCE_ID']
        lead_source = i.update('leadsources', lead_source)
        i.delete('leadsources', lead_source_id)
    lead_statuses = i.read('leadstatuses')
    lead_status = i.create('leadstatuses', {'LEAD_STATUS':'Foozle'})
    if lead_status is not None:
        lead_status_id = lead_status['LEAD_STATUS_ID']
        lead_status['LEAD_STATUS']='Barzle'
        lead_status['STATUS_TYPE']=1
        lead_status = i.update('leadstatuses', lead_status)
        i.delete('leadstatuses', lead_status_id)
    notes = i.read('notes')
    if notes is not None:
        note_id = notes[0]['NOTE_ID']
        note = i.read('notes', note_id)
        file_attachments = i.read('notes', note_id, sub_type='fileattachments')
        i.create_child('notes', note_id, 'follow', {})
        i.delete('notes', note_id, sub_type='follow')
        comments = i.read('notes', note_id, sub_type='comments')
    opportunities = i.read('opportunities')
    if opportunities is not None:
        opportunity_id = opportunities[0]['OPPORTUNITY_ID']
        opportunity = i.read('opportunities', opportunity_id)
        opportunity = i.create('opportunities', {'OPPORTUNITY_NAME':'Foozle','OPPORTUNITY_STATE':'Open'})
        if opportunity is not None:
            opportunity['OPPORTUNITY_NAME'] = 'Barzle'
            opportunity_id = opportunity['OPPORTUNITY_ID']
            opportunity = i.update('opportunities', opportunity)
            i.upload_image('opportunities', opportunity_id, 'apollo17.jpg')
            i.delete('opportunities', opportunity_id, 'image')
            i.create_child('opportunities', opportunity_id, 'tags', {'TAG_NAME':'foo'})
            i.delete('opportunities', opportunity_id, sub_type='tags', sub_type_id='foo')
            notes = i.read('opportunities', opportunity_id, sub_type='notes')
            i.create_child('opportunities', opportunity_id, 'notes', {'TITLE':'foo','BODY':'This is a test'})
            events = i.read('opportunities', opportunity_id, sub_type='events')
            file_attachments = i.read('opportunities', opportunity_id, sub_type='fileattachments')
            i.upload('opportunities', opportunity_id, 'apollo17.jpg')
            i.create_child('opportunities', opportunity_id, 'follow', {})
            i.delete('opportunities', opportunity_id, sub_type='follow')
            # add call to update opportunity state/state reason here
            opportunity_state_reasons = i.read('opportunities', opportunity_id, sub_type='statehistory')
            tasks = i.read('opportunities', opportunity_id, sub_type='tasks')
            emails = i.read('opportunities', opportunity_id, sub_type='emails')
            email = i.read('opportunities', opportunity_id, sub_type='linkemailaddress')
            i.delete('opportunities', opportunity_id, sub_type='pipeline')
            i.delete('opportunities', opportunity_id)
    opportunity_categories = i.read('opportunitycategories')
    opportunity_state_reasons = i.read('opportunitystatereasons')
    
    organisations = i.read('organisations')
    if organisations is not None:
        organisation_id = organisations[0]['ORGANISATION_ID']
        organisation = i.read('organisations', organisation_id)
        organisation = i.create('organisations', {'ORGANISATION_NAME':'Foo Corporation'})
        if organisation is not None:
            organisation_id = organisation['ORGANISATION_ID']
            organisation['ORGANISATION_NAME']='Bar Corporation'
            organisation = i.update('organisations', organisation)
            address = i.create_child('organisations', organisation_id, 'addresses', {'CITY':'San Francisco', 'STATE':'CA', 'COUNTRY':'United States', 'ADDRESS_TYPE':'Work'})
            if address is not None:
                address_id = address['ADDRESS_ID']
                i.delete('organisations', organisation_id, sub_type='addresses', sub_type_id=address_id)
            contactinfo = i.create_child('organisations', organisation_id, 'contactinfos', {'TYPE':'EMAIL','SUBTYPE':'Home','DETAIL':'foo@bar.com'})
            if contactinfo is not None:
                contact_info_id = contactinfo['CONTACT_INFO_ID']
                i.delete('organisations', organisation_id, sub_type='contactinfos', sub_type_id=contact_info_id)
            odate = i.create_child('organisations', organisation_id, 'dates', {'OCCASION_NAME':'Birthday','OCCASION_DATE':'2016-05-02T12:00:00Z'})
            if odate is not None:
                date_id = odate['DATE_ID']
                i.delete('organisations', organisation_id, sub_type='dates', sub_type_id=date_id)
            i.create_child('organisations', organisation_id, 'tags', {'TAG_NAME':'foo'})
            i.delete('organisations',organisation_id, sub_type='tags', sub_type_id='foo')
            i.upload_image('organisations', organisation_id, 'apollo17.jpg')
            i.delete('organisations', organisation_id, sub_type='image')
            notes = i.read('organisations', organisation_id, sub_type='notes')
            i.create_child('organisations', organisation_id, 'notes', {'TITLE':'Title','BODY':'This is the body'})
            events = i.read('organisations', organisation_id, sub_type='events')
            file_attachments = i.read('organisations', organisation_id, sub_type='fileattachments')
            i.upload('organisations', organisation_id, 'apollo17.jpg')
            i.create_child('organisations', organisation_id, 'follow', {})
            i.delete('organisations', organisation_id, sub_type='follow')
            emails = i.read('organisations', organisation_id, sub_type='emails')
            tasks = i.read('organisations', organisation_id, sub_type='tasks')
            i.delete('organisations', organisation_id)
    
    pipelines = i.read('pipelines')
    if pipelines is not None:
        pipeline_id = pipelines[0]['PIPELINE_ID']
        pipeline = i.read('pipelines', pipeline_id)
        
    pipeline_stages = i.read('pipelinestages')
    if pipeline_stages is not None:
        stage_id = pipeline_stages[0]['STAGE_ID']
        pipeline_stage = i.read('pipelinestages', stage_id)
    
    projects = i.read('projects')
    if projects is not None:
        project_id = projects[0]['PROJECT_ID']
        project = i.read('projects', project_id)
        project = i.create('projects', {'PROJECT_NAME':'Foo Corporation','STATUS':'Not Started'})
        if project is not None:
            project_id = project['PROJECT_ID']
            project['PROJECT_NAME']='Barzle Corporation'
            project = i.update('projects', project)
            i.upload_image('projects', project_id, 'apollo17.jpg')
            i.delete('projects', project_id, sub_type='image')
            i.create_child('projects', project_id, 'tags', {'TAG_NAME':'foo'})
            i.delete('projects', project_id, sub_type='tags', sub_type_id='foo')
            notes = i.read('projects', project_id, sub_type='notes')
            i.create_child('projects', project_id, 'notes', {'TITLE':'Foo','BODY':'This is the body'})
            events = i.read('projects', project_id, sub_type='events')
            file_attachments = i.read('projects', project_id, sub_type='fileattachments')
            i.create_child('projects', project_id, 'follow', {})
            i.delete('projects', project_id, sub_type='follow')
            milestones = i.read('projects', project_id, sub_type='milestones')
            tasks = i.read('projects', project_id, sub_type='tasks')
            emails = i.read('projects', project_id, sub_type='emails')
            email = i.read('projects', project_id, sub_type='linkemailaddress')
            i.delete('projects', project_id, sub_type='pipeline')
            i.delete('projects', project_id)
    relationships = i.read('relationships')
    tags = i.read('tags?record_type=contacts')
    task_categories = i.read('taskcategories')
    tasks = i.read('tasks')
    if tasks is not None:
        task_id = tasks[0]['TASK_ID']
        task = i.read('tasks', task_id)
    users = i.read('users')
    if users is not None:
        user_id = users[0]['USER_ID']
        user = i.read('users', user_id)
    else:
        user_id = None
    me = i.read('users/me')
    if user_id is not None:
        task = i.create('tasks', {'TITLE':'Test','STATUS':'Not Started','COMPLETED':'False','PUBLICLY_VISIBLE':'True','RESPONSIBLE_USER_ID':str(user_id)})
        if task is not None:
            task['TITLE'] = task['TITLE'] + 'foo'
            task_id = task['TASK_ID']
            task = i.update('tasks', task)
            i.create_child('tasks', task_id, 'follow', {})
            i.delete('tasks', task_id, sub_type='follow')
            comments = i.read('tasks', task_id, sub_type='comments')
            i.delete('tasks', task_id)
    team_members = i.read('teammembers')
    if team_members is not None:
        team_member_id = team_members[0]['PERMISSION_ID']
        team_member = i.read('teammembers', team_member_id)
    
    teams = i.read('teams')
    if teams is not None:
        team_id = teams[0]['TEAM_ID']
        team = i.read('teams', team_id)
        team = i.create('teams',{'TEAM_NAME':'Team Foo','ANONYMOUS_TEAM':'False'})
        if team is not None:
            team_id = team['TEAM_ID']
            team['TEAM_NAME'] = 'Team Bar'
            team = i.update('teams', team)
            i.delete('teams', team_id)
            
    #
    # Next, create a few objects, add links between them, and then delete them
    #
    
    contact_id = None
    organisation_id = None
    project_id = None
    opportunity_id = None
    
    contact = i.create('contacts',{'FIRST_NAME':'Foo','LAST_NAME':'Bar'})
    if contact is not None:
        contact_id = contact['CONTACT_ID']
    organisation = i.create('organisations',{'ORGANISATION_NAME':'Foo Corporation'})
    if organisation is not None:
        organisation_id = organisation['ORGANISATION_ID']
    project = i.create('projects',{'PROJECT_NAME':'Foo Corporation','Status':'Not Started'})
    if project is not None:
        project_id = project['PROJECT_ID']
    opportunity = i.create('opportunities',{'OPPORTUNITY_NAME':'Foo Corporation','OPPORTUNITY_STATE':'Open'})
    if opportunity is not None:
        opportunity_id = opportunity['OPPORTUNITY_ID']
    
    contact = i.create_child('contacts', contact_id, 'links', {'ORGANISATION_ID':organisation_id})
    organisation = i.create_child('organisations', organisation_id, 'links', {'PROJECT_ID':project_id})
    project = i.create_child('projects', project_id, 'links', {'ORGANISATION_ID':organisation_id})
    opportunity = i.create_child('opportunities', opportunity_id, 'links', {'CONTACT_ID':contact_id})
    
    if contact_id is not None:
        i.delete('contacts', contact_id)
    if organisation_id is not None:
        i.delete('organisations', organisation_id)
    if project_id is not None:
        i.delete('projects', project_id)
    if opportunity_id is not None:
        i.delete('opportunities', opportunity_id)
    
    print(str(i.tests_passed) + ' out of ' + str(i.tests_run) + ' passed')
    print ('')
    print ('Test Failures')
    for f in i.test_failures:
        print (f)