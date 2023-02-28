# from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING:
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from uofi_gui.sourceControls import Destination
    from extronlib.ui import Button, Knob, Label, Level, Slider
    
## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.system import Wait
from extronlib.interface import RelayInterface

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class DisplayController:
    def __init__(self, UIHost: ExUIDevice) -> None:
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        
        self.__labels = \
            {
                'conf': {},
                'proj': {},
                'scn': {},
                'mon': {}
            }
        self.__controls = {}
        for k in self.__labels:
            self.__labels[k] = DictValueSearchByKey(self.UIHost.Lbls, r'DisplayCtl-{}-(\d+)'.format(k), regex=True, capture_dict=True)
            if k != 'scn':  
                self.__controls[k] = {}
                for i in range(1, len(self.__labels[k])+1):
                    self.__controls[k][str(i)] = DictValueSearchByKey(self.UIHost.Btns, r'Tech-Display-{}-{}-(\w+)'.format(k, str(i)), regex=True, capture_dict=True)
                    if k == 'proj':
                        self.__controls[k][str(i)].update(DictValueSearchByKey(self.UIHost.Btns, r'Tech-Display-scn-{}-(\w+)'.format(str(i)), regex=True, capture_dict=True))
                    if k == 'mon':
                        self.__controls[k][str(i)].update({'Vol': self.UIHost.Slds['Tech-Display-mon-{}-Vol'.format(str(i))]})
        # self.__controls[hw_type][ctl_group][ctl_type] = button
        
        self.Destinations = {}
        conf_assign = 1
        mon_assign = 1
        proj_assign = 1
        for dest in self.GUIHost.Destinations:
            self.Destinations[dest['id']] = dest
            self.Destinations[dest['id']]['hw'] = self.GUIHost.Hardware.get(dest['id'], None)
            
            if dest['type'] == 'conf':
                self.Destinations[dest['id']]['hw_type'] = 'conf'
                self.Destinations[dest['id']]['ctl_group'] = str(conf_assign)
                self.__labels['conf'][str(conf_assign)].SetText(dest['name'])
                for key, ctl in self.__controls['conf'][str(conf_assign)].items():
                    if key == 'Src':
                        ctl.SetEnable(False)
                        ctl.SetVisible(False)
                    else:
                        ctl.DestID = dest['id']
                        if key == 'On' or key == 'Off':
                            ctl.ConfControlType = 'switcher'
                conf_assign += 1
            elif dest['type'] == 'c-conf':
                self.Destinations[dest['id']]['hw_type'] = 'conf'
                self.Destinations[dest['id']]['ctl_group'] = str(conf_assign)
                self.__labels['conf'][str(conf_assign)].SetText(dest['name'])
                for key, ctl in self.__controls['conf'][str(conf_assign)].items():
                    ctl.DestID = dest['id']
                    if key == 'On' or key == 'Off':
                        ctl.ConfControlType = 'display'
                conf_assign += 1
            elif dest['type'] == 'mon':
                self.Destinations[dest['id']]['hw_type'] = 'mon'
                self.Destinations[dest['id']]['ctl_group'] = str(mon_assign)
                self.__labels['mon'][str(mon_assign)].SetText(dest['name'])
                for key, ctl in self.__controls['mon'][str(mon_assign)].items():
                    ctl.DestID = dest['id']
                    # Set range for monitor volume slider based on hardware options
                    if key == 'Vol' and hasattr(self.Destinations[dest['id']]['hw'], 'VolumeRange'):
                        ctl.SetRange(*self.Destinations[dest['id']]['hw'].VolumeRange)
                mon_assign += 1
            elif dest['type'] == 'proj':
                self.Destinations[dest['id']]['hw_type'] = 'proj'
                self.Destinations[dest['id']]['ctl_group'] = str(proj_assign)
                self.__labels['proj'][str(proj_assign)].SetText(dest['name'])
                self.__labels['scn'][str(proj_assign)].SetVisibe(False)
                for key, ctl in self.__controls['proj'][str(proj_assign)].items():
                    if key == 'Stop' or key == 'Up' or key == 'Dn':
                        ctl.SetEnable(False)
                        ctl.SetVisible(False)
                    else:
                        ctl.DestID = dest['id']
                proj_assign += 1
            elif dest['type'] == 'proj+scn':
                self.Destinations[dest['id']]['hw_type'] = 'proj'
                self.Destinations[dest['id']]['ctl_group'] = str(proj_assign)
                self.__labels['proj'][str(proj_assign)].SetText(dest['name'])
                self.__labels['scn'][str(proj_assign)].SetText('{} Screen'.format(dest['name']))
                for ctl in self.__controls['proj'][str(proj_assign)].values():
                    ctl.DestID = dest['id']
                    
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
        
        self.__control_list = []
        for hw_type, group_dict in self.__controls.items():
            for group, ctl_dict in group_dict.items():
                for ctl_type, ctl in ctl_dict.items():
                    ctl.CtlType = ctl_type
                    ctl.HwType = hw_type
                    ctl.CtlGroup = group
                    self.__control_list.append(ctl)
        
        @event([ctl for ctl in self.__control_list if type(ctl) is Slider], ['Changed'])
        def sliderFillHandler(control, action, value):
            if type(control) == Slider:
                control.SetFill(value)
        
        @event(self.__control_list, ['Pressed', 'Released'])
        def displayControlButtonHandler(control, action, value=None):
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
                Log('Display Control - Hardware: {} ({}), CtlType: {}, HwType: {}'.format(control.DestID, control.CtlGroup, control.CtlType, control.HwType))
                if control.CtlType == 'On':
                    # set display on, clear off button state
                    if control.HwType == 'conf' and control.ConfControlType == 'switcher':
                        # TODO: do on/off with switcher output
                        pass
                    else:
                        self.DisplayPower(control.DestID, 'On')
                    self.__controls[control.HwType][control.CtlGroup]['Off'].SetState(0)
                    control.SetBlinking('Medium', [0,1])
                elif control.CtlType == 'Off':
                    # set display off, clear on button state
                    if control.HwType == 'conf' and control.ConfControlType == 'switcher':
                        # TODO: do on/off with switcher output
                        pass
                    else:
                        self.DisplayPower(control.DestID, 'Off')
                    self.__controls[control.HwType][control.CtlGroup]['On'].SetState(0)
                    control.SetBlinking('Medium', [0,1])
                elif control.CtlType == 'Src':
                    # set display back to default input source
                    self.DisplaySource(control.DestID)
                    @Wait(3)
                    def delayFeedbackHandler():
                        control.SetState(0)
                elif control.CtlType == 'Up':
                    # send screen up
                    self.Destinations[control.DestID]['Scn']['up'].Pulse(2)
                    # Log('Pulse Up Relay')
                    @Wait(3)
                    def delayFeedbackHandler():
                        control.SetState(0)
                elif control.CtlType == 'Dn':
                    # send screen down
                    self.Destinations[control.DestID]['Scn']['dn'].Pulse(2)
                    # Log('Pulse Down Relay')
                    @Wait(3)
                    def delayFeedbackHandler():
                        control.SetState(0)
                elif control.CtlType == 'Stop':
                    # send screen stop
                    # This assumes that the screen stop command is to close both the up and down contact closures
                    self.Destinations[control.DestID]['Scn']['up'].Pulse(2)
                    self.Destinations[control.DestID]['Scn']['dn'].Pulse(2)
                    # Log('Pulse Up & Down Relays')
                    @Wait(3)
                    def delayFeedbackHandler():
                        control.SetState(0)
                elif control.CtlType == 'Mute':
                    # set display mute toggle - button state has been changed to the approprate mute state
                    if control.State:
                        self.DisplayMute(control.DestID, 'On')
                    else:
                        self.DisplayMute(control.DestID, 'Off')
                elif control.CtlType == 'Vol':
                    # Log('Slider - new value = {}'.format(value))
                    # set display volume
                    self.DisplayVolume(control.DestID, value)
                    control.SetFill(value)

    def DisplayPower(self, dest, state: str='On'):
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Destination:
            Hw = dest['hw'] # TEST: make sure this notation works
        
        if 'qualifier' in Hw.PowerCommand:
            qual = Hw.PowerCommand['qualifier']
        else:
            qual = None
        Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.PowerCommand['command'], state, qual))
        Hw.interface.Set(Hw.PowerCommand['command'], state, qual)
    
    def DisplaySource(self, dest):
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Destination:
            Hw = dest['hw'] # TEST: make sure this notation works
        
        if 'qualifier' in Hw.SourceCommand:
            qual = Hw.SourceCommand['qualifier']
        else:
            qual = None
        if 'value' in Hw.SourceCommand:
            state = Hw.SourceCommand['value']
        else:
            raise KeyError('Display source value not found for {}'.format(dest))
        Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.SourceCommand['command'], state, qual))
        Hw.interface.Set(Hw.SourceCommand['command'], state, qual)
        
    def DisplayMute(self, dest, state):
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Destination:
            Hw = dest['hw'] # TEST: make sure this notation works
            
        if 'qualifier' in Hw.MuteCommand:
            qual = Hw.MuteCommand['qualifier']
        else:
            qual = None
        Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.MuteCommand['command'], state, qual))
        Hw.interface.Set(Hw.MuteCommand['command'], state, qual)
    
    def DisplayVolume(self, dest, value):
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Destination:
            Hw = dest['hw'] # TEST: make sure this notation works
            
        if 'qualifier' in Hw.VolumeCommand:
            qual = Hw.VolumeCommand['qualifier']
        else:
            qual = None
        Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.VolumeCommand['command'], value, qual))
        Hw.interface.Set(Hw.VolumeCommand['command'], int(value), qual)
        
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
            self.__controls[dest['hw_type']][dest['ctl_group']]['On'].SetState(1)
            self.__controls[dest['hw_type']][dest['ctl_group']]['Off'].SetState(0)
        elif state in StateMap['Off']:
            # Log('Show button state Off')
            self.__controls[dest['hw_type']][dest['ctl_group']]['On'].SetState(0)
            self.__controls[dest['hw_type']][dest['ctl_group']]['Off'].SetState(1)
        elif state in StateMap['Warming']:
            # Log('Show button state Warming')
            self.__controls[dest['hw_type']][dest['ctl_group']]['On'].SetBlinking('Medium', [0,1])
            self.__controls[dest['hw_type']][dest['ctl_group']]['Off'].SetState(0)
        elif state in StateMap['Cooling']:
            # Log('Show button state Cooling')
            self.__controls[dest['hw_type']][dest['ctl_group']]['On'].SetState(0)
            self.__controls[dest['hw_type']][dest['ctl_group']]['Off'].SetBlinking('Medium', [0,1])
        else:
            raise ValueError('An unexpected state value has been provided - {}'.format(state))
        
    def DisplayMuteFeedback(self, HwID: str, state: str):
        # Log('Feedback Display - Display Mute - Hardware: {}, State: {}'.format(HwID, state))
        dest = self.Destinations[HwID]
        if state == 'On':
            self.__controls[dest['hw_type']][dest['ctl_group']]['Mute'].SetState(1)
        elif state == 'Off':
            self.__controls[dest['hw_type']][dest['ctl_group']]['Mute'].SetState(0)
            
    def DisplayVolumeFeedback(self, HwID: str, value: int):
        # Log('Feedback Display - Display Volume - Hardware: {}, Value: {}'.format(HwID, value))
        dest = self.Destinations[HwID]
        self.__controls[dest['hw_type']][dest['ctl_group']]['Vol'].SetFill(int(value))


## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------