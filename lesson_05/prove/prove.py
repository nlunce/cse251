"""
Course: CSE 251 
Lesson: L05 Prove
File:   prove.py
Author: <Add name here>

Purpose: Assignment 05 - Factories and Dealers

Instructions:

- Read the comments in the following code.  
- Implement your code where the TODO comments are found.
- No global variables, all data must be passed to the objects.
- Only the included/imported packages are allowed.  
- Thread/process pools are not allowed
- You MUST use a barrier!
- Do not use try...except statements.
- You are not allowed to use the normal Python Queue object. You must use Queue251.
- The shared queue between the threads that are used to hold the Car objects
  can not be greater than MAX_QUEUE_SIZE.
"""

from datetime import datetime, timedelta
import time
import threading
import random

# Include cse 251 common Python files
from cse251 import *

# Global Constants.
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50

# NO GLOBAL VARIABLES!


class Car:
    """This is the Car class that will be created by the factories"""

    # Class Variables
    car_makes = (
        "Ford",
        "Chevrolet",
        "Dodge",
        "Fiat",
        "Volvo",
        "Infiniti",
        "Jeep",
        "Subaru",
        "Buick",
        "Volkswagen",
        "Chrysler",
        "Smart",
        "Nissan",
        "Toyota",
        "Lexus",
        "Mitsubishi",
        "Mazda",
        "Hyundai",
        "Kia",
        "Acura",
        "Honda",
    )

    car_models = (
        "A1",
        "M1",
        "XOX",
        "XL",
        "XLS",
        "XLE",
        "Super",
        "Tall",
        "Flat",
        "Middle",
        "Round",
        "A2",
        "M1X",
        "SE",
        "SXE",
        "MM",
        "Charger",
        "Grand",
        "Viper",
        "F150",
        "Town",
        "Ranger",
        "G35",
        "Titan",
        "M5",
        "GX",
        "Sport",
        "RX",
    )

    car_years = [i for i in range(1990, datetime.now().year)]

    def __init__(self):
        # Make a random car
        self.model = random.choice(Car.car_models)
        self.make = random.choice(Car.car_makes)
        self.year = random.choice(Car.car_years)

        # Sleep a little.  Last statement in this for loop - don't change
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))

        # Display the car that has was just created in the terminal
        # print(f"Created: {self.info()}")

    def info(self):
        """Helper function to quickly get the car information."""
        return f"{self.make} {self.model}, {self.year}"


class Queue251:
    """This is the queue object to use for this assignment. Do not modify!!"""

    def __init__(self):
        self.items = []
        self.max_size = 0

    def get_max_size(self):
        return self.max_size

    def put(self, item):
        self.items.append(item)
        if len(self.items) > self.max_size:
            self.max_size = len(self.items)

    def get(self):
        return self.items.pop(0)


class Factory(threading.Thread):
    """This is a factory.  It will create cars and place them on the car queue"""

    def __init__(
        self,
        car_queue,
        cars_in_queue,
        empty_car_slots,
        factory_id,
        barrier,
        dealer_count,
    ):
        super().__init__()
        self.cars_to_produce = random.randint(200, 300)  # DO NOT change
        self.car_queue = car_queue
        self.cars_in_queue = cars_in_queue
        self.empty_car_slots = empty_car_slots
        self.factory_id = factory_id
        self.barrier = barrier
        self.dealer_count = dealer_count

    def run(self):
        # TODO produce the cars, the send them to the dealerships
        for _ in range(self.cars_to_produce):

            car = Car()

            # Subtracts 1 from semephor keeping track of how many spots open at dealership
            self.empty_car_slots.acquire()
            self.car_queue.put(car)
            print(f"Factory {self.factory_id + 1} created: {car.info()} ")

            # Adds 1 to semephor keeping track of cars in queue
            self.cars_in_queue.release()

        # TODO wait until all of the factories are finished producing cars
        # waits for other factories to finish producing their cars
        self.barrier.wait()

        # TODO "Wake up/signal" the dealerships one more time.  Select one factory to do this
        if self.factory_id == 0:
            for i in range(self.dealer_count):
                self.cars_in_queue.release()
                self.car_queue.put(None)


