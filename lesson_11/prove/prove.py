"""
Course: CSE 251
Lesson Week: 11
File: Assignment.py
"""

import time
import random
import multiprocessing as mp

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE = "Turning on the lights for the party vvvvvvvvvvvvvv"
STOPPING_PARTY_MESSAGE = "Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^"

STARTING_CLEANING_MESSAGE = "Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
STOPPING_CLEANING_MESSAGE = "Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"


def cleaner_waiting():
    """Simulates the cleaner waiting before attempting to clean."""
    time.sleep(random.uniform(0, 2))


def cleaner_cleaning(id):
    """Simulates the cleaning process by a cleaner."""
    print(f"Cleaner: {id}")
    time.sleep(random.uniform(0, 2))


def guest_waiting():
    """Simulates the guest waiting before attempting to party."""
    time.sleep(random.uniform(0, 2))


def guest_partying(id, count):
    """Simulates the partying process by a guest."""
    print(f"Guest: {id}, count = {count}")
    time.sleep(random.uniform(0, 1))


def cleaner(
    room_access_lock, cleaning_turn_lock, id, guests_in_room, clean_count, start_time
):
    """
    do the following for TIME seconds
        cleaner will wait to try to clean the room (cleaner_waiting())
        get access to the room
        display message STARTING_CLEANING_MESSAGE
        Take some time cleaning (cleaner_cleaning())
        display message STOPPING_CLEANING_MESSAGE
    """
    while time.time() - start_time < TIME:
        cleaner_waiting()
        cleaning_turn_lock.acquire()
        room_access_lock.acquire()

        print(STARTING_CLEANING_MESSAGE)
        cleaner_cleaning(id)
        print(STOPPING_CLEANING_MESSAGE)
        clean_count.value += 1
        room_access_lock.release()
        cleaning_turn_lock.release()


def guest(
    room_access_lock, cleaning_turn_lock, id, guests_in_room, party_count, start_time
):
    """
    do the following for TIME seconds
        guest will wait to try to get access to the room (guest_waiting())
        get access to the room
        display message STARTING_PARTY_MESSAGE if this guest is the first one in the room
        Take some time partying (call guest_partying())
        display message STOPPING_PARTY_MESSAGE if the guest is the last one leaving in the room
    """
    while time.time() - start_time < TIME:
        guest_waiting()

        if guests_in_room.value == 0:  # If no one in the room start the party
            room_access_lock.acquire()

        guests_in_room.value += 1
        if guests_in_room.value == 1:
            print(STARTING_PARTY_MESSAGE)

        guest_partying(id, guests_in_room.value)
        guests_in_room.value -= 1

        if guests_in_room.value == 0:
            print(STOPPING_PARTY_MESSAGE)
            party_count.value += 1
            room_access_lock.release()


def main():
    # Start time of the running of the program.
    start_time = time.time()

    # TODO - add any variables, data structures, processes you need
    # TODO - add any arguments to cleaner() and guest() that you need

    # Locks to control access to the room and cleaning turns.
    room_access_lock = mp.Lock()
    cleaning_turn_lock = mp.Lock()

    # Shared variables to keep track of the state.
    guests_in_room = mp.Value("i", 0)
    clean_count = mp.Value("i", 0)
    party_count = mp.Value("i", 0)

    processes = []

    # Create guest processes
    for i in range(HOTEL_GUESTS):
        id = i + 1
        guest_process = mp.Process(
            target=guest,
            args=(
                room_access_lock,
                cleaning_turn_lock,
                id,
                guests_in_room,
                party_count,
                start_time,
            ),
        )
        processes.append(guest_process)

    # Create cleaner processes
    for i in range(CLEANING_STAFF):
        id = i + 1
        cleaner_process = mp.Process(
            target=cleaner,
            args=(
                room_access_lock,
                cleaning_turn_lock,
                id,
                guests_in_room,
                clean_count,
                start_time,
            ),
        )
        processes.append(cleaner_process)

    # Start processes
    for process in processes:
        process.start()

    # Join processes
    for process in processes:
        process.join()

    # Results
    print(
        f"Room was cleaned {clean_count.value} times, there were {party_count.value} parties"
    )


if __name__ == "__main__":
    main()
