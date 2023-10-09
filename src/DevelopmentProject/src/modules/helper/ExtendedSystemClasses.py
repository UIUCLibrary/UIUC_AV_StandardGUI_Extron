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
    pass

#### Python imports

#### Extron Library Imports
from extronlib.system import Timer

#### Project imports
from modules.helper.CommonUtilities import Logger

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
        self.Duration = Duration
        self.DurationFunction = DurationFunction
        
    def __ExFunction(self, Timer: Timer, Count: int) -> None:
        self.__IntervalFunction(Timer, Count)
        
        dur = self.Interval * Count
        if dur >= self.Duration:
            self.Stop()
            self.DurationFunction(Timer, Count)
        

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
