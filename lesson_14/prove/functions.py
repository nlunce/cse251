"""
Course: CSE 251, week 14
File: functions.py
Author: Nathan Lunceford
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

To significantly reduce the execution time of Part 1 from 140 seconds, I used multithreading to implement the
process_person function. This allowed for parallel processing of network requests and data operations. To ensure
thread safety for the tree data structure i used a lock.


Describe how to speed up part 2

I sped up the breadth-first search function by streamlining the process of fetching and adding individuals to the tree.
At first each family member's data was fetched and processed sequentially within the main loop, 
leading to repeated code and inefficient handling of network requests. In the optimized version, I introduced a dedicated 
function called request_and_add_person_to_tree. This function helped to encapsulate the logic for fetching and adding a person which eliminated redundancy 
and improved code clarity. 

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
            person_request = Request_thread(f"{TOP_API_URL}/person/{person_id}")
            print(f"   Retrieving person: {person_id}")
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
            print(f"   Person already exists in the tree: {person_id}")

    # Check if the family has been processed
    if tree.does_family_exist(family_id):
        return

    # Fetch and process the family by its ID
    family_request = Request_thread(f"{TOP_API_URL}/family/{family_id}")
    print(f"Retrieving Family: {family_id}")
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
            person_request = Request_thread(f"{TOP_API_URL}/person/{person_id}")
            # print(f"   Retrieving person: {person_id}")
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
            # print(f"   Person already exists in the tree: {person_id}")
            pass

    # Check if the family has been processed
    with tree_lock:
        family_exists = tree.does_family_exist(family_id)
    if family_exists:
        return

    # Fetch and process the family by its ID
    family_request = Request_thread(f"{TOP_API_URL}/family/{family_id}")
    # print(f"Retrieving Family: {family_id}")
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
def breadth_fs_pedigree_unoptimized(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    q = queue.Queue()
    # Root node
    q.put(family_id)

    while not q.empty():
        family_id = q.get()
        family_exists = tree.does_family_exist(family_id)
        if family_id and not family_exists:
            # Fetch and process the family by its ID
            family_request = Request_thread(f"{TOP_API_URL}/family/{family_id}")
            print(f"Retrieving Family: {family_id}")
            family_request.start()
            family_request.join()

            family_data = family_request.get_response()
            family = Family(family_data)
            tree.add_family(family)

            # Process husband
            husband_id = family.get_husband()
            if husband_id and not tree.does_person_exist(husband_id):
                person_request = Request_thread(f"{TOP_API_URL}/person/{husband_id}")
                print(f"   Retrieving person: {husband_id}")
                person_request.start()
                person_request.join()

                person_data = person_request.get_response()
                person = Person(person_data)
                tree.add_person(person)

                husband_parent_id = person.get_parentid()
                q.put(husband_parent_id)

            # Process wife
            wife_id = family.get_wife()
            if wife_id and not tree.does_person_exist(wife_id):
                person_request = Request_thread(f"{TOP_API_URL}/person/{wife_id}")
                print(f"   Retrieving person: {wife_id}")
                person_request.start()
                person_request.join()

                person_data = person_request.get_response()
                person = Person(person_data)
                tree.add_person(person)

                wife_parent_id = person.get_parentid()
                q.put(wife_parent_id)

            # Process children
            child_ids = family.get_children()
            for child_id in child_ids:
                if child_id and not tree.does_person_exist(child_id):
                    person_request = Request_thread(f"{TOP_API_URL}/person/{child_id}")
                    print(f"   Retrieving person: {child_id}")
                    person_request.start()
                    person_request.join()

                    person_data = person_request.get_response()
                    person = Person(person_data)
                    tree.add_person(person)


# Requests and adds a person's information to the tree if not already present
def request_and_add_person_to_tree(person_id, tree):
    # Avoid adding the person if they are already in the tree.
    if tree.does_person_exist(person_id):
        return

    # Initialize a request to fetch the person's information from the server
    person_request = Request_thread(f"{TOP_API_URL}/person/{person_id}")
    person_request.start()
    person_request.join()

    # If the request fetched data successfully, add the person to the tree
    if person_request.get_response() is not None:
        new_person = Person(person_request.get_response())
        tree.add_person(new_person)


# Create a queue for managing the order of family processing
family_queue = queue.Queue()


def breadth_fs_pedigree(family_id, tree):
    # Enqueue the initial family ID to start processing.
    family_queue.put(family_id)

    # List to track threads that are processing families.
    processing_threads = []
    while not family_queue.empty():
        # Process all families currently enqueued.
        while not family_queue.empty():
            # For each family, spawn a thread to process it.
            family_thread = threading.Thread(
                target=process_family, args=(family_queue.get(), tree, True, True)
            )
            family_thread.start()
            processing_threads.append(family_thread)  # Track the thread.

        # Wait for all threads to finish processing.
        for thread in processing_threads:
            thread.join()


# Fetches and processes a family's information based on its ID
def process_family(family_id, tree, use_queue, allow_threading):
    # Initialize a request to fetch the family's information from the server
    family_request = Request_thread(f"{TOP_API_URL}/family/{family_id}")
    family_request.start()
    family_request.join()

    # Proceed only if the request successfully fetched the family's information
    if family_request.get_response() is None:
        return

    # Create a family object and add it to the tree
    new_family = Family(family_request.get_response())
    tree.add_family(new_family)

    # Compile a list of IDs for all members in the family
    family_member_ids = [
        new_family.get_husband(),
        new_family.get_wife(),
        *new_family.get_children(),
    ]
    if allow_threading:
        # If threading is allowed, process each family member in separate threads
        member_threads = []
        for member_id in family_member_ids:
            member_thread = threading.Thread(
                target=request_and_add_person_to_tree, args=(member_id, tree)
            )
            member_thread.start()
            member_threads.append(member_thread)

        # Wait for all member threads to finish
        for thread in member_threads:
            thread.join()
    else:
        # Process each family member sequentially without threading
        for member_id in family_member_ids:
            request_and_add_person_to_tree(member_id, tree)

    # If this process should use the queue, enqueue parent families for further processing
    if use_queue:
        husband_info = tree.get_person(new_family.get_husband())
        wife_info = tree.get_person(new_family.get_wife())
        if husband_info and husband_info.get_parentid():
            family_queue.put(husband_info.get_parentid())
        if wife_info and wife_info.get_parentid():
            family_queue.put(wife_info.get_parentid())


# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    pass
