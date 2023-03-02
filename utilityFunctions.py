## Begin ControlScript Import --------------------------------------------------
# from extronlib import event, Version
# from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
# from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
#     DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
#     EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
#     RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
#     VolumeInterface)
# from extronlib.ui import Button, Knob, Label, Level, Slider
# from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
#     ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)
#
#print(Version()) ## Sanity check ControlScript Import
from extronlib.system import ProgramLog
from extronlib.system import Wait
## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
from datetime import datetime
import json
from typing import Dict, Tuple, List
import inspect
import re
import functools
import traceback

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def Log(content, level: str='info', stack: bool=False) -> None:
    """Logs data with Extron ProgramLog. Included helpful troubleshooting log header.

    Args:
        content (Any): Content to log. Must be a string or printable as a string.
        level (str, optional): Log level. May be 'info', 'warning', or 'error'. Defaults to 'info'.
        stack (bool, optional): Whether or not to print the function call stack. Defaults to False.
    """    
    
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    
    regex = r"^(?:\/var\/nortxe\/proj\/eup\/|\/var\/nortxe\/uf\/admin\/modules\/|\/usr\/lib\/python3.5\/)?(.+)\.py$"
    
    re_match = re.match(regex, calframe[1].filename)
    fileName = re_match.group(1)
    mod = fileName.replace('/', '.')
    ws = '    '
    
    content = str(content).replace('\n', '\n{0}'.format(ws))
    
    if stack:
        # show call stack back to main
        message = 'Logging from {module} - {func} ({line})\n'.format(
                       module = mod,
                       func = calframe[1].function,
                       line = calframe[1].lineno
                    )
        message = message + '{w}Stack:\n'.format(w=ws)
        i = 2
        while i < len(calframe):
            parent = calframe[i]
            loop_match = re.match(regex, parent.filename)
            if loop_match == None:
                parent_mod = parent.filename
            else:
                parent_fn = loop_match.group(1)
                parent_mod = parent_fn.replace('/','.')
            message = message + '{w}{module} - {func} ({line})\n'.format(
                w = ws+ws,
                module = parent_mod,
                func = parent.function,
                line = parent.lineno
            )
            i += 1
            if ((parent_mod == 'main' and parent.function == '<module>')
                 or (parent_mod == 'extronlib.system.Timer' and parent.function == '__callback')
                 or (parent_mod == 'Extron.ButtonObject' and parent.function == '_handleMsgAcquired')):
                break
        
        message = message + '{w}{content}'.format(w = ws, content = content)
    else:
        message = ("Logging from {module} - {func} ({line})\n{w}{content}""".
                   format(
                       module = mod,
                       func = calframe[1].function,
                       line = calframe[1].lineno,
                       w = ws,
                       content = content
                    )
                   )
    
    ProgramLog(message, level)

def TimeIntToStr(time: int, units: bool = True) -> str:
    """Converts integer seconds to human readable string

    Args:
        time (int): integer time in seconds
        units (bool, optional): True to display units (m minutes s seconds) or
            false to return a unitless string (DD:HH:MM:SS). Defaults to True.

    Returns:
        str: Time string
    """    
    returnStr = ''
    seconds = 0
    minutes = 0
    hours = 0
    days = 0

    if time < 60:
        seconds = time
    elif time > 60:
        seconds = time % 60
        minutes = time // 60
        if minutes > 60:
            hours = minutes // 60
            minutes = minutes % 60
            if hours > 24:
                days = hours // 24
                hours = hours % 24

    if units:
        uS = "seconds"
        uM = "minutes"
        uH = "hours"
        uD = "days"
        if seconds == 1:
            uS = 'second'
        if minutes == 1:
            uM = 'minute'
        if hours == 1:
            uH = 'hour'
        if days == 1:
            uD = 'day'
        if days != 0:
            returnStr = "{d} {unitD}, {hr} {unitH}, {min} {unitM}, {sec} {unitS}"\
                .format(d=days,
                        unitD=uD,
                        hr=hours,
                        unitH=uH,
                        min=minutes,
                        unitM=uM,
                        sec=seconds,
                        unitS=uS)
        elif days == 0 and hours != 0:
            returnStr = "{hr} {unitH}, {min} {unitM}, {sec} {unitS}"\
                .format(hr=hours,
                        unitH=uH,
                        min=minutes,
                        unitM=uM,
                        sec=seconds,
                        unitS=uS)
        elif days == 0 and hours == 0 and minutes != 0:
            returnStr = "{min} {unitM}, {sec} {unitS}"\
                .format(min=minutes,
                        unitM=uM,
                        sec=seconds,
                        unitS=uS)
        elif days == 0 and hours == 0 and minutes == 0:
            returnStr = "{sec} {unitS}".format(sec=seconds, unitS=uS)
    else:
        returnStr = "{d}:{hr}:{min}:{sec}".format(d=days,
                                                  hr=str(hours).zfill(2),
                                                  min=str(minutes).zfill(2),
                                                  sec=str(seconds).zfill(2))

    return returnStr

def DictValueSearchByKey(dict: Dict, search_term: str, regex: bool=False, capture_dict: bool=False) -> List:
    """Searches dictionary keys which match the search term (either partial match or regex match)
    Returns a list of matching values.

    Args:
        dict (Dict): Dictionary to search
        search_term (str): String search string or regex pattern to match
        regex (bool, optional): Regex search flag. Defaults to False.
        capture_dict (bool, optional): Creates a dict using the first cature group for the key. search_term must be a regex search with a capture group and regex must be true. Defaults to False.

    Returns:
        List: Returns a list of values of keys matching the search.
    """    
    if not capture_dict:
        # Log('Finding List')
        find_list = []
        for key, value in dict.items():
            if regex:
                re_match = re.match(search_term, key)
                if re_match != None:
                    find_list.append(value)
            else:
                if search_term in key:
                    find_list.append(value)
                    
        return find_list
    elif capture_dict and regex:
        # Log('Finding Dict')
        find_dict = {}
        for key, value in dict.items():
            re_match = re.match(search_term, key)
            if re_match != None and re_match.group(1) != None:
                find_dict[re_match.group(1)] = value
        return find_dict
    else:
        raise ValueError('regex must be true if capture_dict is true')

def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = ["{}={!r}".format(k, v) for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        callStr = "Calling {}({})".format(func.__name__, signature)
        print(callStr)
        try:
            value = func(*args, **kwargs)
            rtnStr = "{!r} returned {!r}".format(func.__name__, value)
            print(rtnStr)
            Log('{}\n  {}'.format(callStr, rtnStr))
            return value
        except Exception as inst:
            tb = traceback.format_exc()
            print(tb)
            Log('An error occured attempting to call function. {} ({})\n    Exception ({}):\n        {}\n    Traceback:\n        {}'.format(func.__name__, signature, type(inst), inst, tb), 'error')
    return wrapper_debug

def RunAsync(func, callback: callable=None):
    """Run this function asynchronously"""
    @functools.wraps(func)
    def wrapper_async(*args, **kwargs):
        # using Extron wait of 10ms to make the wrapped function effectively asynchronous
        @Wait(0.01)
        def AsyncRun():
            value = func(*args, **kwargs)
            if callable(callback): # run callback with function output if callback is supplied and callable
                callback(value)
    return wrapper_async

## End Function Definitions ----------------------------------------------------
##
## Begin Script Definition -----------------------------------------------------
if __name__ == "__main__": ## this module does not run as a script
    pass
## End Script Definition -------------------------------------------------------


