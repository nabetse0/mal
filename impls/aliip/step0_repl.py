"""
"""

import sys

def read(user_input):
    return user_input

def eval(s):
    return s

def print_result(result):
    return result

def rep(user_input):
    return print_result(eval(read(user_input)))


def main(argv):
    while True:
        user_input = input("user> ")

        # Handle ctrl-D
        # For some reason, we're not getting EOFError 
        if user_input == chr(4):  
            break

        print(rep(user_input))

    return


if __name__ == "__main__":
    main(sys.argv)
