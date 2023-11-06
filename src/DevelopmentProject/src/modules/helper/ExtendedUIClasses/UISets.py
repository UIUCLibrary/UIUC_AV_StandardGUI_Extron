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
    from modules.helper.ExtendedUIClasses import RefButton, ExButton, ExLabel, ExLevel

#### Python imports
import math

#### Extron Library Imports
from extronlib.system import MESet
# from extronlib.ui import Button, Level, Label

#### Project imports
import System
from modules.helper.ExtendedUIClasses.MixIns import ControlMixIn
from modules.helper.CommonUtilities import Logger, isinstanceEx
from modules.helper.ModuleSupport import eventEx
from Constants import SystemState

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class UISetMixin(object):
    def __init__(self, Name: str) -> None:
        self.__Name = Name
    
    @property
    def Name(self) -> str:
        return self.__Name
    
    @Name.setter
    def Name(self, val) -> None:
        raise AttributeError('Overriding the Name property is disallowed')
    
    def GetSubGroups(self) -> List:
        module = type(self).__name__
        groupNameList = ['BtnSet', 'RefSet']
        rtnList = []
        
        for grpName in groupNameList:
            if hasattr(self, '_{}__{}'.format(module, grpName)):
                rtnList.append(getattr(self, '_{}__{}'.format(module, grpName)))
        
        return rtnList

class RadioSet(ControlMixIn, UISetMixin, MESet):
    def __init__(self, 
                 Name: str,
                 Objects: List[Union['ExButton', 'RefButton']]) -> None:
        MESet.__init__(self, Objects)
        ControlMixIn.__init__(self)
        UISetMixin.__init__(self, Name)
        
        for btn in self.Objects:
            btn.Group = self
    
    def __repr__(self) -> str:
        sep = ', '
        return "RadioSet {} (Current: {}) [{}]".format(self.Name, self.GetCurrent(), sep.join([str(val) for val in self.Objects]))
    
    @property
    def Objects(self) -> List[Union['ExButton', 'RefButton']]:
        return super().Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is not allowed')
    
    def GetCurrent(self) -> Union['ExButton', 'RefButton']:
        return super().GetCurrent()
    
    def Append(self, obj: 'ExButton') -> None:
        setattr(obj, 'Group', self)
        return super().Append(obj)
    
    def Remove(self, obj: Union[List[Union[str, int, 'ExButton', 'RefButton']], str, int, 'ExButton', 'RefButton']) -> None:
        if isinstance(obj, list):
            for item in obj:
                self.Remove(item)
        elif type(obj).__name__ in [type(int).__name__, 'ExButton', 'RefButton']:
            if isinstance(obj, int):
                delattr(self.Objects[obj], 'Group')
            elif obj in self.Objects:
                delattr(obj, 'Group')
            super().Remove(obj)
        elif isinstance(obj, str):
            i = None
            for o in self.Objects:
                if o.Name == obj:
                    i = self.Objects.index(o)
                    break
            if i is not None:
                delattr(self.Objects[i], 'Group')
                super().Remove(i)
            else:
                raise ValueError('No object found for name ({}) in radio set'.format(obj))
        elif obj is not None:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetCurrent(self, obj: Union[int, str, 'ExButton', 'RefButton']) -> None:
        if isinstanceEx(obj, ('ExButton', 'RefButton')):
            super().SetCurrent(obj)
        elif obj is None:
            super().SetCurrent(obj)
        elif isinstance(obj, str):
            i = None
            for o in self.Objects:
                if o.Name == obj:
                    i = self.Objects.index(o)
                    break
            if i is not None:
                super().SetCurrent(i)
            else:
                raise ValueError('No object found for name ({}) in radio set'.format(obj))
        elif isinstance(obj, int):
            super().SetCurrent(obj)
        else:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetStates(self, obj: Union[List[Union[str, int, 'ExButton', 'RefButton']], str, int, 'ExButton', 'RefButton'], offState: int, onState: int) -> None:
        if isinstance(obj, list):
            for item in obj:
                self.SetStates(item, offState, onState)
        elif isinstanceEx(obj, (int, 'ExButton', 'RefButton')):
            super().SetStates(obj, offState, onState)
        elif isinstance(obj, str):
            i = None
            for o in self.Objects:
                if o.Name == obj:
                    i = self.Objects.index(o)
                    break
            if i is not None:
                super().SetStates(i, offState, onState)
            else:
                raise ValueError('No object found for name ({}) in radio set'.format(obj))
        elif obj is not None:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
