'''
Created on 18.11.2016

Some basic classes for generating and managing identities

@author: martin
'''
# standard libraries
import string
import random

def id_generator(
                 size=6, 
                 chars=string.ascii_uppercase + string.ascii_lowercase + string.digits
                 ):
    """ Creates a unique ID consisting of a given number of characters with 
    a given set of characters """
    return ''.join(random.choice(chars) for _ in range(size))