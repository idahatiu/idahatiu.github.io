import csv
import os
from pathlib import Path
db_structure = {}
#define field names for each table
db_structure['artifacts'] = (['artifactID','title','collection','creator',
    'address','city','county','state','date','author','contributor','language','rights',
    'group','externalUrl','subject','format','type','description',
    'humanReviewed','distributionPermitted'])
db_structure['periodicals'] = ['artifactID','publication','publisher','volume','issue','pageRange']
db_structure['advertisements'] = ['artifactID','audience','brand']
db_structure['correspondance'] = ['artifactID','recipient']
db_structure['images'] = ['artifactID']
db_structure['media'] = ['artifactID']
db_structure['governmentDocuments'] = ['artifactID']
db_structure['prints'] = ['artifactID','circulation','source']
db_structure['picEntities'] = ['entityID','title','notes','type']
db_structure['picRelationships'] = ['artifactID','entity1ID','entity2ID']
db_structure['geographies'] = ['geoID','geometry','name']
db_structure['entityLocations'] = ['entityID','geoID']
db_structure['socialMedia'] = ['artifactID']

#create csv files and organize into subdirectories
def create_db_csv(fieldDict):
    """ fieldDict (dictionary): key is the name of the table, items is a list of fields in that table
    Organizes tables based on which object ID is found at the start of each field list
    Will create folders appropriately"""
    cwd = os.getcwd()
    os.mkdir('artifacts')
    os.mkdir('pic_entities')
    os.mkdir('geographies')
    for table,fields in fieldDict.items():
        if fields[0] == 'artifactID':
            os.chdir('artifacts')
        elif fields[0] == 'entityID':
            os.chdir('pic_entities')
        else:
            os.chdir('geographies')
        with open(f'{table}.csv', 'w',newline = '') as activeTable:
            writer = csv.writer(activeTable)
            writer.writerow(fields)
            print(f'wrote file {table}.csv with {len(fields)} fields in {os.getcwd()}')
        os.chdir(cwd)
def insert_artifact(properties,db_structure = db_structure,subclass = False):
    """
        properties (list): a list with all metadata properties in the same order as field_list
            subclass fields should be in order at the end, do not repeat artifactID
        db_structure (dict): dictionary used to generate csv files
        subclass (str): name of table for subclass to add items to. optional
    Writes artifacts to main and subclass tables. Does not return
    """
    #validate that input properly maps to fields
    if subclass:
        assert len(properties) == len(db_structure['artifacts']) + len(db_structure[subclass]) - 1, "incorrect number of properties (use empty strings if no data)"
    else:
        assert len(properties) == len(db_structure['artifacts']), "incorrect number of properties (use empty strings if no data)"
    #write generic artifact traits to main csv
    with open(os.path.join(os.getcwd(),Path('artifacts/artifacts.csv')),'a',newline = '') as activeTable:
        writer = csv.writer(activeTable)
        writer.writerow(properties[:len(db_structure['artifacts'])])
    #write subclass properties if necessary
    if subclass:
        with open(os.path.join(os.getcwd(),Path(f'artifacts/{subclass}.csv')),'a',newline = '') as activeTable:
            writer = csv.writer(activeTable)
            writer.writerow([properties[0]] + properties[len(db_structure['artifacts']):])
    return True

def getIDs(tablePath):
    with open(os.path.join(os.getcwd(),tablePath),'r') as activeTable:
        reader = csv.reader(activeTable)
        next(reader)
        ids = [x[0] if x else 0 for x in reader]
    return ids

def autoID(domain):
    id_scheme = {'artifactID':10000,'entityID':9000,'geoID':8000}
    paths = {'artifactID':Path('artifacts/artifacts.csv'),
            'entityID':Path('pic_entities/picEntities.csv'),
            'geoID':Path('geographies/geographies.csv')}
    ids = getIDs(paths[domain])
    if ids:
        autoid = max([int(x) for x in ids]) + 1
    else:
        autoid = id_scheme[domain] + 1
    return autoid

def create_entity(properties,db_structure = db_structure):
    assert len(properties) == len(db_structure['picEntities']), 'Wrong number of fields for new entity'
    with open(os.path.join(os.getcwd(),Path('pic_entities/picEntities.csv')),'a') as activeTable:
        writer = csv.writer(activeTable)
        writer.writerow(properties)
    return True

def create_location(properties,db_structure = db_structure):
    assert len(properties) == len(db_structure['geographies']), 'Wrong number of fields for new entity'
    with open(os.path.join(os.getcwd(),Path('geographies/geographies.csv')),'a') as activeTable:
        writer = csv.writer(activeTable)
        writer.writerow(properties)
    return True

def create_relationship(relation):
    assert str(relation[0]) in getIDs(Path('artifacts/artifacts.csv')), 'relation invalid'
    assert str(relation[1]) in getIDs(Path('pic_entities/picEntities.csv')), 'relation invalid'
    assert str(relation[2]) in getIDs(Path('pic_entities/picEntities.csv')), 'relation invalid'
    with open(os.path.join(os.getcwd(),Path('artifacts/picRelationships.csv')),'a') as table:
        writer = csv.writer(table)
        writer.writerow(relation)
    return True

def assoc_location(relation):
    assert str(relation[0]) in getIDs(Path('pic_entities/picEntities.csv')), 'relation invalid'
    assert str(relation[1]) in getIDs(Path('geographies/geographies.csv')), 'relation invalid'
    with open(os.path.join(os.getcwd(),Path('pic_entities/entityLocations.csv')),'a') as table:
        writer = csv.writer(table)
        writer.writerow(relation)
    return True

