"""
Course: CSE 251 
Lesson: L09 Prove Part 1
File:   prove_part_1.py
Author: Nathan Lunceford

Purpose: Part 1 of prove 9, finding the path to the end of a maze using recursion.

Instructions:

- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- Complete any TODO comments.
"""

import math
from screen import Screen
from maze import Maze
import cv2
import sys

# Include cse 251 files
from cse251 import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)
SLOW_SPEED = 100
FAST_SPEED = 1
speed = FAST_SPEED

# TODO: Add any functions needed here.


def explore_maze(maze, path):
    # Get the current position
    current_position = path[-1]

    # Check if we reached the goal
    if maze.at_end(current_position[0], current_position[1]):
        print("Goal reached:", path)
        return True

    # Get possible moves from the current position
    possible_moves = maze.get_possible_moves(current_position[0], current_position[1])

    # Iterate through possible moves
    for move in possible_moves:
        # Check if the move is already visited
        if move not in path:
            # Move to the next position
            maze.move(move[0], move[1], COLOR)
            path.append(move)

            # Recursively explore from the new position
            if explore_maze(maze, path):
                return True

            # Backtrack if the current path didn't lead to the goal
            maze.restore(move[0], move[1])
            path.pop()

    return False


def solve_path(maze):
    """Solve the maze and return the path found between the start and end positions.
    The path is a list of positions, (x, y)"""
    path = []
    # TODO: Solve the maze recursively while tracking the correct path.

    starting_position = maze.get_start_pos()
    path = [starting_position]
    explore_maze(maze, path)

    return path


def get_path(log, filename):
    """Do not change this function"""
    # 'Maze: Press "q" to quit, "1" slow drawing, "2" faster drawing, "p" to play again'
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename)

    path = solve_path(maze)

    log.write(f"Drawing commands to solve = {screen.get_command_count()}")

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

    return path


def find_paths(log):
    """Do not change this function"""

    files = (
        "very-small.bmp",
        "very-small-loops.bmp",
        "small.bmp",
        "small-loops.bmp",
        "small-odd.bmp",
        "small-open.bmp",
        "large.bmp",
        "large-loops.bmp",
        # 'large-squares.bmp',
        # 'large-open.bmp'
    )

    log.write("*" * 40)
    log.write("Part 1")
    for filename in files:
        filename = f"./mazes/{filename}"
        log.write()
        log.write(f"File: {filename}")
        path = get_path(log, filename)
        log.write(f"Found path has length     = {len(path)}")
    log.write("*" * 40)


def main():
    """Do not change this function"""
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_paths(log)


if __name__ == "__main__":
    main()
