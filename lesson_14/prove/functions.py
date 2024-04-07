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
# Function to recursively process people
def recursive_process_person(person_id, tree, processed_families):
    if tree.does_person_exist(person_id):
        return

    # Create threaded request for person's data
    person_request = Request_thread(f"{TOP_API_URL}/person/{person_id}")
    person_request.start()
    person_request.join()

    # Extract and process person data
    person_json = person_request.get_response()
    if person_json:
        person_obj = Person(person_json)
        tree.add_person(person_obj)

        # Depth-first recursion for the person's parental family
        parent_family_id = person_obj.get_parentid()
        if parent_family_id and parent_family_id not in processed_families:
            depth_fs_pedigree(parent_family_id, tree, processed_families)


def depth_fs_pedigree(family_id, tree, processed_families=set()):
    # KEEP this function even if you don't implement it
    # TODO - implement Depth first retrieval
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    if family_id in processed_families:
        return

    processed_families.add(family_id)

    family_request = Request_thread(f"{TOP_API_URL}/family/{family_id}")
    family_request.start()
    family_request.join()

    family_json = family_request.get_response()
    if family_json:
        family_obj = Family(family_json)
        if not tree.does_family_exist(family_obj.get_id()):
            tree.add_family(family_obj)

        # Collect all family member IDs, including husband, wife, and children
        family_members_ids = [
            family_obj.get_husband(),
            family_obj.get_wife(),
            *family_obj.get_children(),
        ]

        # Create and start threads for each family member
        person_threads = []
        for person_id in family_members_ids:
            if person_id:
                thread = threading.Thread(
                    target=recursive_process_person,
                    args=(person_id, tree, processed_families),
                )
                thread.start()
                person_threads.append(thread)

        # Join threads
        for thread in person_threads:
            thread.join()


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
