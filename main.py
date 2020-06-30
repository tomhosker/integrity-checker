"""
This is the entry point for the Integrity Checker program.
"""

# Local imports.
from comparator import Comparator, demo
from inputs import FIRST_ROOT, SECOND_ROOT

#############
# FUNCTIONS #
#############

def run_from_inputs():
    """ Run the Comparator class, using the inputs in inputs.py. """
    cmptr = Comparator(FIRST_ROOT, SECOND_ROOT)
    cmptr.walk_and_write()

def run_a_demo():
    """ Run a demonstration. """
    demo()

###################
# RUN AND WRAP UP #
###################

def run():
    #run_from_inputs()
    run_a_demo()

if __name__ == "__main__":
    run()
