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
tree_lock = threading.Lock()

def depth_fs_pedigree_unoptimized(family_id, tree):
    
    def process_person(person_id, tree):
        if person_id and not tree.does_person_exist(person_id):
            person_request = Request_thread(f'{TOP_API_URL}/person/{person_id}')
            print(f'   Retrieving person: {person_id}')
            person_request.start()
            person_request.join()
            
            person_data = person_request.get_response()
            person = Person(person_data)
            tree.add_person(person)
            

            person_parent_id = person.get_parentid()
            # Recursive DFS call for the person's parents
            if person_parent_id:  
                depth_fs_pedigree(person_parent_id, tree)
        else:
            print(f'   Person already exists in the tree: {person_id}')
        
    # Check if the family has been processed
    if tree.does_family_exist(family_id):
        return

    # Fetch and process the family by its ID
    family_request = Request_thread(f'{TOP_API_URL}/family/{family_id}')
    print(f'Retrieving Family: {family_id}')
    family_request.start()
    family_request.join()

    family_data = family_request.get_response()
    family = Family(family_data)
    tree.add_family(family)

    # Process the husband
    husband_id = family.get_husband()
    if husband_id:
        process_person(husband_id, tree)

    # Process the wife
    wife_id = family.get_wife()
    if wife_id:
        process_person(wife_id, tree)

    # Process children
    child_ids = family.get_children()
    for child_id in child_ids:
        process_person(child_id, tree)

def depth_fs_pedigree(family_id, tree):
    global tree_lock
    def process_person(person_id, tree):
        global tree_lock
        with tree_lock:
            person_exists = tree.does_person_exist(person_id)
        
        if person_id and not person_exists:
            person_request = Request_thread(f'{TOP_API_URL}/person/{person_id}')
            print(f'   Retrieving person: {person_id}')
            person_request.start()
            person_request.join()
            
            person_data = person_request.get_response()
            person = Person(person_data)
            with tree_lock:
                tree.add_person(person)
            

            person_parent_id = person.get_parentid()
            # Recursive DFS call for the person's parents
            if person_parent_id:  
                depth_fs_pedigree(person_parent_id, tree)
        else:
            print(f'   Person already exists in the tree: {person_id}')
        
    # Check if the family has been processed
    with tree_lock:
        family_exists = tree.does_family_exist(family_id)
    if family_exists:
        return

    # Fetch and process the family by its ID
    family_request = Request_thread(f'{TOP_API_URL}/family/{family_id}')
    print(f'Retrieving Family: {family_id}')
    family_request.start()
    family_request.join()

    family_data = family_request.get_response()
    family = Family(family_data)
    
    with tree_lock:
        tree.add_family(family)
    

    person_threads = []
    
    # Process the husband
    husband_id = family.get_husband()
    if husband_id:
        thread = threading.Thread(
                    target=process_person,
                    args=(husband_id, tree),
                )
        person_threads.append(thread)
        thread.start()

    # Process the wife
    wife_id = family.get_wife()
    if wife_id:
        thread = threading.Thread(
                    target=process_person,
                    args=(wife_id, tree),
                )
        person_threads.append(thread)
        thread.start()

    # Process children
    child_ids = family.get_children()
    for child_id in child_ids:
        thread = threading.Thread(
                    target=process_person,
                    args=(child_id, tree),
                )
        person_threads.append(thread)
        thread.start()
        
    for person_thread in person_threads:
        person_thread.join()


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