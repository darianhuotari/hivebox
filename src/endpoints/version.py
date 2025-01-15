"""Module providing an application version."""

#VERSION = "0.0.9"

#import sys
#import os
#sys.path.append(os.path.abspath('../'))

#with open("../VERSION") as file:
#    VERSION = file.read()

#print(VERSION)

with open("VERSION", "r", encoding="utf-8") as file:
    VERSION = file.read()

def list_version():
    """
    Args: None
        
    Returns: Application version

    """
    return VERSION