class SelectSet(ControlMixIn, UISetMixin, object):
    def __init__(self, 
                 Name: str,
                 Objects: List[Union['ExButton', 'RefButton']]) -> None:
        ControlMixIn.__init__(self)
        UISetMixin.__init__(self, Name)
        
        self.__StateList = []
        self.__Objects = Objects
        
        for btn in self.__Objects:
            self.__StateList.append({"onState": 0, "offState": 1})
            btn.Group = self
    
    def __repr__(self) -> str:
        sep = ', '
        return "SelectSet {} (Current: [{}]) [{}]".format(self.Name, sep.join([str(val) for val in self.GetActive()]), sep.join([str(val) for val in self.Objects]))
    
    @property
    def Objects(self) -> List[Union['ExButton', 'RefButton']]:
        return self.__Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is not allowed')
    
    def Append(self, obj: Union['ExButton', 'RefButton']) -> None:
        setattr(obj, 'Group', self)
        self.__Objects.append(obj)
        self.__StateList.append({"onState": 0, "offState": 1})
        
    def GetActive(self) -> List[Union['ExButton', 'RefButton']]:
        activeList = []
        
        for o in self.__Objects:
            if o.State == self.__StateList[self.__Objects.index(o)]['onState']:
                activeList.append(o)
        
        return activeList
    
    def Remove(self, obj: Union[List[Union[str, int, 'ExButton', 'RefButton']], str, int, 'ExButton', 'RefButton']) -> None:
        if isinstance(obj, list):
            for item in obj:
                self.Remove(item)
        elif isinstance(obj, int):
            delattr(self.__Objects[obj], 'Group')
            self.__Objects.pop(obj)
            self.__StateList.pop(obj)
        elif isinstanceEx(obj, ('ExButton', 'RefButton')):
            delattr(obj, 'Group')
            i = self.__Objects.index(obj)
            self.__Objects.pop(obj)
            self.__StateList.pop(obj)
        elif isinstance(obj, str):
            i = None
            for o in self.__Objects:
                if o.Name == obj:
                    i = self.__Objects.index(o)
                    break
            if i is not None:
                delattr(self.__Objects[obj], 'Group')
                self.__Objects.pop(obj)
                self.__StateList.pop(obj)
            else:
                raise ValueError('No object found for name ({}) in select set'.format(obj))
        elif obj is not None:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
    def SetActive(self, obj: Union[List[Union[str, int, 'ExButton', 'RefButton']], str, int, 'ExButton', 'RefButton']) -> None:
        if isinstance(obj, list):
            for item in obj:
                self.SetActive(item)
        elif obj in ['all', 'All', 'ALL']:
            for o in self.__Objects:
                o.SetState(self.__StateList[self.__Objects.index(o)]['onState'])
        elif obj in ['none', 'None', 'NONE'] or obj is None:
            for o in self.__Objects:
                o.SetState(self.__StateList[self.__Objects.index(o)]['offState'])
        elif isinstance(obj, int):
            self.__Objects[obj].SetState(self.__StateList[obj]['onState'])
        elif isinstance(obj, str):
            i = None
            for o in self.__Objects:
                if o.Name == obj:
                    i = self.__Objects.index(o)
                    break
            if i is not None:
                self.__Objects[i].SetState(self.__StateList[i]['onState'])
            else:
                raise ValueError('No object found for name ({}) in select set'.format(obj))
        elif type(obj).__name__ in ['ExButton', 'RefButton']:
            if obj in self.__Objects:
                obj.SetState(self.__StateList[self.__Objects.index(obj)]['onState'])
            else:
                raise IndexError('Object not found in select list')
        elif obj is not None:
            raise TypeError('Object must be an object name, int index, the button object (Button or ExButton class), or List of these')

    def SetStates(self, obj: Union[List[Union[str, int, 'ExButton', 'RefButton']], str, int, 'ExButton', 'RefButton'], offState: int, onState: int) -> None:
        if isinstance(obj, list):
            for item in obj:
                self.SetStates(item, offState, onState)
        elif isinstance(obj, int):
            self.__StateList[obj]['onState'] = onState
            self.__StateList[obj]['offState'] = offState
        elif isinstanceEx(obj, ('ExButton', 'RefButton')):
            i = self.__Objects.index(obj)
            self.__StateList[i]['onState'] = onState
            self.__StateList[i]['offState'] = offState
        elif isinstance(obj, str):
            i = None
            for o in self.__Objects:
                if o.Name == obj:
                    i = self.__Objects.index(o)
                    break
            if i is not None:
                self.__StateList[i]['onState'] = onState
                self.__StateList[i]['offState'] = offState
            else:
                raise ValueError('No object found for name ({}) in select set'.format(obj))
        elif obj is not None:
            raise TypeError("Object must be string object name, int index, or the button object (Button or ExButton class)")
    
