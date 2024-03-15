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


## Begin Imports ---------------------------------------------------------------

#### Type Checking
from _collections_abc import Iterable
from typing import TYPE_CHECKING, Union, Callable, Any, Dict, List
if TYPE_CHECKING: # pragma: no cover
    from modules.project.Collections import AlertCollection

#### Python imports
from collections import UserDict, UserList
import json
from enum import Enum
from collections import namedtuple

#### Extron Library Imports
from extronlib.system import RFile

#### Project imports
from modules.helper.ModuleSupport import WatchVariable, eventEx
from modules.project.MixIns import InitializeMixin
from modules.helper.CommonUtilities import Logger, MergeLists


## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ActivityMode(Enum):
    Standby = 0
    Share = 1
    AdvShare = 2
    GroupWork = 3

class SystemState(Enum):
    Standby = 0
    Active = 1
    
class TieType(Enum):
    Untie = 0
    Audio = 1
    Video = 2
    AudioVideo = 3

MatrixTie    = namedtuple('MatrixTie',    ['video', 'audio'])
MatrixAction = namedtuple('MatrixAction', ['output', 'input', 'type'])

Layout = namedtuple('Layout', ['row', 'col'])

class classproperty(property):
    """
    Property decorator for class-level properties.
    Subclasses 'property'. 
    """    
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

class Alias(object):
    def __init__(self, source_name):
        self.source_name = source_name

    def __get__(self, obj, objtype=None):
        if obj is None:
            # Class lookup, return descriptor
            return self
        return getattr(obj, self.source_name)

    def __set__(self, obj, value):
        setattr(obj, self.source_name, value)

class DictObj(object):
    def __init__(self, src_dict: dict, recurse: bool=True):
        if not isinstance(src_dict, dict):
            raise TypeError('DictObj src_dict must be of type dict')
        
        for key, val in src_dict.items():
            if recurse:
                if isinstance(val, (list, tuple)):
                    setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
                else:
                    setattr(self, key, DictObj(val) if isinstance(val, dict) else val)
            else:
                setattr(self, key, val)
               
    def __repr__(self) -> str:
        return str(self.__dict__)

class FeedbackObject(object):
    def __init__(self) -> None:
        pass
    
    
class WatchMixIn(object):
    def __init__(self, watchType: type) -> None:
        if watchType is list:
            watchStr = "List Changed"
        elif watchType is dict:
            watchStr = "Dictionary Changed"

        self.Watch = WatchVariable(watchStr)

    def __GetKey(self, key: str, eventKey: Union[str, list]) -> list:
        if key is None:
            if isinstance(eventKey, list):
                watchKey = eventKey
            else:
                watchKey = [eventKey]
        else:
            if isinstance(eventKey, list):
                watchKey = [key]
                watchKey.extend(eventKey)
            else:
                watchKey = [key, eventKey]

        return watchKey

    def CreateWatchList(self, value: List, key: str=None) -> 'WatchList':
        rtnList = WatchList(*value)
        @eventEx(rtnList.Watch, 'Changed')
        def WatchListHandler(source, event, evKey=None, evValue=None):
            watchKey = self.__GetKey(key, evKey)

            self.Watch.Change(event, watchKey, evValue)

        return rtnList

    def CreateWatchDict(self, value: Dict, key: str=None) -> 'WatchDict':
        rtnDict = WatchDict(**value)
        @eventEx(rtnDict.Watch, 'Changed')
        def WatchListHandler(source, event, evKey=None, evValue=None):
            watchKey = self.__GetKey(key, evKey)

            self.Watch.Change(event, watchKey, evValue)

        return rtnDict
    
    
class WatchDict(WatchMixIn, UserDict):
    def __init__(self, mapping: dict=None, **kwargs):
        WatchMixIn.__init__(self, dict)
        
        if mapping is not None:
            mapping = {
                key: value for key, value in mapping.items()
            }
        else:
            mapping = {}
            
        if kwargs:
            mapping.update(
                {key: value for key, value in kwargs.items()}
            )
        
        for key, value in mapping.items():
            if isinstance(value, list):
                mapping[key] = self.CreateWatchList(value, key)
            elif isinstance(value, dict):
                mapping[key] = self.CreateWatchDict(value, key)
        
        UserDict.__init__(self, **mapping)
    
    def __setitem__(self, key: Any, item: Any) -> None:
        if isinstance(item, list):
            newItem = self.CreateWatchList(item, key)
        elif isinstance(item, dict):
            newItem = self.CreateWatchDict(item, key)
        else:
            newItem = item
            
        UserDict.__setitem__(self, key, newItem)
        self.Watch.Change('Updated', key, item)
        
    def __delitem__(self, key: Any) -> None:
        delVal = self.data[key]
        UserDict.__delitem__(self, key)
        self.Watch.Change('Deleted', key, delVal)
        
    def serialize(self) -> None:
        serialDict = self.data.copy()
        
        for key, item in serialDict.items():
            if isinstance(item, WatchDict):
                serialDict[key] = item.serialize()
            elif isinstance(item, WatchList):
                serialDict[key] = item.serialize()
                
        return serialDict
        
