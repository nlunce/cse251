"""
Course: CSE 251 
Lesson: L07 Prove
File:   prove.py
Author: Nathan

Purpose: Process Task Files.

Instructions:

See Canvas for the full instructions for this assignment. You will need to complete the TODO comment
below before submitting this file:

TODO:

Add your comments here on the pool sizes that you used for your assignment and why they were the best choices.

I have 6 cores with 12 threads on my computer

PRIME_POOL_SIZE = 12
- Prime number checking is intensive computational work. Utilizing all twelve pyhsical threads allows for maximizing the processing of these CPU-bound tasks.

WORD_POOL_SIZE = 6
- Processing words, such as searching within a file, is relatively less CPU-intensive. A pool size of 6 is chosen to allocate half of the system's threads to these tasks, allowing other tasks to run concurrently without starving them of CPU resources.

UPPER_POOL_SIZE = 6
- Similar to word processing, converting text to uppercase is not highly CPU-demanding. Allocating three cores/six pyhsical threads to this task type ensures that it has enough resources to complete quickly while leaving room for more demanding tasks.

SUM_POOL_SIZE = 12
- This is more computationaly intensive. With six cores/12 threads, this task type is allocated enough resources to significantly speed up computation, taking full advantage of the system's CPU capabilities.

NAME_POOL_SIZE = 12
- Although making HTTP requests is primarily I/O-bound, having a higher pool size can help overlap network latency and potentially improve throughput. With six cores/12 threads, dedicating more resources to this task type can enhance overall performance, especially when network responses are the bottleneck.

"""

from datetime import datetime, timedelta
import requests
import multiprocessing as mp
from matplotlib.pylab import plt
import numpy as np
import glob
import math

# Include cse 251 common Python files - Dont change
from cse251 import *

# Constants - Don't change
TYPE_PRIME = "prime"
TYPE_WORD = "word"
TYPE_UPPER = "upper"
TYPE_SUM = "sum"
TYPE_NAME = "name"

# TODO: Change the pool sizes and explain your reasoning in the header comment

PRIME_POOL_SIZE = 12
WORD_POOL_SIZE = 6
UPPER_POOL_SIZE = 6
SUM_POOL_SIZE = 12
NAME_POOL_SIZE = 12

# Global lists to collect the task results
result_primes = []
result_words = []
result_upper = []
result_sums = []
result_names = []


def task_prime_callback(result):
    result_primes.append(result)


def task_word_callback(result):
    result_words.append(result)


def task_upper_callback(result):
    result_upper.append(result)


def task_sum_callback(result):
    result_sums.append(result)


def task_name_callback(result):
    result_names.append(result)


def is_prime(n: int):
    """Primality test using 6k+-1 optimization.
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


def task_prime(value):
    """
    Use the is_prime() above
    Add the following to the global list:
        {value} is prime
            - or -
        {value} is not prime
    """
    prime_result = is_prime(value)
    result_text = f"{value} is prime" if prime_result else f"{value} is not prime"
    return result_text


def task_word(word):
    """
    search in file 'words.txt'
    Add the following to the global list:
        {word} Found
            - or -
        {word} not found *****
    """
    with open("words.txt") as file:
        words_set = set(file.read().splitlines())
    if word in words_set:
        return f"{word} Found"
    else:
        return f"{word} not found *****"


def task_upper(text):
    """
    Add the following to the global list:
        {text} ==>  uppercase version of {text}
    """
    upper_text = f"{text} ==> {text.upper()}"
    return upper_text


def task_sum(start_value, end_value):
    """
    Add the following to the global list:
        sum of {start_value:,} to {end_value:,} = {total:,}
    """
    total = sum(range(start_value, end_value + 1))
    sum_result = f"sum of {start_value:,} to {end_value:,} = {total:,}"
    return sum_result


def task_name(url):
    """
    use requests module
    Add the following to the global list:
        {url} has name <name>
            - or -
        {url} had an error receiving the information
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        name = data.get("name", "Name not found")
        return f"{url} has name {name}"
    else:
        return f"{url} had an error receiving the information"


def main():
    log = Log(show_terminal=True)
    log.start_timer()

    # TODO Create process pools
    prime_pool = mp.Pool(PRIME_POOL_SIZE)
    word_pool = mp.Pool(WORD_POOL_SIZE)
    upper_pool = mp.Pool(UPPER_POOL_SIZE)
    sum_pool = mp.Pool(SUM_POOL_SIZE)
    name_pool = mp.Pool(NAME_POOL_SIZE)
    # TODO change the following to start the pools

    count = 0
    task_files = glob.glob("tasks/*.task")
    for filename in task_files:
        # print()
        # print(filename)
        task = load_json_file(filename)
        print(task)
        count += 1
        task_type = task["task"]
        if task_type == TYPE_PRIME:
            prime_pool.apply_async(
                task_prime, args=(task["value"],), callback=task_prime_callback
            )
        elif task_type == TYPE_WORD:
            word_pool.apply_async(
                task_word, args=(task["word"],), callback=task_word_callback
            )
        elif task_type == TYPE_UPPER:
            upper_pool.apply_async(
                task_upper, args=(task["text"],), callback=task_upper_callback
            )
        elif task_type == TYPE_SUM:
            sum_pool.apply_async(
                task_sum, args=(task["start"], task["end"]), callback=task_sum_callback
            )
        elif task_type == TYPE_NAME:
            name_pool.apply_async(
                task_name, args=(task["url"],), callback=task_name_callback
            )
        else:
            log.write(f"Error: unknown task type {task_type}")

    # TODO wait on the pools
    pools = [prime_pool, word_pool, upper_pool, sum_pool, name_pool]
    for pool in pools:
        pool.close()
        pool.join()

    # DO NOT change any code below this line!
    # ---------------------------------------------------------------------------
    def log_list(lst, log):
        for item in lst:
            log.write(item)
        log.write(" ")

    log.write("-" * 80)
    log.write(f"Primes: {len(result_primes)}")
    log_list(result_primes, log)

    log.write("-" * 80)
    log.write(f"Words: {len(result_words)}")
    log_list(result_words, log)

    log.write("-" * 80)
    log.write(f"Uppercase: {len(result_upper)}")
    log_list(result_upper, log)

    log.write("-" * 80)
    log.write(f"Sums: {len(result_sums)}")
    log_list(result_sums, log)

    log.write("-" * 80)
    log.write(f"Names: {len(result_names)}")
    log_list(result_names, log)

    log.write(f"Number of Primes tasks: {len(result_primes)}")
    log.write(f"Number of Words tasks: {len(result_words)}")
    log.write(f"Number of Uppercase tasks: {len(result_upper)}")
    log.write(f"Number of Sums tasks: {len(result_sums)}")
    log.write(f"Number of Names tasks: {len(result_names)}")
    log.stop_timer(f"Total time to process {count} tasks")


if __name__ == "__main__":
    main()
