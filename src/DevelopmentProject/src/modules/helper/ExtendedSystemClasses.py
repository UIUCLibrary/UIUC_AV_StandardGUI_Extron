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
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING: # pragma: no cover
    pass

#### Python imports

#### Extron Library Imports
from extronlib.system import Timer

#### Project imports

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ExTimer(Timer):
    def __init__(self, 
                 Interval: float, 
                 Function: Callable = None,
                 Duration: float = None,
                 DurationFunction: Callable = None) -> None:
        self.__IntervalFunction = Function
        super().__init__(Interval, self.__ExFunction)
        self.__Duration = None
        if Duration is not None:
            self.ChangeDuration(Duration)
        self.DurationFunction = DurationFunction
    
    @property
    def Duration(self) -> float:
        return self.__Duration
    
    @Duration.setter
    def Duration(self, val) -> None:
        raise AttributeError('Setting Duration is disallowed. Use ChangeDuration instead.')
    
    @property
    def Function(self) -> Callable:
        return self.__IntervalFunction
    
    @Function.setter
    def Function(self, val) -> None:
        raise AttributeError('Setting Function is disallowed.')
    
    def __ExFunction(self, Timer: Timer, Count: int) -> None:
        if callable(self.__IntervalFunction):
            self.__IntervalFunction(Timer, Count)
        
        elapsed = self.Interval * Count
        if self.__Duration is not None and elapsed >= self.__Duration:
            self.Stop()
            if callable(self.DurationFunction):
                self.DurationFunction(Timer, Count)
            
    def ChangeDuration(self, Duration: float) -> None:
        if Duration is None:
            self.__Duration = None
        if type(Duration) in [int, float]:
            if Duration <= self.Interval:
                raise ValueError('Duration must be greater than Interval')
            self.__Duration = Duration
        else:
            raise TypeError('Duration must be an int, float, or None') 
        
    def Wrapup(self) -> None:
        if callable(self.DurationFunction):
            self.DurationFunction(self, self.Count)
        return super().Stop()
        

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