class WatchList(WatchMixIn, UserList):
    def __init__(self, *args):
        WatchMixIn.__init__(self, list)
        
        for item in args:
            index = args.index(item)
            if isinstance(item, list):
                args[index] = self.CreateWatchList(item, index)
            elif isinstance(item, dict):
                args[index] = self.CreateWatchDict(item, index)
        
        UserList.__init__(self, args)
        
    def __setitem__(self, i: Union[int, slice], item: Any) -> None: # Use SupportsIndex instead of int if moving to Python > 3.8
        if isinstance(item, list):
            newItem = self.CreateWatchList(item, i)
        elif isinstance(item, dict):
            newItem = self.CreateWatchDict(item, i)
        else:
            newItem = item
        
        UserList.__setitem__(self, i, newItem)
        self.Watch.Change('Updated', i, newItem)
        
    def __delitem__(self, i: Union[int, slice]) -> None: # Use SupportsIndex instead of int if moving to Python > 3.8
        delVal = self.data[i]
        UserList.__delitem__(self, i)
        self.Watch.Change('Deleted', i, delVal)
        
    def pop(self, i: int = -1) -> Any:
        UserList.pop(self, i)
        self.Watch.Change('Deleted', i, self.data[i])
    
    def remove(self, item: Any) -> None:
        index = self.data.index(item)
        UserList.remove(self, item)
        self.Watch.Change('Deleted', index, item)
    
    def append(self, item: Any) -> None:
        UserList.append(self, item)
        
        index = self.data.index(item)
        if isinstance(item, list):
            self.data[index] = self.CreateWatchList(item, index)
        elif isinstance(item, dict):
            self.data[index] = self.CreateWatchDict(item, index)
        
        self.Watch.Change('Updated', index, item)
    
    def extend(self, other: Iterable) -> None:
        UserList.extend(self, other)
        
        for item in other:
            index = self.data.index(item)
            if isinstance(item, list):
                self.data[index] = self.CreateWatchList(item, index)
            elif isinstance(item, dict):
                self.data[index] = self.CreateWatchDict(item, index)
            
            self.Watch.Change('Updated', index, item)
    
    def insert(self, i: int, item: Any) -> None:
        if isinstance(item, list):
            newItem = self.CreateWatchList(item, i)
        elif isinstance(item, dict):
            newItem = self.CreateWatchDict(item, i)
        else:
            newItem = item
        
        UserList.insert(i, newItem)
        self.Watch.Change('Updated', i, item)
        
    def serialize(self) -> None:
        serialList = self.data.copy()
        
        for item in serialList:
            index = serialList.index(item)
            if isinstance(item, WatchDict):
                serialList[index] = item.serialize()
            elif isinstance(item, WatchList):
                serialList[index] = item.serialize()
                
        return serialList
        
class SettingsObject():
    def __init__(self, SettingsFile: str) -> None:
        self.FileName = SettingsFile
        self.__JSON = None
        self.__LoadFromFile()
        
        self.__LoadSettings()
        
        @eventEx(self.Settings.Watch, 'Changed')
        def WatchHandler(source, event, key=None, value=None):
            Logger.Debug('Settings Object Changed -', source, event, key, value)
            self.__WriteToFile()

    def __LoadSettings(self) -> None:
        jsonObj = json.loads(self.__JSON)
        if isinstance(jsonObj, list):
            self.Settings = WatchList(*jsonObj)
        elif isinstance(jsonObj, dict):
            self.Settings = WatchDict(**jsonObj)
        else:
            raise ValueError('JSON object ({} - {}) must have a top level list or dict'.format(jsonObj, type(jsonObj)))
    
    def __LoadFromFile(self) -> None:
        file = RFile(self.FileName, 'r')
        self.__JSON = file.read()
        file.close()
    
    def __WriteToFile(self) -> None:
        file = RFile(self.FileName, 'w')
        self.__JSON = json.dumps(self.Settings.serialize(), indent=4)
        file.write(self.__JSON)
        file.close()
       
