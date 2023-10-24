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
from modules.helper.CommonUtilities import Logger
from modules.helper.ModuleSupport import eventEx
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

class DictObj:
    def __init__(self, src_dict: dict):
        if type(src_dict) is not dict:
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

class ControlMixIn():
    def __init__(self) -> None:
        self.__Control = None
        
    @property
    def Control(self) -> 'ControlObject':
        return self.__Control
    
    @Control.setter
    def Control(self, val) -> None:
        raise AttributeError('Overriding Control property directly is disallowed. Use "SetControlObject" instead.')
    
    def SetControlObject(self, Control: 'ControlObject'):
        if type(Control) is ControlObject:
            self.__Control = Control
        else:
            raise TypeError('Control must be a ControlObject')
        
        Logger.Log('RadioSet ControlObject:', Control)
        
class EventMixIn():
    def __init__(self) -> None:
        if type(self).__name__ == "ExButton":
            @eventEx(self, ['Pressed', 'Released', 'Held', 'Repeated', 'Tapped'])
            def ExButtonHandler(source, event) -> None:
                self.__ExButtonHandler(source, event)
        elif type(self).__name__ == "ExSlider":
            Logger.Log('Slider event def goes here')
                
    def __ExButtonHandler(self, source: 'ExButton', event: str) -> None:
        Logger.Log('ExButton Event', source, event)
        if event is 'Pressed':
            # Capture initial press state
            source.SetInitialPressState()
            
            # Change state to Shift state
            if source.GetControlShift('Press'):
                source.SetState(source.GetControlState('Shift'))
            
        elif event is 'Released':
            # Released no Hold
            if not source.HasHold():
                # Do primary functionality
                for fn in source.GetControlFunctionList('Primary'):
                    fn(source, event)
                
                # Determine after release state
                ## Control is latching (active after release)
                if source.GetControlLatching('Latching'):
                    # Change state to Active state
                    if source.Group is not None:
                        if hasattr(source.Group, 'SetCurrent'):
                            source.Group.SetCurrent(source)
                        elif hasattr(source.Group, 'SetCurrentButton'):
                            source.Group.SetCurrentButton(source)
                        elif hasattr(source.Group, 'SetActive'):
                            source.Group.SetActive(source)
                    source.SetState(source.GetControlState('Active'))
                ## Control is non-latching (inactive after release)
                else:
                    # Change state to Inactive state
                    source.SetState(source.GetControlState('Inactive'))
                    
            # Relased after hold
            else:
                # Do Hold functionality
                for fn in source.GetControlFunctionList('Hold'):
                    fn(source, event)
                
                # Determine after release state
                ## Control is hold latching (HoldActive after release)
                if source.GetControlLatching('HoldLatching'):
                    # Change to HoldActive state
                    source.SetState(source.GetControlState('HoldActive'))
                else:
                    # Return to initial press state
                    source.SetState(source.GetInitialPressState())
                    
            # Clear initial press state
            source.ClearInitialPressState()
            
        elif event is 'Held':
            source.UIHost.Click()
            # Determine if state change is needed
            source.SetState(source.GetControlState('HoldShift'))
                
        elif event is 'Repeated':
            # Do Repeat functionality
            for fn in source.GetControlFunctionList('Repeat'):
                fn(source, event)
            
        elif event is 'Tapped':
            source.Control.Functions.Primary(source, event)
            
            # Do primary functionality
            for fn in source.GetControlFunctionList('Primary'):
                fn(source, event)
            
            # Determine after release state
            ## Control is latching (active after release)
            if source.GetControlLatching('Latching'):
                # Change state to Active state
                if source.Group is not None:
                    if hasattr(source.Group, 'SetCurrent'):
                        source.Group.SetCurrent(source)
                    elif hasattr(source.Group, 'SetCurrentButton'):
                        source.Group.SetCurrentButton(source)
                    elif hasattr(source.Group, 'SetActive'):
                        source.Group.SetActive(source)
                source.SetState(source.GetControlState('Active'))
            ## Control is non-latching (inactive after release)
            else:
                # Change state to Inactive state
                source.SetState(source.GetControlState('Inactive'))
            
            # Clear initial press state
            source.ClearInitialPressState()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