class VariableRadioSet(ControlMixIn, UISetMixin, object):
    def __init__(self, 
                 Name: str,
                 Objects: List['ExButton'],
                 PopupCallback: Callable,
                 PopupGroups: List[Dict[str, str]] = None) -> None:
        ControlMixIn.__init__(self)
        UISetMixin.__init__(self, Name)
        
        self.__BtnSet = RadioSet('{}-Objects'.format(self.Name), Objects)
        self.__PopupCallback = PopupCallback
        self.__PopupGroups = PopupGroups
        
        self.__BtnSet.Group = self
    
    def __repr__(self) -> str:
        sep = ', '
        return "VariableRadioSet {} (Current: {}, Popup: {}) [{}]".format(self.Name, self.GetCurrent(), self.PopupName, sep.join([str(val) for val in self.Objects]))
    
    @property
    def Objects(self) -> List['ExButton']:
        return self.__BtnSet.Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    @property
    def PopupName(self) -> str:
        return self.__PopupCallback(self.__BtnSet.Objects)
    
    @PopupName.setter
    def PopupName(self, val) -> None:
        raise AttributeError('Overriding the PopupName property is disallowed')    
    
    def Append(self, obj: 'ExButton' = None) -> None:
        if obj is not None:
            setattr(obj, 'Group', self)
            self.__BtnSet.Append(obj)
            
    def GetCurrent(self) -> 'ExButton':
        return self.__BtnSet.GetCurrent()
    
    def Remove(self, 
               Object: Union[int, str, 'ExButton'] = None, 
               Popup: Union[int, str] = None) -> None:
        
        if Object is not None:
            self.__BtnSet.Remove(Object)
            
        if Popup is not None:
            if isinstance(Popup, int):
                self.__PopupDict.pop(Popup)
            elif isinstance(Popup, str):
                for key, val in self.__PopupDict:
                    if val == Popup:
                        self.__PopupDict.pop(key)
                        break
            else:
                raise TypeError('Popup must either by an int or str')
            
        self.__PopupKey = self.__GetPopupKey()
            
    def SetCurrent(self, obj: Union[int, str, 'ExButton']) -> None:
        self.__BtnSet.SetCurrent(obj)
        
    def SetStates(self, 
                  obj: Union[List[Union[int, str, 'ExButton']], 
                             int, 
                             str, 
                             'ExButton'], 
                  offState: int, 
                  onState: int) -> None:
        
        self.__BtnSet.SetStates(obj, offState, onState)
        
    def ShowPopup(self) -> None:
        if self.__PopupGroups is not None:
            for pug in self.__PopupGroups:
                if pug['Suffix'] is None:
                    self.__BtnSet.Objects[0].Host.ShowPopup(self.PopupName)
                else:
                    self.__BtnSet.Objects[0].Host.ShowPopup('{}_{}'.format(self.PopupName, str(pug['Suffix'])))
        else:
            self.__BtnSet.Objects[0].Host.ShowPopup(self.PopupName)
        
