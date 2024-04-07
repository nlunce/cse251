"""
Course: CSE 251, week 14
File: functions.py
Author: <your name>

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
request = Request_thread(f'{TOP_API_URL}/family/{id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
request = Request_thread(f'{TOP_API_URL}/person/{id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}

You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

<Add your comments here>


Describe how to speed up part 2

<Add your comments here>


Extra (Optional) 10% Bonus to speed up part 3

<Add your comments here>

"""
from common import *
import queue

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement Depth first retrieval
    # TODO - Printing out people and families that are retrieved from the server will help debugging
    
    # Check if family has been processed
    if tree.does_family_exist(family_id):
        return

    family_request = Request_thread(f'{TOP_API_URL}/family/{family_id}')
    print(f'Retrieving Family: {family_id}')
    family_request.start()
    family_request.join()
    
    family_data = family_request.get_response()
    family = Family(family_data)
    tree.add_family(family)
    
    husband_id = family.get_husband()
    print(f"Husband id: {husband_id}")
    wife_id = family.get_wife()
    child_ids = family.get_children()

    if not tree.does_person_exist(husband_id):
        husband_request = Request_thread(f'{TOP_API_URL}/person/{husband_id}')
        print(f'   Retrieving Husband : {husband_id}')
        husband_request.start()
        husband_request.join()
        
        husband_data = husband_request.get_response()
        husband = Person(husband_data)
        tree.add_person(husband)
    else:
        print(f'   Husband already exists in the tree: {husband_id}')
    
    if not tree.does_person_exist(wife_id):
        wife_request = Request_thread(f'{TOP_API_URL}/person/{wife_id}')
        print(f'   Retrieving Wife    : {wife_id}')
        wife_request.start()
        wife_request.join()
        
        wife_data = wife_request.get_response()
        wife = Person(wife_data)
        tree.add_person(wife)
    else:
        print(f'   Wife already exists in the tree: {wife_id}')
    
    child_requests = []
    for child_id in child_ids:
        if not tree.does_person_exist(child_id):  # Check if child does NOT exist
            child_request = Request_thread(f'{TOP_API_URL}/person/{child_id}')
            child_requests.append(child_request)
            
        else:
            print(f'   Child already exists in the tree: {child_id}') 
    
    
    print(f'   Retrieving children: {str(family.get_children())[1:-1]}')
    for req in child_requests:
        req.start()

    for req in child_requests:
        req.join()
        
    for req in child_requests:
        child_data = req.get_response()
        child = Person(child_data)  
        tree.add_person(child)
        

            
        
   
   
    

    

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    pass

# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    pass