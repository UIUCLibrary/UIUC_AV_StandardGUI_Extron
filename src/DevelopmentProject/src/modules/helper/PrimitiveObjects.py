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
from typing import TYPE_CHECKING, Union, Callable, Any, List, Dict
from types import ModuleType
# from typing_extensions import SupportsIndex
if TYPE_CHECKING: # pragma: no cover
    pass

#### Python imports
import importlib
import importlib.util
from collections import UserDict, UserList
import json

#### Extron Library Imports
from extronlib.system import RFile

#### Project imports
import control.AV
from modules.helper.ModuleSupport import WatchVariable, eventEx
from modules.helper.CommonUtilities import Logger, isinstanceEx
import Constants

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class classproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

class Alias:
    def __init__(self, source_name):
        self.source_name = source_name

    def __get__(self, obj, objtype=None):
        if obj is None:
            # Class lookup, return descriptor
            return self
        return getattr(obj, self.source_name)

    def __set__(self, obj, value):
        setattr(obj, self.source_name, value)

class DictObj:
    def __init__(self, src_dict: dict):
        if not isinstance(src_dict, dict):
            raise TypeError('DictObj src_dict must be of type dict')
        
        for key, val in src_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)
               
    def __repr__(self) -> str:
        return str(self.__dict__)

