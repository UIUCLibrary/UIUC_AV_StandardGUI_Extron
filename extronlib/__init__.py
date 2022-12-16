# This is a dummy module for unit testing extron control script code files
from typing import List
## METHOD DEFINITIONS ----------------------------------------------------------

def event(obj, EventName):
    if type(obj) == type([]):
        for o in obj:
            def event_wrapper(func1):
                func1(o, EventName)
    else:
        def event_wrapper(func2):
            func2(obj, EventName)
    return event_wrapper

def Version() -> str:
    return "1.3r8"

def Platform() -> str:
    return "Pro xi"

## -----------------------------------------------------------------------------