class Alert(InitializeMixin, object):
    __eqList  = ['eq', 'equal', 'equals', 'equal to', '=', '==']
    __neqList = ['neq', '!eq', 'not equal', 'not equals', 'unequal to', '!=', '!==']
    __gtList  = ['gt', 'greater', 'greater than', '>']
    __gteList = ['gte', 'greater or equal', 'greater than or equal to', '>=']
    __ltList  = ['lt', 'less', 'less than', '<']
    __lteList = ['lte', 'less or equal', 'less than or equal to', '<=']
    __inList  = ['in', 'in list', 'in object']
    __ninList = ['not in', '!in', 'not in list', 'not in object']
    __isList  = ['is']
    __isnList = ['is not', '!is']
    __operatorList = MergeLists(__eqList, __neqList, __gteList, __gteList, 
                                __ltList, __lteList, __inList, __ninList, 
                                __isList, __isnList)
    
    def __init__(self, 
                 AlertCollection: 'AlertCollection',
                 Name: str, 
                 AlertDeviceId: str,
                 AlertLevel: Union[str, Callable],
                 AlertText: Union[str, Callable],
                 TestDeviceId: str, 
                 TestCommand: str, 
                 TestOperator: Union[str, Callable],
                 TestOperand: Any,
                 TestQualifier: dict = None) -> None:
        InitializeMixin.__init__(self, self.__Initialize)
        
        self.Name = Name
        self.AlertCollection = AlertCollection
        
        if not (callable(TestOperator) or TestOperator in self.__operatorList):
            raise ValueError('TestOperator must be a valid comparison string or callable'
                             )
        self.__Test = DictObj({
            'DeviceId': TestDeviceId,
            'DeviceInterface': None,
            'Command': TestCommand,
            'Qualifier': TestQualifier,
            'Operator': TestOperator,
            'Operand': TestOperand,
        }, recurse=False)
        self.__LastResult = None
        
        self.DeviceId = AlertDeviceId
        
        if callable(AlertLevel) or isinstance(AlertLevel, str):
            self.__Level = AlertLevel
        else:
            raise ValueError('AlertLevel must either be a str or callable')
        
        if callable(AlertText) or isinstance(AlertText, str):
            self.__Text = AlertText
        else:
            raise ValueError('AlertText must either be a str or callable')
        
        self.Changed = WatchVariable('Alert Value ({}) Changed'.format(self.Name))
        
    @property
    def Active(self) -> bool:
        # callable
        if callable(self.__Test.Operator):
            return bool(self.__Test.Operator(self.__LastResult, self.__Test.Operand))
        # ==
        elif self.__Test.Operator in self.__eqList:
            return (self.__LastResult == self.__Test.Operand)
        # !=
        elif self.__Test.Operator in self.__neqList:
            return (self.__LastResult != self.__Test.Operand)
        # >
        elif self.__Test.Operator in self.__gtList:
            return (self.__LastResult > self.__Test.Operand)
        # >=
        elif self.__Test.Operator in self.__gteList:
            return (self.__LastResult >= self.__Test.Operand)
        # <
        elif self.__Test.Operator in self.__ltList:
            return (self.__LastResult < self.__Test.Operand)
        # <=
        elif self.__Test.Operator in self.__lteList:
            return (self.__LastResult <= self.__Test.Operand)
        # in
        elif self.__Test.Operator in self.__inList:
            return (self.__LastResult in self.__Test.Operand)
        # not in
        elif self.__Test.Operator in self.__ninList:
            return (self.__LastResult not in self.__Test.Operand)
        # is
        elif self.__Test.Operator in self.__isList:
            return (self.__LastResult is self.__Test.Operand)
        # is not
        elif self.__Test.Operator in self.__isnList:
            return (self.__LastResult is not self.__Test.Operand)
    
    @Active.setter
    def Active(self, val) -> None:
        raise AttributeError('Setting Alert.Active is disallowed.')
    
    @property
    def Level(self) -> str:
        if callable(self.__Level):
            return self.__Level(self, self.__LastResult)
        else:
            return self.__Level
        
    @Level.setter
    def Level(self, val) -> None:
        raise AttributeError('Setting Alert.Level is disallowed.')
    
    @property
    def Text(self) -> str:
        if callable(self.__Text):
            return self.__Text(self, self.__LastResult)
        else:
            return self.__Text
    
    def __repr__(self) -> str:
        act = 'X' if self.Active else '_'
        return '<Alert {} [{}]>'.format(self.Name, act)
     
    def __Initialize(self) -> None:
        # get interface for test device
        self.__Test.DeviceInterface = self.AlertCollection.SystemHost.Devices[self.__Test.DeviceId].interface
    
    def Check(self) -> bool:
        prev = self.__LastResult
        self.__LastResult = self.__Test.DeviceInterface.ReadStatus(self.__Test.Command, self.__Test.Qualifier)

        if prev != self.__LastResult:
            self.Changed.Change(self.Active, self.Level, self.Text)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