class ScrollingRadioSet(ControlMixIn, UISetMixin, object):
    def __init__(self, 
                 Name: str,
                 Objects: List['ExButton'], 
                 RefObjects: List['RefButton'],
                 PrevBtn: 'ExButton', 
                 NextBtn: 'ExButton', 
                 PopupCallback: Callable,
                 PopupGroups: List[Dict[str, str]] = None) -> None:
        ControlMixIn.__init__(self)
        UISetMixin.__init__(self, Name)
        
        self.__Offset = 0
        self.__BtnSet = RadioSet('{}-Objects'.format(self.Name), Objects)
        self.__BtnSet.Group = self
        self.__RefSet = RadioSet('{}-RefObjects'.format(self.Name), RefObjects)
        self.__RefSet.Group = self
        self.__Prev = PrevBtn
        self.__Prev.Group = self
        self.__Next = NextBtn
        self.__Next.Group = self
        
        self.__PopupCallback = PopupCallback
        self.__PopupGroups = PopupGroups
        
        self.__BtnSet.Group = self
        self.__RefSet.Group = self
        
        self.LoadButtonView()

    def __repr__(self) -> str:
        sep = ', '
        return "ScrollingRadioSet {} (Current: {}, Popup: {}) [{}]".format(self.Name, self.GetCurrentRef(), self.PopupName, sep.join([str(val) for val in self.RefObjects]))
    
    @property
    def Objects(self) -> List['ExButton']:
        return self.__BtnSet.Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    @property
    def RefObjects(self) -> List['RefButton']:
        return self.__RefSet.Objects
    
    @RefObjects.setter
    def RefObjects(self, val) -> None:
        raise AttributeError('Overriding the RefObjects property is disallowed')
    
    @property
    def UIControls(self) -> Dict[str, 'ExButton']:
        return {
            'Previous': self.__Prev,
            'Next': self.__Next
        }
    
    @UIControls.setter
    def UIControls(self) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    @property
    def Offset(self) -> int:
        return self.__Offset
    
    @Offset.setter
    def Offset(self, val) -> None:
        raise AttributeError('Overriding the Offset property is disallowed')
    
    @property
    def PopupName(self) -> str:
        return self.__PopupCallback(self)
    
    @PopupName.setter
    def PopupName(self, val) -> None:
        raise AttributeError('Overriding the PopupName property is disallowed')
    
    @property
    def Pages(self) -> int:
        return math.ceil((len(self.RefObjects)/len(self.Objects)))
    
    @Pages.setter
    def Pages(self, val) -> None:
        raise AttributeError('Overriding the Pages property is disallowed')
    
    @property
    def CurrentPage(self) -> int:
        index = self.Offset + 1
        pg = math.ceil((index/len(self.Objects)))
        return pg
    
    def GetRefByObject(self, obj: Union[int, str, 'ExButton']) -> 'RefButton':
        if isinstance(obj, int):
            return self.__RefSet.Objects[obj + self.__Offset]
        elif isinstance(obj, str):
            for btn in self.__BtnSet.Objects:
                if btn.Name == obj:
                    return self.__RefSet.Objects[self.__BtnSet.Objects.index(btn) + self.__Offset]
            return None
        elif isinstanceEx(obj, 'ExButton'):
            return self.__RefSet.Objects[self.__BtnSet.Objects.index(obj) + self.__Offset]
        else:
            raise TypeError('obj must be an index int, name str, Button or ExButton object')
    
    def GetObjectByRef(self, ref: Union[int, str, 'RefButton']) -> Union[None, 'ExButton']:
        objIndex = None
        
        Logger.Log("GetObjectByRef Ref:", ref, type(ref))
        
        if isinstance(ref, int):
            objIndex = ref - self.__Offset
            
        elif isinstance(ref, str):
            for refBtn in self.__RefSet.Objects:
                if refBtn.Name == ref:
                    objIndex = self.__RefSet.Objects.index(refBtn) - self.__Offset
                    
        elif isinstanceEx(ref, 'RefButton'):
            objIndex = self.__RefSet.Objects.index(ref) - self.__Offset
        
        Logger.Log("ObjIndex", objIndex, self.__Offset)
        
        if objIndex is None:
            return None
        elif objIndex >= 0 and objIndex < len(self.Objects):
            return self.__BtnSet.Objects[objIndex]
        else:
            return None
    
    def GetCurrentButton(self) -> 'ExButton':
        return self.__BtnSet.GetCurrent()
    
    def GetCurrentRef(self) -> 'RefButton':
        return self.__RefSet.GetCurrent()
    
    def AppendButton(self, btn: 'ExButton') -> None:
        self.__BtnSet.Append(btn)
        btn.Group = self
    
    def AppendRef(self, ref: 'RefButton') -> None:
        self.__RefSet.Append(ref)
        ref.Group = self
        
    def RemoveButton(self, btn: Union[List[Union[int, str, 'ExButton']], int, str, 'ExButton']) -> None:
        self.__BtnSet.Remove(btn)
        
    def RemoveRef(self, btn: Union[List[Union[int, str, 'RefButton']], int, str, 'RefButton']) -> None:
        self.__RefSet.Remove(btn)
        
    def SetCurrentButton(self, btn: Union[int, str, 'ExButton', None]) -> None:
        self.__BtnSet.SetCurrent(btn)
        
        index = self.__BtnSet.Objects.index(self.__BtnSet.GetCurrent())
        refIndex = index + self.__Offset
        self.__RefSet.SetCurrent(refIndex)
        
    def SetCurrentRef(self, ref: Union[int, str, 'RefButton']) -> None:
        self.__RefSet.SetCurrent(ref)
        
        index = self.__RefSet.Objects.index(self.__RefSet.GetCurrent())
        btnIndex = index - self.__Offset
        
        if btnIndex < 0:
            self.__BtnSet.SetCurrent(None)
        elif btnIndex >= 0 and btnIndex < len(self.__BtnSet.Objects):
            self.__BtnSet.SetCurrent(btnIndex)
        elif btnIndex > len(self.__BtnSet.Objects):
            self.__BtnSet.SetCurrent(None)
            
    def SetStates(self, obj: Union[List[Union[int, str, 'ExButton']], int, str, 'ExButton'], offState: int, onState: int) -> None:
        self.__BtnSet.SetStates(obj, offState, onState)
        
    def ShowPopup(self, suffix: str=None) -> None:
        if self.__PopupGroups is not None:
            for pug in self.__PopupGroups:
                if pug['Suffix'] is None:
                    self.__BtnSet.Objects[0].Host.ShowPopup(self.PopupName)
                else:
                    self.__BtnSet.Objects[0].Host.ShowPopup('{}_{}'.format(self.PopupName, str(pug['Suffix'])))
        else:
            self.__BtnSet.Objects[0].Host.ShowPopup(self.PopupName)
        
    def LoadButtonView(self) -> None:
        Logger.Log('Current Page', self.CurrentPage, 'Pages', self.Pages, 'Offset', self.Offset)
        if self.CurrentPage == 1:
            # Disabled Prev button
            self.__Prev.SetEnable(False)
            self.__Prev.SetState(2)
        else:
            self.__Prev.SetEnable(True)
            self.__Prev.SetState(0)
            
        if self.CurrentPage == self.Pages:
            # Disabled Next button
            self.__Next.SetEnable(False)
            self.__Next.SetState(2)
        else:
            self.__Next.SetEnable(True)
            self.__Next.SetState(0)
            
        endOffset = self.Offset + len(self.Objects)
        
        self.__BtnSet.SetCurrent(None)
        
        curRefSet = self.RefObjects[self.Offset:endOffset]
        
        for btn in self.Objects:
            # Set Names and icons
            index = self.Objects.index(btn)
            
            btn.SetText(curRefSet[index].Text)
            # TODO: Set Icon state
        
        Logger.Log("Current Object", self.GetCurrentRef(), self.GetObjectByRef(self.GetCurrentRef()))
        
        curObj = self.GetObjectByRef(self.GetCurrentRef())
        if curObj is not None:
            self.SetCurrentButton(curObj)
    
    def SetOffset(self, Offset: int) -> None:
        if not isinstance(Offset, int):
            raise TypeError('Offset must be an integer')
        elif (Offset < 0 or Offset >= len(self.RefObjects)):
            raise ValueError("Offset must be greater than or equal to 0 and less than the number of Ref Objects ({})".format(len(self.RefObjects)))
        self.__Offset = Offset
        self.LoadButtonView()
        
