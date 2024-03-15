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

from typing import TYPE_CHECKING, Dict, List, Union, Callable, Any, Tuple
if TYPE_CHECKING: # pragma: no cover
    from extronlib.ui import Button
    from modules.project.Devices import SystemHardwareController
    import Constants

## Begin ControlScript Import --------------------------------------------------
from extronlib.system import Wait
from extronlib.ui import Label

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
import inspect
import re
import functools
import traceback
import html

## End Python Imports ----------------------------------------------------------
##
## Begin Project Import -----------------------------------------------------------
from modules.helper.ModuleSupport import ProgramLogLogger, TraceLogger

import Variables

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
        if not isinstance(sortItem, str):
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
        
    @classmethod
    def MatrixLabelSort(cls, sortItem: Tuple[int, str]) -> int:
        return sortItem[0]

    @classmethod
    def SourceSort(cls, sortItem: Dict):
        dictMap = {
            "PC": 1,
            "UI": 2,
            "WPD": 3,
            "CAM": 4,
            "DC": 5,
            "DVD": 6
        }
        
        rtnVal = 9999
        for key, value in dictMap.items():
            if sortItem['srcId'].startswith(key):
                rtnVal = int('{}{}'.format(value, sortItem['srcId'][-3:]))
        
        return rtnVal
        
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def FullName(o) -> str:
    klass = o.__class__
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__ # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__

def MergeLists(*Lists) -> List:
    rtnList = []
    for mergeList in Lists:  # noqa: E741
        if isinstance(mergeList, tuple):
            mergeList = list(mergeList)
        rtnList.extend(mergeList)
    return rtnList


class LoadingLabel(Label):
    def __init__(self, Host: 'Constants.UI_HOSTS', ID: Union[int, str], Text: str="") -> None:
        super().__init__(Host, ID)
        self.__Text = Text
        
    def SetText(self, text: str) -> None:
        self.__Text = text
        super().SetText(text)
        
    @property
    def Text(self) -> str:
        return self.__Text
    
    @Text.setter
    def Text(self, text: str) -> None:
        self.__Text = text
        super().SetText(text)
    
class Logger():
    __Prog = ProgramLogLogger()
    __Trace = TraceLogger()
    
    __LoadingData = None
    
    @classmethod
    def CreateLoadingLabels(cls, Host):
        cls.__LoadingData = [LoadingLabel(Host=Host, ID=idNum) for idNum in range(100, 112)]

    @classmethod
    def AppendLoadingMsg(cls, msg):
        if cls.__LoadingData is not None:
            for i in range(11, -1, -1):
                if i > 0:
                    txt = cls.__LoadingData[i-1].Text
                else:
                    txt = html.escape(msg)
                cls.__LoadingData[i].SetText(txt)

    @classmethod
    def Log(cls, *recordobjs, separator=' ', logSeverity='info', callTrace=False) -> None:
        if Variables.TRACING or callTrace:
            current_frame = inspect.currentframe()
            current_frame_info = inspect.getframeinfo(current_frame)
            frame_stack = inspect.getouterframes(current_frame, 2)
            
            index = None
            for frame in frame_stack:
                if frame.filename == current_frame_info.filename:
                    index = frame_stack.index(frame) + 1
                    break
            
            caller_frame_info = frame_stack[index]
            
            regex = r"^(?:\/var\/nortxe\/proj\/eup\/|\/var\/nortxe\/uf\/admin\/modules\/|\/usr\/lib\/python3.5\/)?(.+)\.py$"
            
            re_match = re.match(regex, caller_frame_info.filename)
            fileName = re_match.group(1)
            mod = fileName.replace('/', '.')
            
            trace_msg = '\n    {module} [{func} ({line})]'.format(
                module = mod,
                func   = caller_frame_info.function,
                line   = caller_frame_info.lineno
            )
            
            cls.__Prog.Log(*recordobjs, trace_msg, sep=separator, severity=logSeverity)
        else:
            cls.__Prog.Log(*recordobjs, sep=separator, severity=logSeverity)
            
        if Variables.Loading:
            msg = separator.join(str(obj) for obj in recordobjs)
            cls.AppendLoadingMsg(msg)
    
    @classmethod
    def Trace(cls, *recordobjs, separator=' ', logSeverity='info') -> None:
        cls.__Trace.Log(*recordobjs, sep=separator, severity=logSeverity)
        
    @classmethod
    def Debug(cls, *recordobjs, separator=' ', logSeverity='info', callTrace=False) -> None:
        if Variables.TESTING:
            cls.Log(*recordobjs, separator=separator, logSeverity=logSeverity, callTrace=callTrace)

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
                if re_match is not None:
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
            if re_match is not None and re_match.group(1) is not None:
                find_dict[re_match.group(1)] = value
        return find_dict
    else:
        raise ValueError('regex must be true if capture_dict is true')

def SchedulePatternToString(Pattern: Dict) -> str:
    DoW = ''
    Pattern['days'].sort(key = SortKeys.SortDaysOfWeek)
    if len(Pattern['days']) == 0:
        return 'None'
    for d in Pattern['days']:
        if len(DoW) > 0:
            DoW = DoW + ','
        if d[0] == 'S' or d[0] == 'T':
            DoW = DoW + d[0:2]
        else:
            DoW = DoW + d[0]
        
    text = '{dow} {h}:{m} {a}'.format(dow = DoW, 
                                        h = str(Pattern['time']['hr']).zfill(2),
                                        m = str(Pattern['time']['min']).zfill(2),
                                        a = str(Pattern['time']['ampm']).upper())
    
    return text

def debug(func): # pragma: no cover
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = ["{}={!r}".format(k, v) for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        callStr = "Calling {}({})".format(func.__name__, signature)
        Logger.__Trace.Log(callStr)
        try:
            value = func(*args, **kwargs)
            rtnStr = "{!r} returned {!r}".format(func.__name__, value)
            Logger.Debug(callStr, rtnStr, separator='\n')
            return value
        except Exception as inst:
            tb = traceback.format_exc()
            Logger.Debug('An error occured attempting to call function. {} ({})\n    Exception ({}):\n        {}\n    Traceback:\n        {}'.format(func.__name__, signature, type(inst), inst, tb), logSeverity='error')
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

def isinstanceEx(Object: Any, Type: Union[str, type, Tuple[Union[str, type]]]) -> bool:
    if isinstance(Type, str):
        return (type(Object).__name__ == Type)
    elif isinstance(Type, type):
        return isinstance(Object, Type)
    elif isinstance(Type, tuple):
        rtnBool = False
        for t in Type:
            if isinstance(t, str) and type(Object).__name__ == t:
                rtnBool = True
            elif isinstance(t, type) and isinstance(Object, t):
                rtnBool = True
        return rtnBool

## End Function Definitions ----------------------------------------------------