def membership(objectID,tablePath):
    return objectID in getIDs(tablePath)

def isASubclass(artifactID):
    classes = []
    for table in db_structure.keys():
        if table == 'artifacts':
            continue
        elif (db_structure[table][0] == 'artifactID' and
            membership(artifactID,Path('artifacts',f'{table}.csv'))):
            classes += [table]
    return classes if classes else 'artifacts'

def getArtifactProperties(artifactID):
    with open(os.path.join(os.getcwd(),Path('artifacts/artifacts.csv')),'r') as table:
        reader = csv.reader(table)
        for row in reader:
            if row[0] == artifactID:
                properties = row
                break
    if row[14] in db_structure.keys():
        with open(os.path.join(os.getcwd(),Path('artifacts',f'{row[14]}.csv')),'r') as table:
            reader = csv.reader(table)
            for row in reader:
                if row[0] == artifactID:
                    properties += row
                    break
    return properties
def propIndex(prop,fields = db_structure['artifacts']):
    for i in range(len(fields)):
        if fields[i] == prop:
            break
    return i
    
def generateArtifactMd(artifactID):
    
    filename = f'CS_{artifactID}.md'
    properties = getArtifactProperties(artifactID)
    markdown = """---
layout: item
format: {}
title: {}
creator: 
  creator_1:  {}
  creator_2: {}
contributor: {}
creation_date: {}
type: {}
short_desc: {}
group: 
categories: {} 
tags: [{}]
team_member: 
contributor_quote: 
image_list: 
  alt_text_1: 
  alt_text_2: 
---
## About This Artifact

""".format(properties[propIndex('format')],
           properties[propIndex('title')],
           properties[propIndex('author')],
           properties[propIndex('creator')],
           properties[propIndex('contributor')],
           properties[propIndex('date')],
           properties[propIndex('type')],
           properties[propIndex('description')],
           isASubclass(artifactID),
           properties[propIndex('subject')])
    with open(filename,'w') as file:
        file.write(markdown)
    return True

def interactive_workflow():
    loop = True
    menu = {'artifactID':(create_relationship,'picRelationships'),'entityID':(assoc_location,'entityLocations')}
    while loop:
        inputType = input('\nTable to insert: ')
        try:
            inputType in db_structure.keys()
            if db_structure[inputType][0] == 'artifactID':
                if inputType != 'artifacts':
                    subclass = inputType
                else:
                    subclass = False
                print('if field is empty, use empty string ie ""')
                inputList = [autoID('artifactID')]
                for field in db_structure['artifacts'][1:]:
                    prop = input(f'\nenter {field}: ')
                    inputList += [prop]
                if inputType != 'artifacts':
                    for field in db_structure[inputType][1:]:
                        prop = input(f'\nenter {field}: ')
                        inputList += [prop]
                insert_artifact(inputList, subclass=subclass)
            elif db_structure[inputType][0] == 'entityID':
                inputList = [autoID('entityID')]
                for field in db_structure[inputType][1:]:
                    prop = input(f'\nenter {field}: ')
                    inputList += [prop]
                create_entity(inputList)
            elif db_structure[inputType][0] == 'geoID':
                inputList = [autoID('geoID')]
                for field in db_structure[inputType][1:]:
                    prop = input(f'\nenter {field}: ')
                    inputList += [prop]
                create_location(inputList)
        except:
            print('invalid_table')
        print(f'Added entry to table {inputType}.csv with id {inputList[0]}')
        relations = input('add relation y/n')
        while relations == 'y':
            relationType = db_structure[inputType][0]
            print(f'using {menu[relationType]} to add relation')
            try:
                relationList = [inputList[0]]
                for field in db_structure[menu[relationType][1]][1:]:
                    prop = input(f'\nenter {field}: ')
                    relationList += [prop]
                menu[relationType][0](relationList)
            except:
                print('relation add failed')
            relations = input('add another relation? y/n')
        nextitem = input('add another item? y/n')
        loop = True if nextitem == 'y' else False
                    
                    
            
        
                
            
            

if __name__ == '__main__':
    #os.chdir(Path('C:/Users/tctim/Documents/Projects/IDAH'))
    #os.chdir(Path('/Users/timothyclark/Projects/IDAH'))
    #create_db_csv(db_structure)
    #sample = ([autoID('artifactID'),'Is Colorado in America?','','Western Federation of Miners',
    #           '','Telluride','San Miguel', 'CO',
    #           '1902-1904', 'William Haywood','Drew Heiderschiedt','eng','Public Domain',
    #           'WFM; Labor Organizing','','','photo','prints',"A poster created by the Western Federation of Miners during the Colorado Labor Wars concerning agitation in Telluride, Colorado for better working conditions, wages, etc. that was violently suppressed by local state institutions, especially police.",
    #           'True','False','Denver','Western Federation of Miners'])
    #insert_artifact(sample,subclass = 'prints')
    #create_entity([autoID('entityID'),'Colorado Supreme Court','','Judicial'])
    #create_location([autoID('geoID'),'Point(39.738093, -104.986735)','Denver Supreme Court'])
    #create_relationship(['10001','9001','9001'])
    #assoc_location(['9001','8001'])
    #print(membership('10001',Path('artifacts/prints.csv')))
    #interactive_workflow()
    #create_relationship(['20002','9001','9001']) #this should cause assertionError -
        #prevents invalid relationships from being added to the table
    #generateArtifactMd('10001')
    a = '5'



    
