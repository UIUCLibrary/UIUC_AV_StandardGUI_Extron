################################################################################
# Copyright © 2023 The Board of Trustees of the University of Illinois
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

from typing import TYPE_CHECKING, Dict, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from extronlib.ui import Button, Label
    from modules.project.SystemHardware import SystemHardwareController

## Begin ControlScript Import --------------------------------------------------
from extronlib.system import Wait

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
import inspect
import re
import functools
import traceback

## End Python Imports ----------------------------------------------------------
##
## Begin Project Import -----------------------------------------------------------
from modules.helper.ModuleSupport import ProgramLogLogger, TraceLogger

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class SortKeys:
    
    @classmethod
    def StatusSort(cls, sortItem: Union['Button', 'Label']) -> int:
        if not hasattr(sortItem, 'Name'):
            raise IndexError('Sort item has no attribute Name')
        res = re.match(r'DeviceStatus(?:Icon|Label)-(\d+)', sortItem.Name)
        if res is None:
            raise ValueError('Sort item does not match regex')
        sortInt = int(res.group(1))
        return sortInt
    
    @classmethod
    def HardwareSort(cls, sortItem: 'SystemHardwareController') -> str:
        if not hasattr(sortItem, 'Id'):
            raise IndexError('Sort item has no attribute Id')
        return sortItem.Id
    
    @classmethod
    def SortDaysOfWeek(cls, sortItem: str) -> int:
        if type(sortItem) is not str:
            raise TypeError("sortItem must be a string")
        test = sortItem.lower()
        if test in ['monday', 'mon', 'm']:
            return 0
        elif test in ['tuesday', 'tues', 'tue', 'tu', 't']:
            return 1
        elif test in ['wednesday', 'wednes', 'wed', 'we', 'w']:
            return 2
        elif test in ['thursday', 'thurs', 'thu', 'th', 'r']:
            return 3
        elif test in ['friday', 'fri', 'fr', 'f']:
            return 4
        elif test in ['saturday', 'sat', 'sa', 's']:
            return 5
        elif test in ['sunday', 'sun', 'su', 'u']:
            return 6
        else:
            raise ValueError("sortItem must be a valid day of the week")

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------


class Logger():
    Prog = ProgramLogLogger()
    Trace = TraceLogger()

    @classmethod
    def Log(cls, *recordobjs, separator=' ', logSeverity='info') -> None:
        cls.Prog.Log(*recordobjs, sep=separator, severity=logSeverity)
        cls.Trace.Log(*recordobjs, sep=separator, severity=logSeverity)

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

def DictValueSearchByKey(dict: Dict, search_term: str, regex: bool=False, capture_dict: bool=False) -> Union[List, Dict]:
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

def debug(func): # pragma: no cover
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = ["{}={!r}".format(k, v) for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        callStr = "Calling {}({})".format(func.__name__, signature)
        Logger.Trace.Log(callStr)
        try:
            value = func(*args, **kwargs)
            rtnStr = "{!r} returned {!r}".format(func.__name__, value)
            Logger.Log(callStr, rtnStr, separator='\n')
            return value
        except Exception as inst:
            tb = traceback.format_exc()
            Logger.Log('An error occured attempting to call function. {} ({})\n    Exception ({}):\n        {}\n    Traceback:\n        {}'.format(func.__name__, signature, type(inst), inst, tb), logSeverity='error')
    return wrapper_debug

def RunAsync(func, callback: Callable=print):
    """Run this function asynchronously"""
    @functools.wraps(func)
    def wrapper_async(*args, **kwargs):
        # using Extron wait of 10ms to make the wrapped function effectively asynchronous
        @Wait(0.01)
        def AsyncRun(): # pragma: no cover
            value = func(*args, **kwargs)
            if callable(callback): # run callback with function output if callback is supplied and callable
                callback(value)
    return wrapper_async

## End Function Definitions ----------------------------------------------------
