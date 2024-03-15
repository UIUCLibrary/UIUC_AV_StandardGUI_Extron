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
    from modules.project.extended.Device import ExUIDevice
    from modules.project.extended.UI import ButtonEx
    from modules.project.Collections.UISets import PINPadControlGroup

#### Python imports

#### Extron Library Imports

#### Project imports

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class PINController:
    def __init__(self,
                 UIHost: 'ExUIDevice',
                 ControlGroup: 'PINPadControlGroup') -> None:
        # Public Properties
        self.UIHost = UIHost
        self.PIN = None
        self.Callback = None
        
        # Private Properties
        self.__CurrentPIN = ""
        self.__ControlGroup = ControlGroup
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def UpdatePINHandler(self, value: int):
        self.__CurrentPIN = self.__CurrentPIN + str(value)
        self.__MaskPIN() #remask pin after change
        if (self.__CurrentPIN == self.PIN):
            self.UIHost.ShowPopup("PIN Outcome Success", 2)
            # clean up and go to destination page while success popup is up
            self.Close(success=True)
        elif (len(self.__CurrentPIN) >= 10):
            self.UIHost.ShowPopup("PIN Outcome Failure", 2)
            # clean up and go back to pin page while failure popup is up
            self.ResetPIN()
    
    def BackspacePINHandler(self):
        self.__CurrentPIN = self.__CurrentPIN[:-1] # remove last character of current pin
        self.__MaskPIN()  # remask pin after change
    
    def CancelBtnHandler(self):
        self.Close()
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __MaskPIN(self) -> None:
        """Generates and sets Masked PIN feedback"""    

        mask = ""
        while (len(mask) < len(self.__CurrentPIN)):
            mask = mask + "*"
        self.__ControlGroup.SetText(mask)
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def ResetPIN(self) -> None:
        """Resets the currently input PIN code"""
        self.__CurrentPIN = ''
        self.__MaskPIN()
    
    def Open(self, PIN: str, Callback: Callable=None) -> None:
        """Displays Pin Modal"""
        self.Callback = Callback
        
        # validate pin
        if isinstance(PIN, str):
            for character in PIN:
                if not character.isnumeric():
                    raise ValueError('All PIN Characters must be numeric')
            self.PIN = PIN
        else:
            raise TypeError('PIN must be a string of numeric characters')
        
        self.ResetPIN()
        self.UIHost.ShowPopup("PIN Code")
        
    def Close(self, success: bool=False) -> None:
        """Hides PIN Modal"""
        if success:
            self.Callback()
        
        self.Callback = None
        self.PIN = None
        
        self.ResetPIN()
        
        self.UIHost.HidePopup("PIN Code")

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def PINPadHandler(source: 'ButtonEx', event: str) -> None:
    PINCtl = source.UIHost.PINAccess
    PINCtl.UpdatePINHandler(source.pinValue)
            
def PINBackspaceHandler(source: 'ButtonEx', event: str) -> None:
    PINCtl = source.UIHost.PINAccess
    PINCtl.BackspacePINHandler()

def PINCancelHandler(source: 'ButtonEx', event: str) -> None:
    PINCtl = source.UIHost.PINAccess
    PINCtl.CancelBtnHandler()

## End Function Definitions ----------------------------------------------------