class VolumeControlGroup(ControlMixIn, UISetMixin, object):
    def __init__(self,
                 Name: str,
                 VolUp: 'ExButton',
                 VolDown: 'ExButton',
                 Mute: 'ExButton',
                 Feedback: 'ExLevel',
                 ControlLabel: 'ExLabel'=None,
                 DisplayName: str=None,
                 Range: Tuple[int, int, int]=(0, 100, 1)
                 ) -> None:
        ControlMixIn.__init__(self)
        UISetMixin.__init__(self, Name)
        
        if type(VolUp).__name__ in ['ExButton']:
            self.VolUpBtn = VolUp
            self.VolUpBtn.Group = self
        else:
            raise TypeError("VolUp must be an Extron Button object")
        
        if type(VolDown).__name__ in ['ExButton']:
            self.VolDownBtn = VolDown
            self.VolDownBtn.Group = self
        else:
            raise TypeError("VolDown must be an Extron Button object")
        
        if type(Mute).__name__ in ['ExButton']:
            self.MuteBtn = Mute
            self.MuteBtn.Group = self
        else:
            raise TypeError("Mute must be an Extron Button object")
        
        if type(Feedback).__name__ in ['ExLevel']:
            self.FeedbackLvl = Feedback
            self.FeedbackLvl.Group = self
        else:
            raise TypeError("Feedback must be an Extron Level object")
        
        if type(ControlLabel).__name__ in ['ExLabel'] or ControlLabel is None:
            self.ControlLbl = ControlLabel
            self.ControlLbl.Group = self
        else:
            raise TypeError("ControlLabel must either be an Extron Label object or None (default)")
        
        if DisplayName is not None:
            self.DisplayName = DisplayName
        else:
            self.DisplayName = Name
            
        if type(Range) is tuple and len(Range) == 3:
            for i in Range:
                if not isinstance(i, int):
                    raise TypeError("Range tuple may only consist of int values")
            self.__Range = Range
            self.FeedbackLvl.SetRange(*Range)
            
    def __repr__(self) -> str:
        return "VolumeControlSet {}".format(self.Name)
    
        
