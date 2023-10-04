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
if TYPE_CHECKING: # pragma: no cover
    from modules.project.Collections import RadioSet, SelectSet, VariableSelectSet, ScollingSelectSet
    from modules.project.ExtendedUIClasses import ExButton, ExSlider, SelectObject

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.project.Collections import DictObj

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
    def __init__(self, 
                 PrimaryFunc: Union[str, Callable], 
                 HoldFunc: Union[str, Callable] = None,
                 RepeatFunc: Union[str, Callable] = None,
                 PressShift: bool=True, 
                 ShiftState: int = 1, 
                 ActiveState: int = 1,
                 InactiveState: int = 0,
                 IconId: int = None) -> None:
        
        self.__LinkedObject = None
        self.__LinkedCollection = None
        self.Functions = DictObj({
            'Primary': PrimaryFunc,
            'Hold': HoldFunc,
            'Repeat': RepeatFunc
        })
        self.PressStateShift = PressShift
        
        if IconId is not None and type(IconId) is int:
            self.States = DictObj({
                'Shift': int('{}{}'.format(IconId, ShiftState)),
                'Active': int('{}{}'.format(IconId, ActiveState)),
                'Inactive': int('{}{}'.format(IconId, InactiveState))
            })
        elif IconId is None:
            self.States = DictObj({
                'Shift': ShiftState,
                'Active': ActiveState,
                'Inactive': InactiveState
            })
        else:
            raise TypeError('IconId must be an int or None')
    
    @property
    def LinkedObject(self) -> Union['ExButton', 'ExSlider', 'SelectObject']:
        return self.__LinkedObject
    
    @LinkedObject.setter
    def LinkedObject(self, val) -> None:
        raise ValueError('Overriding LinkedObject property directly is disallowed. Use "LinkControlObject" instead.')
    
    @property
    def LinkedCollection(self) -> Union['RadioSet', 'SelectSet', 'VariableSelectSet', 'ScollingSelectSet']:
        return self.__LinkedCollection
    
    @LinkedCollection.setter
    def LinkedCollection(self, val) -> None:
        raise ValueError('Overriding LinkedCollection property directly is disallowed. Use "LinkControlObject" instead.')
    
    def LinkControlObject(self, ControlObject: Union['ExButton', 'ExSlider', 'SelectObject'], ControlCollection: Union['RadioSet', 'SelectSet', 'VariableSelectSet', 'ScollingSelectSet'] = None):
        if type(ControlObject) not in [ExButton, ExSlider, SelectObject]:
            raise TypeError('Invalid ControlObject type ({}) provided'.format(type(ControlObject)))
        if ControlCollection is not None and type(ControlCollection) not in [RadioSet, SelectSet, VariableSelectSet, ScollingSelectSet]:
            raise TypeError('Invalid ControlCollection type ({}) provided'.format(type(ControlCollection)))
        
        self.__LinkedObject = ControlObject
        self.__LinkedObject.SetControlObject(self)
        self.__LinkedCollection = ControlCollection
        
        if type(self.Functions.Primary) is str:
            strFn = self.Functions.Primary
            potentialCallable = getattr(self.__LinkedObject, strFn)
            if callable(potentialCallable):
                self.Functions.Primary = potentialCallable
            else:
                potentialCallable = getattr(self.__LinkedCollection, strFn)
                if callable(potentialCallable):
                    self.Functions.Primary = potentialCallable
        
        if type(self.Functions.Hold) is str:
            strFn = self.Functions.Hold
            potentialCallable = getattr(self.__LinkedObject, strFn)
            if callable(potentialCallable):
                self.Functions.Hold = potentialCallable
            else:
                potentialCallable = getattr(self.__LinkedCollection, strFn)
                if callable(potentialCallable):
                    self.Functions.Hold = potentialCallable
                
        if type(self.Functions.Repeat) is str:
            strFn = self.Functions.Repeat
            potentialCallable = getattr(self.__LinkedObject, strFn)
            if callable(potentialCallable):
                self.Functions.Repeat = potentialCallable
            else:
                potentialCallable = getattr(self.__LinkedCollection, strFn)
                if callable(potentialCallable):
                    self.Functions.Repeat = potentialCallable
                
        if self.__LinkedCollection is not None:
            self.__LinkedCollection.SetStates(self.__LinkedObject, self.States.Inactive, self.States.Active)
            
        
class FeedbackObject():
    def __init__(self) -> None:
        pass

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
