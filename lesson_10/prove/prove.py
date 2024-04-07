"""
Course: CSE 251
Lesson Week: 10
File: assignment.py
Author: Nathan

Purpose: assignment for week 10 - reader writer problem

Instructions:

- Review TODO comments

- writer: a process that will send numbers to the reader.  
  The values sent to the readers will be in consecutive order starting
  at value 1.  Each writer will use all of the sharedList buffer area
  (ie., BUFFER_SIZE memory positions)

- reader: a process that receive numbers sent by the writer.  The reader will
  accept values until indicated by the writer that there are no more values to
  process.  

- Do not use try...except statements

- Display the numbers received by the reader printing them to the console.

- Create WRITERS writer processes

- Create READERS reader processes

- You can use sleep() statements for any process.

- You are able (should) to use lock(s) and semaphores(s).  When using locks, you can't
  use the arguments "block=False" or "timeout".  Your goal is to make your
  program as parallel as you can.  Over use of lock(s), or lock(s) in the wrong
  place will slow down your code.

- You must use ShareableList between the two processes.  This shareable list
  will contain different "sections".  There can only be one shareable list used
  between your processes.
  1) BUFFER_SIZE number of positions for data transfer. This buffer area must
     act like a queue - First In First Out.
  2) current value used by writers for consecutive order of values to send
  3) Any indexes that the processes need to keep track of the data queue
  4) Any other values you need for the assignment

- Not allowed to use Queue(), Pipe(), List(), Barrier() or any other data structure.

- Not allowed to use Value() or Array() or any other shared data type from 
  the multiprocessing package.

- When each reader reads a value from the sharedList, use the following code to display
  the value:
  
                    print(<variable from the buffer>, end=', ', flush=True)

Add any comments for me:

"""

import random
from multiprocessing.managers import SharedMemoryManager
import multiprocessing as mp

BUFFER_SIZE = 10
READERS = 2
WRITERS = 2

# Define constants used in the shared buffer for control and signaling
STOP_VALUE = -1  # Special value to signal readers to stop
NEXT_INDEX = BUFFER_SIZE  # Index in shared buffer to track the next value to be sent
WRITE_INDEX = BUFFER_SIZE + 1  # Index to keep track of where to write in the buffer
READ_INDEX = BUFFER_SIZE + 2  # Index to keep track of where to read in the buffer
RESULT_INDEX = BUFFER_SIZE + 3  # Index to store the result or last value read


# Writer process function
def write(items_to_send, lock, write_sem, read_sem, shared_list):
    go = True
    while go:
        write_sem.acquire()  # Wait for a signal that it's safe to write
        lock.acquire()  # Lock the shared buffer for exclusive access

        # Determine the next value to write, either incrementing or signaling stop
        if shared_list[NEXT_INDEX] > items_to_send:
            next_value = STOP_VALUE
        else:
            next_value = shared_list[NEXT_INDEX]

        next_index = shared_list[WRITE_INDEX]  # Where to write the next value
        shared_list[next_index] = next_value  # Write the value

        # Update indexes or signal stop
        if next_value == STOP_VALUE:
            go = False
        else:
            shared_list[NEXT_INDEX] += 1
            shared_list[WRITE_INDEX] = (shared_list[WRITE_INDEX] + 1) % BUFFER_SIZE

        lock.release()  # Release exclusive access
        read_sem.release()  # Signal that there's new data to read


# Reader process function
def read(lock, write_sem, read_sem, shared_list):
    go = True
    while go:
        read_sem.acquire()  # Wait for a signal that there's data to read
        lock.acquire()  # Lock the shared buffer for exclusive access

        next_index = shared_list[READ_INDEX]  # Where to read the next value
        next_value = shared_list[next_index]  # Read the value

        # Check if it's the stop signal or a valid data
        if next_value == STOP_VALUE:
            go = False
        else:
            shared_list[RESULT_INDEX] = next_value  # Store or process the value
            print(next_value, end=", ", flush=True)  # Display the value
            shared_list[READ_INDEX] = (
                shared_list[READ_INDEX] + 1
            ) % BUFFER_SIZE  # Update the read index

        lock.release()  # Release exclusive access
        write_sem.release()  # Signal that there's space to write


def main():
    items_to_send = random.randint(
        1000, 10000
    )  # Determine the number of values to send

    smm = SharedMemoryManager()  # Manage shared memory across processes
    smm.start()  # Start the shared memory manager

    shared_list = smm.ShareableList(
        [0] * (BUFFER_SIZE + 4)
    )  # Create the shared buffer with extra control spaces

    # Initialize synchronization primitives
    lock = mp.Lock()  # Ensure exclusive access to the shared buffer
    write_sem = mp.Semaphore(
        BUFFER_SIZE
    )  # Control the number of writes based on buffer size
    read_sem = mp.Semaphore(0)  # Control the number of reads based on data availability

    # Create writer and reader processes
    writers = [
        mp.Process(
            target=write, args=(items_to_send, lock, write_sem, read_sem, shared_list)
        )
        for _ in range(WRITERS)
    ]
    readers = [
        mp.Process(target=read, args=(lock, write_sem, read_sem, shared_list))
        for _ in range(READERS)
    ]

    # Start all processes
    for process in readers + writers:
        process.start()

    # Wait for all processes to complete
    for process in readers + writers:
        process.join()

    print(f"\n\n{items_to_send} values sent")
    print(f"{shared_list[RESULT_INDEX]} values received")

    smm.shutdown()  # Clean up the shared memory manager


if __name__ == "__main__":
    main()