class ControlObject():
    __DefaultModule = control.AV
    def __init__(self, 
                 PrimaryFunc: Union[str, Callable] = None, 
                 HoldFunc: Union[str, Callable] = None,
                 RepeatFunc: Union[str, Callable] = None,
                 PressShift: bool=True, 
                 Latching: bool=False,
                 HoldLatching: bool=False,
                 ShiftState: int = 1, 
                 ActiveState: int = 1,
                 InactiveState: int = 0,
                 HoldActiveState: int = None,
                 HoldShiftState: int = None,
                 IconId: int = None,
                 FuncModule: Union[str, 'ModuleType'] = None) -> None:
        """_summary_

        Example Control Item
            {
                "ControlObject": "Button-Name", 
                "ControlCollection": "Group-Name",
                "PrimaryFunc": "String Function Name", # Must be a callable or a string function name in this object function module
                "HoldFunc": "String Function Name", # Must be a callable or a string function name in this object function module
                "RepeatFunc": "String Function Name", # Must be a callable or a string function name in this object function module
                "PressShift": true, # bool
                "ShiftState": 1, # int state Id
                "ActiveState": 1, # int state Id
                "InactiveState": 0, # int state Id
                "IconId": null, # [Optional] in icon Id, prepended to state
                "FuncModule": null, # module or string module name if the default will be overriden
            }
        
        Args:
            PrimaryFunc (Union[str, Callable]): _description_
            HoldFunc (Union[str, Callable], optional): _description_. Defaults to None.
            RepeatFunc (Union[str, Callable], optional): _description_. Defaults to None.
            PressShift (bool, optional): _description_. Defaults to True.
            ShiftState (int, optional): _description_. Defaults to 1.
            ActiveState (int, optional): _description_. Defaults to 1.
            InactiveState (int, optional): _description_. Defaults to 0.
            IconId (int, optional): _description_. Defaults to None.
            FuncModule (Union[str, &#39;ModuleType&#39;], optional): _description_. Defaults to None.

        Raises:
            TypeError: _description_
        """
        self.__LinkedObject = None
        self.__LinkedCollection = None
        
        self.__FuncModule = self.__DefaultModule
        if isinstance(FuncModule, ModuleType):
            self.__FuncModule = FuncModule
        elif isinstance(FuncModule, str):
            self.__FuncModule = importlib.import_module(FuncModule)
        
        funcDict = {}
        
        if PrimaryFunc is not None:
            funcDict['Primary'] = PrimaryFunc if callable(PrimaryFunc) else getattr(self.__FuncModule, PrimaryFunc)
        else:
            funcDict['Primary'] = self.__DefaultCallable
        
        holdDict = {}
        if HoldFunc is not None:
            funcDict['Hold'] = HoldFunc if callable(HoldFunc) else getattr(self.__FuncModule, HoldFunc)
            if HoldActiveState is not None:
                if IconId is not None and isinstance(IconId, int):
                    holdDict['HoldActive'] = int('{}{}'.format(IconId, HoldActiveState))
                else:
                    holdDict['HoldActive'] = HoldActiveState
            if HoldShiftState is not None:
                if IconId is not None and isinstance(IconId, int):
                    holdDict['HoldShift'] = int('{}{}'.format(IconId, HoldShiftState))
                else:
                    holdDict['HoldShift'] = HoldShiftState
        else:
            funcDict['Hold'] = self.__DefaultCallable
            
        if RepeatFunc is not None:
            funcDict['Repeat'] = RepeatFunc if callable(RepeatFunc) else getattr(self.__FuncModule, RepeatFunc)
        else:
            funcDict['Repeat'] = self.__DefaultCallable
        
        self.Functions = DictObj(funcDict)
        
        self.PressStateShift = PressShift
        self.Latching = Latching
        self.HoldLatching = HoldLatching
        
        if IconId is not None and isinstance(IconId, int):
            stateDict = {
                'Shift': int('{}{}'.format(IconId, ShiftState)),
                'Active': int('{}{}'.format(IconId, ActiveState)),
                'Inactive': int('{}{}'.format(IconId, InactiveState))
            }
            if holdDict != {}:
                stateDict.update(holdDict)
            self.States = DictObj(stateDict)
        elif IconId is None:
            stateDict = {
                'Shift': ShiftState,
                'Active': ActiveState,
                'Inactive': InactiveState
            }
            if holdDict != {}:
                stateDict.update(holdDict)
            self.States = DictObj(stateDict)
        else:
            raise TypeError('IconId must be an int or None')
    
    def __repr__(self) -> str:
        if self.LinkedCollection is not None and self.LinkedObject is not None:
            str_rep = '<Control Object {} | Collection: {} | Object: {}>'.format(hex(id(self)), self.LinkedCollection.Name, self.LinkedObject.Name)
        elif self.LinkedCollection is not None and self.LinkedObject is None:
            str_rep = '<Control Object {} | Collection: {}>'.format(hex(id(self)), self.LinkedCollection.Name)
        elif self.LinkedCollection is None and self.LinkedObject is not None:
            str_rep = '<Control Object {} | Object: {}>'.format(hex(id(self)), self.LinkedObject.Name)
        else:
            str_rep = '<Control Object {} | Unassigned>'.format(hex(id(self)))
        
        return str_rep
    
    @property
    def LinkedObject(self) -> Constants.UI_OBJECTS:
        return self.__LinkedObject
    
    @LinkedObject.setter
    def LinkedObject(self, val) -> None:
        raise AttributeError('Overriding LinkedObject property directly is disallowed. Use "LinkControlObject" instead.')
    
    @property
    def LinkedCollection(self) -> Constants.UI_SETS:
        return self.__LinkedCollection
    
    @LinkedCollection.setter
    def LinkedCollection(self, val) -> None:
        raise AttributeError('Overriding LinkedCollection property directly is disallowed. Use "LinkControlObject" instead.')
    
    def LinkControlObject(self, ControlObject: Constants.UI_OBJECTS = None, ControlCollection: Constants.UI_SETS = None):
        if ControlObject is not None:
            if not isinstanceEx(ControlObject, Constants.UI_OBJECTS_MATCH):
                raise TypeError('Invalid ControlObject type ({}) provided'.format(type(ControlObject)))
            
            self.__LinkedObject = ControlObject
            self.__LinkedObject.SetControlObject(self)
        if ControlCollection is not None:
            if not isinstanceEx(ControlCollection, Constants.UI_SETS_MATCH):
                raise TypeError('Invalid ControlCollection type ({}) provided'.format(type(ControlCollection)))
            
            self.__LinkedCollection = ControlCollection
                    
            # if self.__LinkedCollection is not None:
            #     self.__LinkedCollection.SetStates(self.__LinkedObject, self.States.Inactive, self.States.Active)
                
            self.__LinkedCollection.SetControlObject(self)

    def __DefaultCallable(self, button, action) -> None:
        pass

class FeedbackObject():
    def __init__(self) -> None:
        pass
    
    
class WatchMixIn():
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
        

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