class HeaderControlGroup(ControlMixIn, UISetMixin, object):
    def __init__(self, 
                 Name, 
                 RoomButton: 'ExButton',
                 HelpButton: 'ExButton',
                 AudioButton: 'ExButton',
                 LightsButton: 'ExButton',
                 CameraButton: 'ExButton',
                 AlertButton: 'ExButton',
                 CloseButton: 'ExButton') -> None:
        ControlMixIn.__init__(self)
        UISetMixin.__init__(self, Name)
        
        self.__RoomButton = RoomButton
        setattr(self.__RoomButton, 'HeaderAction', 'Room')
        self.__RoomButton.SetEnable(False)
        
        self.__HelpButton = HelpButton
        setattr(self.__HelpButton, 'HeaderAction', 'Help')
        
        self.__AudioButton = AudioButton
        setattr(self.__AudioButton, 'HeaderAction', 'Audio')
        setattr(self.__AudioButton, 'PopoverSuffix', self.__AudioSuffixCallback)
        
        self.__LightsButton = LightsButton
        setattr(self.__LightsButton, 'HeaderAction', 'Lights')
        setattr(self.__LightsButton, 'PopoverSuffix', self.__LightsSuffixCallback)
        
        self.__CameraButton = CameraButton
        setattr(self.__CameraButton, 'HeaderAction', 'Camera')
        setattr(self.__CameraButton, 'PopoverSuffix', self.__CameraSuffixCallback)
        self.__CameraButton.SetVisible(False)
        
        self.__AlertButton = AlertButton
        setattr(self.__AlertButton, 'HeaderAction', 'Alert')
        self.__AlertButton.SetVisible(False)
        
        self.__CloseButton = CloseButton
        setattr(self.__CloseButton, 'HeaderAction', 'Close')
        
        for btn in self.UIControls.values():
            btn.Group = self
            
        @eventEx(System.CONTROLLER.SystemStateWatch, 'Changed')
        def SystemStateHandler(source, State: SystemState):
            if State is SystemState.Active:
                self.__CameraButton.SetVisible(True)
            elif State is SystemState.Standby:
                self.__CameraButton.SetVisible(False)
    
    def __repr__(self) -> str:
        return "HeaderControlGroup {}".format(self.Name)
    
    @property
    def UIControls(self) -> Dict[str, 'ExButton']:
        return {
            'Room': self.__RoomButton,
            'Help': self.__HelpButton, 
            'Audio': self.__AudioButton, 
            'Lights': self.__LightsButton, 
            'Camera': self.__CameraButton, 
            'Alert': self.__AlertButton,
            'Close': self.__CloseButton
        }
    
    @UIControls.setter
    def UIControls(self, val) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    def __AudioSuffixCallback(self) -> str:
        return str(len(System.CONTROLLER.Devices.Microphones))
    
    def __CameraSuffixCallback(self) -> str:
        return str(len(System.CONTROLLER.Devices.Cameras))
    
    def __LightsSuffixCallback(self) -> str:
        return str(len(System.CONTROLLER.Devices.Lights))
    
    def SetStates(self, obj: Union[List[Union[int, str, 'ExButton']], int, str, 'ExButton'], offState: int, onState: int) -> None:
        Logger.Log('Attempting to set states of Header Control Group')

