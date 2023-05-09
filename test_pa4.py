# File: test_pa4.py
# Author: John Glick    
# Date: April 11, 2023
# Description: Program that tests the correctness
#              of pa4, comp 480, spring 2023.

import sys
import math
from time import process_time

# import the module containing pa1 solution
import pa4


def read_input_file(input_filename):
    """
    Reads the input file, and returns a tuple
    of the fixed entries, where each tuple
    is (og_row, og_col, val).
    """

    with open(input_filename) as f:
        fixed_vals = []
        for line in f:
            line_entries = line.split()
            row = int(line_entries[0].strip())
            col = int(line_entries[1].strip())
            val = line_entries[2].strip()
            fixed_vals.append((row, col, val))
    return fixed_vals


def read_solution_file(size, solution_filename):
    """
    Reads solution for a problem whose size is "size" 
    from the file solution_filename.
    Returns the solution as a nested list containing
    the correct value in each cell.  The og_row is the first
    index of the nested list.  If the problem is infeasible,
    None is returned.
    """

    with open(solution_filename) as f:
        # Read first line
        first_line = f.readline()
        if first_line.strip() == "Infeasible":
            return None
        else:
            f.seek(0)  # reset file so we're reading from the beginning again
            sol = []
            for r in range(size):
                sol.append([val.strip() for val in f.readline().split()])
            return sol


def is_solution(size, solution, fixed_vals):
    """
    Checks if solution is valid.  Problem size is size.
    Fixed values of entries (from the problem input) are
    in fixed_vals, as a list of (og_row, og_col, val) tuples.
    Returns True or False.
    """
    # Values of entries
    values = "123456789ABCDEFG"[:size]
    submatrix_size = round(math.sqrt(size))

    # Check fixed vals
    for r, c, val in fixed_vals:
        if solution[r - 1][c - 1] != val:
            return False

    # Check columns
    for c in range(size):
        entries = set(values)
        for r in range(size):
            entries.remove(solution[r][c])
        if len(entries) > 0:
            return False

    # Check rows
    for r in range(size):
        entries = set(values)
        for c in range(size):
            entries.remove(solution[r][c])
        if len(entries) > 0:
            return False

    # Check submatrices
    for submatrix_row in range(submatrix_size):
        for submatrix_col in range(submatrix_size):
            entries = set(values)
            for r in range(submatrix_row * submatrix_size, (submatrix_row + 1) * submatrix_size):
                for c in range(submatrix_col * submatrix_size, (submatrix_col + 1) * submatrix_size):
                    entries.remove(solution[r][c])
            if len(entries) > 0:
                return False

    # Everything ok
    return True


if __name__ == "__main__":

    # Print message
    print("Testing your program.\n")

    TARGET_RUN_TIME = 2

    # The tests to run
    tests = [(9, "p1.txt", "p1Sol.txt"),
             (9, "p2.txt", "p2Sol.txt"),
             (9, "p3.txt", "p3Sol.txt"),
             (9, "p4.txt", "p4Sol.txt"),
             (9, "p5.txt", "p5Sol.txt"),
             (9, "p6.txt", "p6Sol.txt"),
             (9, "p7.txt", "p7Sol.txt"),
             (9, "p8.txt", "p8Sol.txt"),
             (9, "p9.txt", "p9Sol.txt"),
             (9, "p10.txt", "p10Sol.txt"),
             (9, "p11.txt", "p11Sol.txt"),
             (9, "p12.txt", "p12Sol.txt"),
             (16, "p13.txt", "p13Sol.txt"),
             (25, "p14.txt", "p14Sol.txt"),
             (9, "p15.txt", "p15Sol.txt"),
             (16, "p16.txt", "p16Sol.txt"),
             (25, "p17.txt", "p17Sol.txt"),
             (25, "p18.txt", "p18Sol.txt")]

    # Initialize some things
    num_tests = 0
    num_correct = 0
    start_time = process_time()

    # Run the tests
    for test in tests:
        # Get problem specs
        size = test[0]
        input_filename = test[1]
        solution_filename = test[2]

        # Print message
        print(f"Running test size {size} from file {input_filename}")

        # Read input file
        fixed_vals = read_input_file(input_filename)

        # Read solution file
        solution = read_solution_file(size, solution_filename)

        # Solve the problem
        your_solution, number_nodes_generated = pa4.solve(size, input_filename)

        # Check your answer
        num_tests += 1
        if your_solution == solution:
            print("Correct solution")
            num_correct += 1
        elif your_solution and is_solution(size, your_solution, fixed_vals):
            print("Correct solution")
            num_correct += 1
        else:
            print("Incorrect solution")
            print(f"Your solution =\n{your_solution}")
            print(f"Correct solution =\n{solution}")
        print(f"Your number of nodes generated = {number_nodes_generated}\n\n")

    # Get running time
    processor_time = process_time() - start_time
    print(f"Processor time = {processor_time} seconds")
    if processor_time > TARGET_RUN_TIME:
        print("Your run time higher than the target.  Look to make your program more efficient.")

    # Check number of correct answers
    if num_tests == num_correct:
        print("All tests correct.")
    else:
        print("Some incorrect output on these tests.  Keep working on it")
