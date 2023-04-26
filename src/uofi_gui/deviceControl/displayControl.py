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
    from extronlib.ui import Button, Slider
    
## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.system import Wait
from extronlib.interface import RelayInterface
from extronlib.ui import Button, Knob, Label, Level, Slider

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug
from uofi_gui.sourceControls import Destination

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class DisplayController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        
        self.__Labels = \
            {
                'conf': {},
                'proj': {},
                'scn': {},
                'mon': {}
            }
        self.__Controls = {}
        for k in self.__Labels:
            self.__Labels[k] = DictValueSearchByKey(self.UIHost.Lbls, r'DisplayCtl-{}-(\d+)'.format(k), regex=True, capture_dict=True)
            if k != 'scn':  
                self.__Controls[k] = {}
                for i in range(1, len(self.__Labels[k])+1):
                    self.__Controls[k][str(i)] = DictValueSearchByKey(self.UIHost.Btns, r'Tech-Display-{}-{}-(\w+)'.format(k, str(i)), regex=True, capture_dict=True)
                    if k == 'proj':
                        self.__Controls[k][str(i)].update(DictValueSearchByKey(self.UIHost.Btns, r'Tech-Display-scn-{}-(\w+)'.format(str(i)), regex=True, capture_dict=True))
                    if k == 'mon':
                        self.__Controls[k][str(i)].update({'Vol': self.UIHost.Slds['Tech-Display-mon-{}-Vol'.format(str(i))]})
        
        self.__ControlList = []
        for hw_type, group_dict in self.__Controls.items():
            for group, ctl_dict in group_dict.items():
                for ctl_type, ctl in ctl_dict.items():
                    ctl.CtlType = ctl_type
                    ctl.HwType = hw_type
                    ctl.CtlGroup = group
                    # disable all controls as we add them to the the control list
                    # will enable controls tied to active displays
                    ctl.SetEnable(False)
                    self.__ControlList.append(ctl)
        
        self.Destinations = {}
        conf_assign = 1
        mon_assign = 1
        proj_assign = 1
        for dest in self.GUIHost.Destinations:
            self.Destinations[dest['id']] = dest
            self.Destinations[dest['id']]['hw'] = self.GUIHost.Hardware.get(dest['id'], None)
            self.Destinations[dest['id']]['mute'] = False
            self.Destinations[dest['id']]['volume'] = 0.0
            
            if dest['type'] == 'conf' or dest['type'] == 'c-conf':
                self.Destinations[dest['id']]['hw_type'] = 'conf'
                self.Destinations[dest['id']]['ctl_group'] = str(conf_assign)
                self.__Labels['conf'][str(conf_assign)].SetText(dest['name'])
                if dest['type'] == 'conf':
                    for key, ctl in self.__Controls['conf'][str(conf_assign)].items():
                        ctl.DestID = dest['id']
                        ctl.SetEnable(True)
                        if key == 'Src':
                            ctl.SetEnable(False)
                            ctl.SetVisible(False)
                        elif key == 'On' or key == 'Off':
                            ctl.ConfControlType = 'switcher'
                elif dest['type'] == 'c-conf':
                    self.Destinations[dest['id']]['hw_type'] = 'conf'
                    self.Destinations[dest['id']]['ctl_group'] = str(conf_assign)
                    self.__Labels['conf'][str(conf_assign)].SetText(dest['name'])
                    for key, ctl in self.__Controls['conf'][str(conf_assign)].items():
                        ctl.DestID = dest['id']
                        ctl.SetEnable(True)
                        if key == 'On' or key == 'Off':
                            ctl.ConfControlType = 'display'
                conf_assign += 1
            elif dest['type'] == 'mon':
                self.Destinations[dest['id']]['hw_type'] = 'mon'
                self.Destinations[dest['id']]['ctl_group'] = str(mon_assign)
                self.__Labels['mon'][str(mon_assign)].SetText(dest['name'])
                for key, ctl in self.__Controls['mon'][str(mon_assign)].items():
                    ctl.DestID = dest['id']
                    ctl.SetEnable(True)
                    # Set range for monitor volume slider based on hardware options
                    if key == 'Vol' and hasattr(self.Destinations[dest['id']]['hw'], 'VolumeRange'):
                        ctl.SetRange(*self.Destinations[dest['id']]['hw'].VolumeRange)
                mon_assign += 1
            elif dest['type'] == 'proj' or dest['type'] == 'proj+scn':
                self.Destinations[dest['id']]['hw_type'] = 'proj'
                self.Destinations[dest['id']]['ctl_group'] = str(proj_assign)
                self.__Labels['proj'][str(proj_assign)].SetText(dest['name'])
                if dest['type'] == 'proj':
                    # hide screen controls
                    self.__Labels['scn'][str(proj_assign)].SetVisible(False)
                    for key, ctl in self.__Controls['proj'][str(proj_assign)].items():
                        if key == 'Stop' or key == 'Up' or key == 'Dn':
                            ctl.SetEnable(False)
                            ctl.SetVisible(False)
                        ctl.DestID = dest['id']
                        ctl.SetEnable(True)
                elif dest['type'] == 'proj+scn':
                    # configure screen controls
                    self.__Labels['scn'][str(proj_assign)].SetText('{} Screen'.format(dest['name']))
                    for ctl in self.__Controls['proj'][str(proj_assign)].values():
                        ctl.DestID = dest['id']
                        ctl.SetEnable(True)
                        
                    # instanciate projector screen relay control
                    self.Destinations[dest['id']]['Scn'] = {}
                    if type(self.Destinations[dest['id']]['rly'][0]) is int:
                        self.Destinations[dest['id']]['Scn']['up'] = RelayInterface(self.GUIHost.CtlProc_Main, 'RLY{}'.format(self.Destinations[dest['id']]['rly'][0]))
                        self.Destinations[dest['id']]['Scn']['up'].SetState('Open')
                    else:
                        # TODO: figure out standardization for relays attached to devices other than the main control processor
                        pass
                    if type(self.Destinations[dest['id']]['rly'][1]) is int:
                        self.Destinations[dest['id']]['Scn']['dn'] = RelayInterface(self.GUIHost.CtlProc_Main, 'RLY{}'.format(self.Destinations[dest['id']]['rly'][1]))
                        self.Destinations[dest['id']]['Scn']['dn'].SetState('Open')
                    else:
                        # TODO: figure out standardization for relays attached to devices other than the main control processor
                        pass
                
                proj_assign += 1
        
        @event([ctl for ctl in self.__ControlList if type(ctl) is Slider], ['Changed']) # pragma: no cover
        def sliderFillHandler(control: 'Slider', action: str, value: float):
            self.__SliderFillHandler(control, action, value)
        
        @event(self.__ControlList, ['Pressed', 'Released']) # pragma: no cover
        def displayControlButtonHandler(control: Union['Button', 'Slider'], action: str, value: float=None):
            self.__DisplayControlButtonHandler(control, action, value)
            
    @property
    def DisplayMute(self) -> Dict[str, bool]:
        rtnDict = {}
        for key, dest in self.Destinations.items():
            rtnDict[key] = dest['mute']
                
        return rtnDict
    
    @DisplayMute.setter
    def DisplayMute(self, Value: Tuple[Union[str, Destination], Union[str, int, bool]]):
        if type(Value) is not tuple:
            raise TypeError('Value must be a Tuple')
        if type(Value[0]) not in [str, Destination] or type(Value[1]) not in [str, int, bool]:
            raise TypeError('Value must be a Tuple with index [0] being a Destination (str or Destination object) and index [1] being a mute state')
        
        dest = Value[0]
        State = Value[1]
        
        setState = (State in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE'])
        
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
            self.Destinations[dest]['mute'] = setState
        elif type(dest) is Destination:
            Hw = self.Destinations[dest.Id]['hw']
            self.Destinations[dest.Id]['mute'] = setState
        
        value = 'On' if setState else 'Off'
        
        qual = Hw.MuteCommand.get('qualifier', None)
            
        Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.MuteCommand['command'], value, qual))
        Hw.interface.Set(Hw.MuteCommand['command'], value, qual)

    @property
    def DisplayVolume(self):
        rtnDict = {}
        for key, dest in self.Destinations.items():
            rtnDict[key] = dest['volume']

        return rtnDict
    
    @DisplayVolume.setter
    def DisplayVolume(self, Value: Tuple[Union[str, Destination], Union[str, int, bool]]):
        if type(Value) is not tuple:
            raise TypeError('Value must be a Tuple')
        if type(Value[0]) not in [str, Destination] or type(Value[1]) not in [int, float]:
            raise TypeError('Value must be a Tuple with index [0] being a Destination (str or Destination object) and index [1] being a volume (int or float)')
        
        dest = Value[0]
        value = int(Value[1])
        
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
            self.Destinations[dest]['volume'] = value
        elif type(dest) is Destination:
            Hw = self.Destinations[dest.Id]['hw']
            self.Destinations[dest.Id]['volume'] = value
            
        qual = Hw.VolumeCommand.get('qualifier', None)
            
        Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.VolumeCommand['command'], value, qual))
        Hw.interface.Set(Hw.VolumeCommand['command'], value, qual)   

    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __SliderFillHandler(self, control: 'Slider', action: str, value: float):
        if type(control) == Slider:
            control.SetFill(value)
                
    def __DisplayControlButtonHandler(self, control: Union['Button', 'Slider'], action: str, value: float=None):
        if control.Enabled is False:
            # do not process disabled buttons
            return
        
        if action == 'Pressed':
            if type(control) == Button:
                if control.CtlType == 'Mute':
                    if control.State == 0:
                        control.SetState(1)
                    else:
                        control.SetState(0)
                else:
                    control.SetState(1)
        elif action == 'Released':
            # Log('Display Control - Hardware: {} ({}), CtlType: {}, HwType: {}'.format(control.DestID, control.CtlGroup, control.CtlType, control.HwType))
            if control.CtlType == 'On':
                # set display on, clear off button state
                if control.HwType == 'conf' and control.ConfControlType == 'switcher':
                    output = self.Destinations[control.DestID]['output']
                    self.GUIHost.Hardware[self.GUIHost.PrimarySwitcherId].interface.Set('VideoMute', 'Off', {'Output': output}) # sets video mute off, which turns on the display
                else:
                    self.SetDisplayPower(control.DestID, 'On')
                self.__Controls[control.HwType][control.CtlGroup]['Off'].SetState(0)
                control.SetBlinking('Medium', [0,1])
            elif control.CtlType == 'Off':
                # set display off, clear on button state
                if control.HwType == 'conf' and control.ConfControlType == 'switcher':
                    output = self.Destinations[control.DestID]['output']
                    self.GUIHost.Hardware[self.GUIHost.PrimarySwitcherId].interface.Set('VideoMute', 'Video & Sync', {'Output': output}) # sets video mute on, which turns off the display
                else:
                    self.SetDisplayPower(control.DestID, 'Off')
                self.__Controls[control.HwType][control.CtlGroup]['On'].SetState(0)
                control.SetBlinking('Medium', [0,1])
            elif control.CtlType == 'Src':
                # set display back to default input source
                if control.HwType == 'conf' and control.ConfControlType == 'switcher':
                    # There is no source to set on the conference display so do nothing
                    pass
                else:
                    self.SetDisplaySource(control.DestID)
                @Wait(3) # pragma: no cover
                def delayFeedbackHandler():
                    control.SetState(0)
            elif control.CtlType == 'Up':
                # send screen up
                self.Destinations[control.DestID]['Scn']['up'].Pulse(2)
                # Log('Pulse Up Relay')
                @Wait(3) # pragma: no cover
                def delayFeedbackHandler():
                    control.SetState(0)
            elif control.CtlType == 'Dn':
                # send screen down
                self.Destinations[control.DestID]['Scn']['dn'].Pulse(2)
                # Log('Pulse Down Relay')
                @Wait(3) # pragma: no cover
                def delayFeedbackHandler():
                    control.SetState(0)
            elif control.CtlType == 'Stop':
                # send screen stop
                # This assumes that the screen stop command is to close both the up and down contact closures
                self.Destinations[control.DestID]['Scn']['up'].Pulse(2)
                self.Destinations[control.DestID]['Scn']['dn'].Pulse(2)
                # Log('Pulse Up & Down Relays')
                @Wait(3) # pragma: no cover
                def delayFeedbackHandler():
                    control.SetState(0)
            elif control.CtlType == 'Mute':
                # set display mute toggle - button state has been changed to the approprate mute state
                if control.State:
                    self.DisplayMute = (control.DestID, 'On')
                else:
                    self.DisplayMute = (control.DestID, 'Off')
            elif control.CtlType == 'Vol' and value is not None:
                # Log('Slider - new value = {}'.format(value))
                self.DisplayVolume = (control.DestID, value)
                control.SetFill(value)
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def SetDisplayPower(self, dest: Union[str, 'Destination'], state: str='On'):
        # Log('Dest: {}; State: {}'.format(dest, state))
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Destination:
            Hw = self.Destinations[dest.Id]['hw']
        else:
            raise TypeError("Dest must either by a string destination ID or a Destination object")
        
        if Hw is None:
            raise LookupError('Destination ({}) not found'.format(dest))
        
        qual = Hw.PowerCommand.get('qualifier', None)
        
        Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.PowerCommand['command'], state, qual))
        Hw.interface.Set(Hw.PowerCommand['command'], state, qual)
    
    def SetDisplaySource(self, dest: Union[str, 'Destination']):
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Destination:
            Hw = self.Destinations[dest.Id]['hw']
        else:
            raise TypeError("Dest must either by a string destination ID or a Destination object")
        
        if Hw is None:
            raise LookupError('Destination hardware ({}) not found'.format(dest))
        
        qual = Hw.SourceCommand.get('qualifier', None)
        
        if 'value' in Hw.SourceCommand:
            state = Hw.SourceCommand['value']
        else:
            raise KeyError('Display source value not found for {}'.format(dest))
        
        Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.SourceCommand['command'], state, qual))
        Hw.interface.Set(Hw.SourceCommand['command'], state, qual)
        
    def DisplayPowerFeedback(self, HwID: str, state: str):
        # Log('Feedback Display - Display Power - Hardware: {}, State: {}'.format(HwID, state))
        dest = self.Destinations[HwID]
        StateMap = \
            {
                'On': ['On', 'on', 'Power On'],
                'Off': ['Off', 'off', 'Power Off', 'Standby (Power Save)', 'Suspend (Power Save)'],
                'Warming': ['Warming', 'Warming up'],
                'Cooling': ['Cooling', 'Cooling down']
            }
        if state in StateMap['On']:
            # Log('Show button state On')
            self.__Controls[dest['hw_type']][dest['ctl_group']]['On'].SetState(1)
            self.__Controls[dest['hw_type']][dest['ctl_group']]['Off'].SetState(0)
        elif state in StateMap['Off']:
            # Log('Show button state Off')
            self.__Controls[dest['hw_type']][dest['ctl_group']]['On'].SetState(0)
            self.__Controls[dest['hw_type']][dest['ctl_group']]['Off'].SetState(1)
        elif state in StateMap['Warming']:
            # Log('Show button state Warming')
            self.__Controls[dest['hw_type']][dest['ctl_group']]['On'].SetBlinking('Medium', [0,1])
            self.__Controls[dest['hw_type']][dest['ctl_group']]['Off'].SetState(0)
        elif state in StateMap['Cooling']:
            # Log('Show button state Cooling')
            self.__Controls[dest['hw_type']][dest['ctl_group']]['On'].SetState(0)
            self.__Controls[dest['hw_type']][dest['ctl_group']]['Off'].SetBlinking('Medium', [0,1])
        else:
            raise ValueError('An unexpected state value has been provided - {}'.format(state))
        
    def DisplayMuteFeedback(self, HwID: str, state: Union[str, int, bool]):
        # Log('Feedback Display - Display Mute - Hardware: {}, State: {}'.format(HwID, state))
        dest = self.Destinations[HwID]
        if state in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE']:
            self.__Controls[dest['hw_type']][dest['ctl_group']]['Mute'].SetState(1)
            dest['mute'] = True
        else:
            self.__Controls[dest['hw_type']][dest['ctl_group']]['Mute'].SetState(0)
            dest['mute'] = False
            
    def DisplayVolumeFeedback(self, HwID: str, value: int):
        # Log('Feedback Display - Display Volume - Hardware: {}, Value: {}'.format(HwID, value))
        dest = self.Destinations[HwID]
        dest['volume'] = int(value)
        self.__Controls[dest['hw_type']][dest['ctl_group']]['Vol'].SetFill(int(value))


## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------