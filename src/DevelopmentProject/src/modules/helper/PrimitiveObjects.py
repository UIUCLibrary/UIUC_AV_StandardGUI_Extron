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
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
from types import ModuleType
if TYPE_CHECKING: # pragma: no cover
    from modules.helper.Collections import RadioSet, SelectSet, VariableRadioSet, ScrollingRadioSet
    from modules.helper.ExtendedUIClasses import ExButton, ExSlider, RefButton

#### Python imports
import importlib
import importlib.util

#### Extron Library Imports

#### Project imports
from modules.helper.Collections import DictObj
import control.AV

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
        if type(FuncModule) is ModuleType:
            self.__FuncModule = FuncModule
        elif type(FuncModule) is str:
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
                if IconId is not None and type(IconId) is int:
                    holdDict['HoldActive'] = int('{}{}'.format(IconId, HoldActiveState))
                else:
                    holdDict['HoldActive'] = HoldActiveState
            if HoldShiftState is not None:
                if IconId is not None and type(IconId) is int:
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
        
        if IconId is not None and type(IconId) is int:
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
    
    @property
    def LinkedObject(self) -> Union['ExButton', 'ExSlider', 'RefButton']:
        return self.__LinkedObject
    
    @LinkedObject.setter
    def LinkedObject(self, val) -> None:
        raise AttributeError('Overriding LinkedObject property directly is disallowed. Use "LinkControlObject" instead.')
    
    @property
    def LinkedCollection(self) -> Union['RadioSet', 'SelectSet', 'VariableRadioSet', 'ScrollingRadioSet']:
        return self.__LinkedCollection
    
    @LinkedCollection.setter
    def LinkedCollection(self, val) -> None:
        raise AttributeError('Overriding LinkedCollection property directly is disallowed. Use "LinkControlObject" instead.')
    
    def LinkControlObject(self, ControlObject: Union['ExButton', 'ExSlider', 'RefButton'] = None, ControlCollection: Union['RadioSet', 'SelectSet', 'VariableRadioSet', 'ScrollingRadioSet'] = None):
        if ControlObject is not None:
            # if type(ControlObject) not in [ExButton, ExSlider, RefButton]:
            #     raise TypeError('Invalid ControlObject type ({}) provided'.format(type(ControlObject)))
            
            self.__LinkedObject = ControlObject
            self.__LinkedObject.SetControlObject(self)
        if ControlCollection is not None:
            # if type(ControlCollection) not in [RadioSet, SelectSet, VariableRadioSet, ScrollingRadioSet]:
            #     raise TypeError('Invalid ControlCollection type ({}) provided'.format(type(ControlCollection)))
            
            self.__LinkedCollection = ControlCollection
                    
            if self.__LinkedCollection is not None:
                self.__LinkedCollection.SetStates(self.__LinkedObject, self.States.Inactive, self.States.Active)
                
            self.__LinkedCollection.SetControlObject(self)

    def __DefaultCallable(self, button, action) -> None:
        pass

class FeedbackObject():
    def __init__(self) -> None:
        pass

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