class Dealer(threading.Thread):
    """This is a dealer that receives cars"""

    def __init__(
        self, car_queue, cars_in_queue, empty_car_slots, dealer_id, dealer_stats
    ):
        super().__init__()
        self.car_queue = car_queue
        self.cars_in_queue = cars_in_queue
        self.empty_car_slots = empty_car_slots
        self.dealer_id = dealer_id
        self.dealer_stats = dealer_stats

    def run(self):
        while True:
            # TODO handle a car
            # This represents selling a car -> it will decrease semephore by one and the size of the queue by one
            self.cars_in_queue.acquire()
            car = self.car_queue.get()

            # Checks if its the last car and if it is -> stops the while loop
            if car == None:
                break

            self.dealer_stats[self.dealer_id] += 1
            # This represents telling the factory 'we have an open spot for a new car'
            self.empty_car_slots.release()

            # Sleep a little - don't change.  This is the last line of the loop
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR + 0))


def run_production(factory_count, dealer_count):
    """This function will do a production run with the number of
    factories and dealerships passed in as arguments.
    """

    # TODO Create semaphore(s) if needed
    # 10 slots available
    empty_car_slots = threading.Semaphore(MAX_QUEUE_SIZE)

    # this should increase and deacrease with the queue
    cars_in_queue = threading.Semaphore(0)

    # TODO Create queue
    car_queue = Queue251()
    # TODO Create lock(s) if needed
    # TODO Create barrier
    barrier = threading.Barrier(factory_count)

    # This is used to track the number of cars received by each dealer
    dealer_stats = list([0] * dealer_count)

    # TODO create your factories, each factory will create a random amount of cars; your code must account for this.
    factories = []
    for factory_id in range(factory_count):
        factory = Factory(
            car_queue, cars_in_queue, empty_car_slots, factory_id, barrier, dealer_count
        )
        factories.append(factory)

    # NOTE: You have no control over how many cars a factory will create in this assignment.

    # TODO create your dealerships
    dealers = []
    for dealer_id in range(dealer_count):
        dealer = Dealer(
            car_queue, cars_in_queue, empty_car_slots, dealer_id, dealer_stats
        )
        dealers.append(dealer)

    log.start_timer()

    # TODO Start all factories
    for factory in factories:
        factory.start()

    # TODO Start all dealerships
    for dealer in dealers:
        dealer.start()

    # This is used to track the number of cars produced by each factory NOTE: DO NOT pass this into
    # your factories! You must collect this data here in `run_production` after the factories are finished.

    # TODO Wait for the factories and dealerships to complete; do not forget to get the factories stats
    for factory in factories:
        factory.join()

    for dealer in dealers:
        dealer.join()

    run_time = log.stop_timer(f"{sum(dealer_stats)} cars have been created.")

    # This function must return the following - Don't change!
    # factory_stats: is a list of the number of cars produced by each factory.
    #                collect this information after the factories are finished.

    factory_stats = [factory.cars_to_produce for factory in factories]
    return (run_time, car_queue.get_max_size(), dealer_stats, factory_stats)


def main(log):
    """Main function - DO NOT CHANGE!"""

    runs = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 5), (5, 2), (10, 10)]
    for factories, dealerships in runs:
        run_time, max_queue_size, dealer_stats, factory_stats = run_production(
            factories, dealerships
        )

        log.write(f"Factories      : {factories}")
        log.write(f"Dealerships    : {dealerships}")
        log.write(f"Run Time       : {run_time:.4f}")
        log.write(f"Max queue size : {max_queue_size}")
        log.write(f"Factory Stats  : Made = {sum(dealer_stats)} @ {factory_stats}")
        log.write(f"Dealer Stats   : Sold = {sum(factory_stats)} @ {dealer_stats}")
        log.write("")

        # The number of cars produces needs to match the cars sold
        assert sum(dealer_stats) == sum(factory_stats)


if __name__ == "__main__":
    log = Log(show_terminal=True)
    main(log)
