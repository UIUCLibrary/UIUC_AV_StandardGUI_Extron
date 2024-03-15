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
from typing import TYPE_CHECKING, Tuple, Callable
if TYPE_CHECKING: # pragma: no cover
    from modules.project.ExtendedClasses.Device import ExUIDevice
    from modules.project.ExtendedClasses.UI import ButtonEx
    from modules.project.Collections.UISets import KeyboardControlGroup

#### Python imports

#### Extron Library Imports
from extronlib.system import Timer

#### Project imports

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class KeyboardController:
    def __init__(self, 
                 UIHost: 'ExUIDevice', 
                 ControlGroup: 'KeyboardControlGroup') -> None:
        # Public Properties
        self.UIHost = UIHost
        self.CapsLock = False
        self.Shift = False
        self.Text = ''
        self.Callback = None
        
        # Private Properties
        self.__ControlGroup = ControlGroup
        
        self.__Cursor = ('\u2502','\u2588')
        self.__Pos = 0
        self.__CursorTimer = Timer(0.5, self.__CursorTimerHandler)
        self.__CursorTimer.Stop()

    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def CharBtnHandler(self, char: Tuple[str, str]):
        # Tuple[lc_char, uc_char]
        self.__InsertChar(char[self.__CharIndex()])
        self.__ControlGroup.SetText(self.__CursorString())
        
        # unshift after character entry
        if self.Shift:
            self.Shift = False
            self.__ControlGroup.UIControls['Shift'].SetState(0)
            self.__UpdateKeyboardState()
    
    def SpaceBtnHandler(self):
        self.__InsertChar(' ')
        self.__ControlGroup.SetText(self.__CursorString())
    
    def ShiftBtnHandler(self):
        self.Shift = not self.Shift
        self.__UpdateKeyboardState()
    
    def CapsLockBtnHandler(self):
        self.CapsLock = not self.CapsLock
        self.__UpdateKeyboardState()
    
    def ArrowBtnHandler(self, shift: int):
        self.__Pos += shift
        if self.__Pos < 0:
            self.__Pos = 0
        elif self.__Pos > (len(self.Text)):
            self.__Pos = (len(self.Text))
        self.__ControlGroup.SetText(self.__CursorString())
    
    def RemoveCharBtnHandler(self, remove: int):
            self.__RemoveChar(remove)
            self.__ControlGroup.SetText(self.__CursorString())
    
    # def SaveBtnHandler(self, button: 'Button', action: str):
    #     if action == 'Pressed':
    #         button.SetState(1)
    #     elif action == 'Released':
    #         button.SetState(0)
    #         self.Save()
    
    # def __CancelBtnHandler(self, button: 'Button', action: str):
    #     if action == 'Pressed':
    #         button.SetState(1)
    #     elif action == 'Released':
    #         button.SetState(0)
    #         self.Close()
    
    def __CursorTimerHandler(self, timer: 'Timer', count: int):
        self.__ControlGroup.SetText(self.__CursorString(count % 2))
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __CharIndex(self):
        index = False
        if self.CapsLock:
            index = not index
        if self.Shift:
            index = not index
        
        return int(index is True)
    
    def __CursorString(self, cursorInd = 0):
        return self.Text[:self.__Pos] + self.__Cursor[cursorInd] + self.Text[self.__Pos:]
    
    def __InsertChar(self, char: str):
        self.Text = self.Text[:self.__Pos] + char + self.Text[self.__Pos:]
        self.__Pos += len(char)
        
    def __RemoveChar(self, count: int):
        if count > 0:
            if self.__Pos < (len(self.Text)):
                self.Text = self.Text[:self.__Pos] + self.Text[(self.__Pos + count):]
            else: # pragma: no cover
                # not covering this because coverage can't tell this has run.
                # see test_uofi_keyboardControl.py for more information
                pass # cursor is at the end of the string, there is nothing to remove
        elif count < 0:
            if self.__Pos >=0 and (self.__Pos + count) >= 0:
                self.Text = self.Text[:(self.__Pos + count)] + self.Text[self.__Pos:]
            else:
                pass # cursor is at the beginning of the string
            self.__Pos += count # fix Position after removing characters infront of the cursor
            if self.__Pos < 0: # fixes Position if it becomes less than zero
                self.__Pos = 0
        
    def __UpdateKeyboardState(self):
        for charBtn in self.__ControlGroup.Objects:
            charBtn.SetText(charBtn.char[self.__CharIndex()])
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def Open(self, Text: str='', Callback: Callable=None):
        self.Callback = Callback
        self.__ControlGroup.UIControls['Shift'].SetState(0)
        self.__ControlGroup.UIControls['CapsLock'].SetState(0)
        self.Shift = False
        self.CapsLock = False
        
        self.__CursorTimer.Restart()
        
        self.__UpdateKeyboardState()
        
        self.__Pos = len(Text)
        self.Text = Text
        
        self.__ControlGroup.SetText(self.__CursorString())
        
        self.UIHost.ShowPopup('Keyboard')
        
    def Save(self):
        self.Callback(self.Text)
        self.Close()
        
    def Close(self):
        self.Callback = None
        self.__CursorTimer.Stop()
        self.UIHost.HidePopup('Keyboard')

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def KeyboardCharHandler(source: 'ButtonEx', event: str) -> None:
    kb = source.UIHost.Keyboard
    kb.CharBtnHandler(source.char)

def RemoveCharHandler(source: 'ButtonEx', event: str) -> None:
    kb = source.UIHost.Keyboard
    kb.RemoveCharBtnHandler(source.remove)

def CancelHandler(source: 'ButtonEx', event: str) -> None:
    kb = source.UIHost.Keyboard
    kb.Close()

def SaveHandler(source: 'ButtonEx', event: str) -> None:
    kb = source.UIHost.Keyboard
    kb.Save()

def CapsLockHandler(source: 'ButtonEx', event: str) -> None:
    kb = source.UIHost.Keyboard
    kb.CapsLockBtnHandler()

def ShiftHandler(source: 'ButtonEx', event: str) -> None:
    kb = source.UIHost.Keyboard
    kb.ShiftBtnHandler()

def CursorHandler(source: 'ButtonEx', event: str) -> None:
    kb = source.UIHost.Keyboard
    kb.ArrowBtnHandler(source.shift)

def SpaceHandler(source: 'ButtonEx', event: str) -> None:
    kb = source.UIHost.Keyboard
    kb.SpaceBtnHandler()

## End Function Definitions ----------------------------------------------------



