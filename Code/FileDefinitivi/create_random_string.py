import random
import string

"""python and xml tree don't recognize the char ":" inside the tag.
change ":" with an upper string of 4 chars that doens't exist in the file"""
def createRandomChanger(file):
    running = True
    while running:
        random_choice = ""
        for i in [1,2,3,4]: # create a string of 4 chars
            random_choice = random_choice + random.choice(string.ascii_letters).upper()
            if i == 4 and not random_choice in file: # check if string doesn't exist in the file
                running = False
    return random_choice
