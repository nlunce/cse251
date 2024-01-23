"""
Course: CSE 251 
Lesson: L02 Prove
File:   prove.py
Author: Nathan

Purpose: Retrieve Star Wars details from a server

Instructions:

- Each API call must only retrieve one piece of information
- You are not allowed to use any other modules/packages except for the ones used
  in this assignment.
- Run the server.py program from a terminal/console program.  Simply type
  "python server.py" and leave it running.
- The only "fixed" or hard coded URL that you can use is TOP_API_URL.  Use this
  URL to retrieve other URLs that you can use to retrieve information from the
  server.
- You need to match the output outlined in the description of the assignment.
  Note that the names are sorted.
- You are required to use a threaded class (inherited from threading.Thread) for
  this assignment.  This object will make the API calls to the server. You can
  define your class within this Python file (ie., no need to have a separate
  file for the class)
- Do not add any global variables except for the ones included in this program.

The call to TOP_API_URL will return the following Dictionary(JSON).  Do NOT have
this dictionary hard coded - use the API call to get this.  Then you can use
this dictionary to make other API calls for data.

{
   "people": "http://127.0.0.1:8790/people/", 
   "planets": "http://127.0.0.1:8790/planets/", 
   "films": "http://127.0.0.1:8790/films/",
   "species": "http://127.0.0.1:8790/species/", 
   "vehicles": "http://127.0.0.1:8790/vehicles/", 
   "starships": "http://127.0.0.1:8790/starships/"
}
"""

from datetime import datetime, timedelta
import requests
import json
import threading

# Include cse 251 common Python files
from cse251 import *

# Const Values
TOP_API_URL = "http://127.0.0.1:8790"

# Global Variables
call_count = 0


# TODO Add your threaded class definition here
class Request_thread(threading.Thread):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.response = {}
        self.status_code = {}

    def run(self):
        response = requests.get(self.url)
        self.status_code = response.status_code
        if response.status_code == 200:
            self.response = response.json()
        else:
            print("RESPONSE = ", response.status_code)


# TODO Add any functions you need here
def get_film_details(top_api_urls, film_number):
    global call_count
    req = Request_thread(top_api_urls["films"] + film_number)
    call_count += 1
    req.start()
    req.join()
    film = req.response

    film_details = {
        "title": film["title"],
        "director": film["director"],
        "producer": film["producer"],
        "release_date": film["release_date"],
        "character_names": get_names(film["characters"]),
        "planet_names": get_names(film["planets"]),
        "starship_names": get_names(film["starships"]),
        "vehicle_names": get_names(film["vehicles"]),
        "species_names": get_names(film["species"]),
    }

    return film_details


def get_names(url_list):
    global call_count
    threads = []
    for e in url_list:
        req = Request_thread(e)
        threads.append(req)
        call_count += 1
        req.start()

    for thread in threads:
        thread.join()

    data = [thread.response for thread in threads]

    names = []

    for e in data:
        names.append(e["name"])

    sorted_names = sorted(names)

    return sorted_names


def display_details(log, film_details):
    global call_count
    log.write(f"Title: {film_details['title']}")
    log.write(f"Director: {film_details['director']}")
    log.write(f"Producer: {film_details['producer']}")
    log.write(f"Released: {film_details['release_date']}")

    character_count = len(film_details["character_names"])
    log.write()
    log.write(f"Characters: {character_count}")
    log.write(str(film_details["character_names"])[1:-1].replace("'", ""))
    log.write()

    planet_count = len(film_details["planet_names"])
    log.write(f"Planets: {planet_count}")
    log.write(str(film_details["planet_names"])[1:-1].replace("'", ""))
    log.write()

    starship_count = len(film_details["starship_names"])
    log.write(f"Starships: {starship_count}")
    log.write(str(film_details["starship_names"])[1:-1].replace("'", ""))
    log.write()

    vehicle_count = len(film_details["vehicle_names"])
    log.write(f"Vehicles: {vehicle_count}")
    log.write(str(film_details["vehicle_names"])[1:-1].replace("'", ""))
    log.write()

    species_count = len(film_details["species_names"])
    log.write(f"Species: {species_count}")
    log.write(str(film_details["species_names"])[1:-1].replace("'", ""))
    log.write()

    # # lists


def create_threads(url_list):
    thread_list = []  # Stores threads

    # Creates threads and adds them to thread list
    for url in url_list:
        thread = Request_thread(url)
        thread_list.append(thread)

    return thread_list


def main():
    global call_count
    log = Log(show_terminal=True)
    log.start_timer("Starting to retrieve data from the server")

    # TODO Retrieve Top API urls
    req = Request_thread(TOP_API_URL)
    call_count += 1
    req.start()
    req.join()
    top_api_urls = req.response

    # TODO Retrieve Details on film 6
    desired_film = "6"
    film_details = get_film_details(top_api_urls, desired_film)

    # TODO Display results
    display_details(log, film_details)

    log.stop_timer("Total Time To complete")
    log.write(f"There were {call_count} calls to the server")


if __name__ == "__main__":
    main()
