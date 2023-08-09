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

from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button, Knob, Label, Level, Slider

## Begin ControlScript Import --------------------------------------------------
from extronlib import event

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
import re

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug


#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------
class HeaderController: 
    def __init__(self,
                 UIHost: 'ExUIDevice') -> None:
        
        # Public Properties
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost

        # Private Properties
        self.__CloseBtn = self.UIHost.Btns['Popover-Close']
        
        self.__HideWhenOff = ['Camera']
        self.__HideAlways = ['Alert']
        
        self.UIHost.Btns['Header-Alert'].PopoverName = 'Popover-Ctl-Alert'
        self.UIHost.Btns['Header-Camera'].PopoverName = 'Popover-Ctl-Camera_{}'.format(len(self.GUIHost.Cameras))
        self.UIHost.Btns['Header-Lights'].PopoverName = 'Popover-Ctl-Lights_{}'.format(len(self.GUIHost.Lights))
        self.UIHost.Btns['Header-Settings'].PopoverName = 'Popover-Ctl-Audio_{}'.format(len(self.GUIHost.Microphones))
        self.UIHost.Btns['Header-Help'].PopoverName = 'Popover-Ctl-Help'
        self.UIHost.Btns['Room-Label'].PopoverName = 'Popover-Room'
        
        self.__HeaderBtns = [
            self.UIHost.Btns['Header-Alert'],
            self.UIHost.Btns['Header-Camera'],
            self.UIHost.Btns['Header-Lights'],
            self.UIHost.Btns['Header-Settings'],
            self.UIHost.Btns['Header-Help'],
            self.UIHost.Btns['Room-Label'],
        ]
        
        self.__AllPopovers = []
        for btn in self.__HeaderBtns:
            btn.Hide = None
            re_match = re.match(r'Popover-Ctl-([A-Za-z]*)(?:_\d+)?', btn.PopoverName)
            if re_match is not None and re_match.group(1) is not None:
                if re_match.group(1) in self.__HideWhenOff:
                    btn.Hide = 'off'
                if re_match.group(1) in self.__HideAlways:
                    btn.Hide = 'always'
            self.__AllPopovers.append(btn.PopoverName)
        
        for btn in self.__HeaderBtns:
            if btn.Hide is not None:
                btn.SetEnable(False)
                btn.SetVisible(False)
                
            # we don't have anything to do with the room name at this point,
            # so we are going to disable it for now
            # this can be removed if used in the future
            if btn.Name == 'Room-Label':
                btn.SetEnable(False)
        
        @event(self.__HeaderBtns, ['Pressed', 'Tapped','Released']) # pragma: no cover
        def HeaderBtnHandler(button: 'Button', action: str):
            self.__HeaderButtonHandler(button, action)
        
        @event(self.__CloseBtn, 'Pressed') # pragma: no cover
        def PopoverCloseHandler(button: 'Button', action: str):
            self.__PopoverCloseHandler(button, action)
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __HeaderButtonHandler(self, button: 'Button',  action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif (action == 'Released' and button.holdTime is None) or action == 'Tapped':
            button.SetState(0)
            self.UIHost.ShowPopup(button.PopoverName)
    
    def __PopoverCloseHandler(self, button: 'Button', action: str):
        self.ClosePopovers()
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def ConfigSystemOn(self) -> None:
        for btn in self.__HeaderBtns:
            if btn.Hide == 'off':
                btn.SetEnable(True)
                btn.SetVisible(True)
    
    def ConfigSystemOff(self) -> None:
        for btn in self.__HeaderBtns:
            if btn.Hide == 'off':
                btn.SetEnable(False)
                btn.SetVisible(False)
                
    def ClosePopovers(self) -> None:
        for po in self.__AllPopovers:
            self.UIHost.HidePopup(po)
        
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
