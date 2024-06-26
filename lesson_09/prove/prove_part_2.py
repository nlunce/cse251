"""
Course: CSE 251 
Lesson: L09 Prove Part 2
File:   prove_part_2.py
Author: Nathan 

Purpose: Part 2 of prove 9, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

<Answer here>
To update the program so that it shows the route, 
to the mazes exit I would create a data structure that can be accessed safely 
by different threads to track the path each thread takes. Every thread would add
its movements to this structure, labeled with an identifier (ID) to differentiate between paths. 
Once a thread reaches the end of the maze its path will be identified as the solution.


Why would it work?

<Answer here>
This method is effective as it ensures the consistency of
operations by using thread safe processes guaranteeing precise
path mapping in the presence of multiple threads. By focusing on 
monitoring and showcasing the path of the victorious thread,
distinguished by its distinct identifier this technique effectively 
illustrates the successful navigation through the maze utilizing parallel exploration, 
for enhanced speed and precision.


"""

import math
import threading
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 251 files
from cse251 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (128, 0, 0),
    (128, 128, 0),
    (0, 128, 0),
    (128, 0, 128),
    (0, 128, 128),
    (0, 0, 128),
    (72, 61, 139),
    (143, 143, 188),
    (226, 138, 43),
    (128, 114, 250),
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED


def get_color():
    """Returns a different color when called"""
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


# TODO: Add any function(s) you need, if any, here.
def explore_maze_threaded(maze, current_position, condition, stop, color):
    global thread_count
    with condition:
        if stop[0]:
            return

    if maze.at_end(current_position[0], current_position[1]):
        with condition:
            stop[0] = True
            condition.notify_all()
        return

    possible_moves = maze.get_possible_moves(current_position[0], current_position[1])
    threads = []  # Keep track of threads to join at intersections

    for move in possible_moves:
        with condition:
            if stop[0]:
                break

        # Move and color in the current thread's color
        maze.move(move[0], move[1], color)

        if len(possible_moves) > 1:  # At an intersection, spawn new threads
            with condition:
                thread_count += 1

            new_thread = threading.Thread(
                target=explore_maze_threaded,
                args=(maze, move, condition, stop, get_color()),
            )
            threads.append(new_thread)
            new_thread.start()
        else:
            # Continue exploration in the current thread if not at an intersection
            explore_maze_threaded(maze, move, condition, stop, color)

    # Wait for all spawned threads at this intersection to complete
    for thread in threads:
        thread.join()


def solve_find_end(maze):
    """Finds the end position using threads. Nothing is returned."""
    # When one of the threads finds the end position, stop all of them.
    global stop, thread_count
    stop = [False]
    thread_count = 0  # Reset thread count for each maze
    condition = threading.Condition()
    initial_color = get_color()
    start_pos = maze.get_start_pos()

    initial_thread = threading.Thread(
        target=explore_maze_threaded,
        args=(maze, start_pos, condition, stop, initial_color),
    )
    initial_thread.start()
    initial_thread.join()  # Wait for the initial thread to complete


def find_end(log, filename, delay):
    """Do not change this function"""

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f"Number of drawing commands = {screen.get_command_count()}")
    log.write(f"Number of threads created  = {thread_count}")

    done = False
    while not done:
        if screen.play_commands(speed):
            key = cv2.waitKey(0)
            if key == ord("1"):
                speed = SLOW_SPEED
            elif key == ord("2"):
                speed = FAST_SPEED
            elif key == ord("q"):
                exit()
            elif key != ord("p"):
                done = True
        else:
            done = True


def find_ends(log):
    """Do not change this function"""

    files = (
        ("very-small.bmp", True),
        ("very-small-loops.bmp", True),
        ("small.bmp", True),
        ("small-loops.bmp", True),
        ("small-odd.bmp", True),
        ("small-open.bmp", False),
        ("large.bmp", False),
        ("large-loops.bmp", False),
        ("large-squares.bmp", False),
        ("large-open.bmp", False),
    )

    log.write("*" * 40)
    log.write("Part 2")
    for filename, delay in files:
        filename = f"./mazes/{filename}"
        log.write()
        log.write(f"File: {filename}")
        find_end(log, filename, delay)
    log.write("*" * 40)


def main():
    """Do not change this function"""
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()