class PINPadControlGroup(ControlMixIn, UISetMixin, object):
    def __init__(self, 
                 Name: str, 
                 Objects: List['ExButton'], 
                 BackspaceButton: 'ExButton', 
                 CancelButton: 'ExButton',
                 TextAreaLabel: 'ExLabel') -> None:
        ControlMixIn.__init__(self)
        UISetMixin.__init__(self, Name)
        
        self.__BtnSet = SelectSet('{}-Objects'.format(self.Name), Objects)
        self.__BackspaceBtn = BackspaceButton
        self.__CancelBtn = CancelButton
        self.__TextArea = TextAreaLabel
        
    def __repr__(self) -> str:
        return "PINPadControlGroup {}".format(self.Name)
    
    @property
    def Objects(self) -> List['ExButton']:
        return self.__BtnSet.Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    @property
    def UIControls(self) -> Dict[str, 'ExButton']:
        return {
            'Backspace': self.__BackspaceBtn,
            'Cancel': self.__CancelBtn
        }
    
    @UIControls.setter
    def UIControls(self) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    def SetStates(self, obj: Union[List[Union[int, str, 'ExButton']], int, str, 'ExButton'], offState: int, onState: int) -> None:
        self.__BtnSet.SetStates(obj, offState, onState)
        
    def SetText(self, value: str) -> None:
        self.__TextArea.SetText(value)

class KeyboardControlGroup(ControlMixIn, UISetMixin, object):
    def __init__(self, 
                 Name: str, 
                 Objects: List['ExButton'], 
                 BackspaceButton: 'ExButton', 
                 DeleteButton: 'ExButton',
                 CancelButton: 'ExButton',
                 SaveButton: 'ExButton',
                 CapsLockButton: 'ExButton',
                 ShiftButton: 'ExButton',
                 SpaceButton: 'ExButton',
                 CursorLeftButton: 'ExButton',
                 CursorRightButton: 'ExButton',
                 TextAreaLabel: 'ExLabel') -> None:
        ControlMixIn.__init__(self)
        UISetMixin.__init__(self, Name)
        
        self.__BtnSet = SelectSet('{}-Objects'.format(self.Name), Objects)
        self.__BackspaceBtn = BackspaceButton
        self.__DeleteBtn = DeleteButton
        self.__CancelBtn = CancelButton
        self.__SaveBtn = SaveButton
        self.__CapsLockBtn = CapsLockButton
        self.__ShiftBtn = ShiftButton
        self.__SpaceBtn = SpaceButton
        self.__CursorLeftBtn = CursorLeftButton
        self.__CursorRightBtn = CursorRightButton
        
        self.__TextArea = TextAreaLabel
        
    def __repr__(self) -> str:
        return "KeyboardControlGroup {}".format(self.Name)
    
    @property
    def Objects(self) -> List['ExButton']:
        return self.__BtnSet.Objects
    
    @Objects.setter
    def Objects(self, val) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    @property
    def UIControls(self) -> Dict[str, 'ExButton']:
        return {
            'Backspace': self.__BackspaceBtn,
            'Delete': self.__DeleteBtn,
            'Cancel': self.__CancelBtn,
            'Save': self.__SaveBtn,
            'CapsLock': self.__CapsLockBtn,
            'Shift': self.__ShiftBtn,
            'Space': self.__SpaceBtn,
            'CursorLeft': self.__CursorLeftBtn,
            'CursorRight': self.__CursorRightBtn
        }
    
    @UIControls.setter
    def UIControls(self) -> None:
        raise AttributeError('Overriding the Objects property is disallowed')
    
    def SetText(self, value: str) -> None:
        self.__TextArea.SetText(value)
        
    def SetStates(self, obj: Union[List[Union[int, str, 'ExButton']], int, str, 'ExButton'], offState: int, onState: int) -> None:
        self.__BtnSet.SetStates(obj, offState, onState)
        
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------


