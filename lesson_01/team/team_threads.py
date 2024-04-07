"""
Course: CSE 251 
Lesson: L01 Team Activity
File:   team.py
Author: <Add name here>

Purpose: Find prime numbers

Instructions:

- Don't include any other Python packages or modules
- Review and follow the team activity instructions (team.md)
"""

from datetime import datetime, timedelta
import threading
import random

# Include cse 251 common Python files
from cse251 import *

# Global variable for counting the number of primes found
prime_count = 0
numbers_processed = 0


def is_prime(n):
    """
    Primality test using 6k+-1 optimization.
    From: https://en.wikipedia.org/wiki/Primality_test
    """

    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i**2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def thread_function(start, end, lock_prime, lock_processed):
    global prime_count
    global numbers_processed
    for i in range(start, end):
        if is_prime(i):
            with lock_prime:
                prime_count += 1
            print(i, end=", ", flush=True)

        with lock_processed:
            numbers_processed += 1


if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer()

    # TODO 1) Get this program running
    # TODO 2) move the following for loop into 1 thread

    # TODO 3) change the program to divide the for loop into 10 threads
    # TODO 4) change range_count to 100007.  Does your program still work?  Can you fix it?
    # Question: if the number of threads and range_count was random, would your program work?

    start = 10000000000
    range_count = 100007
    number_threads = 10
    thread_range = range_count // number_threads
    threads = []

    lock_prime = threading.Lock()
    lock_processed = threading.Lock()

    for i in range(number_threads):
        thread_start = start + (thread_range * i)
        thread_end = thread_start + thread_range
        thread = threading.Thread(
            target=thread_function,
            args=(thread_start, thread_end, lock_prime, lock_processed),
        )
        threads.append(thread)

    # Start
    for thread in threads:
        thread.start()

    # Join
    for thread in threads:
        thread.join()

    print(flush=True)

    # Should find 4306 primes
    log.write(f"Numbers processed = {numbers_processed}")
    log.write(f"Primes found      = {prime_count}")
    log.stop_timer("Total time")
