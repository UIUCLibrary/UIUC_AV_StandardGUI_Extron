## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

print(Version()) ## Sanity check ControlScript Import
## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
from datetime import datetime
import json
import re
from typing import Dict, Tuple, List, Callable, Union
import functools

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
import utilityFunctions
import settings
import vars

import uofi_gui.systemHardware as SysHW
from uofi_gui.sourceControls import Destination as Dest

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class CameraController:
    def __init__(self, UIHost: UIDevice, SelectionSet: MESet, PresetList: List, ControlsList: List, EditorDict: Dict, CamSwitcher: Union[SysHW.SystemHardwareController, str]) -> None:
        self.__presetsFilePath = '/user/states/camera_presets.json'
        self.UIHost = UIHost
        self.Cameras = {}
        for cam in settings.cameras:
            if cam['Id'] in vars.Hardware:
                cam['Hw'] = vars.Hardware[cam['Id']]
                self.Cameras[cam['Id']] = cam
            else:
                raise KeyError('No hardware item found for Camera Id ({})'.format(cam['Id']))
        
        if type(CamSwitcher) is SysHW.SystemHardwareController:
            self.__switcher = CamSwitcher
        elif type(CamSwitcher) is str:
            if CamSwitcher in vars.Hardware:
                self.__switcher = vars.Hardware[CamSwitcher]
            else:
                raise KeyError('No hardware item found for Switcher Id ({})'.format(CamSwitcher))
        else:
            raise TypeError("CamSwitcher must either be a SystemHardwareController object or string Id")
        
        self.__defaultCamera = None
        self.__selectBtns = SelectionSet
        for selBtn in self.__selectBtns.Objects:
            re_match = re.match(r'Ctl-Camera-Select-(\w+)', selBtn.Name)
            camId = re_match.group(1)
            if camId in self.Cameras:
                selBtn.camera = self.Cameras[camId]
                selBtn.camName = selBtn.camera['Name']
                selBtn.SetText(selBtn.camera['Name'])
            if camId == settings.defaultCamera:
                self.__defaultCamera = selBtn
        
        @event(self.__selectBtns.Objects, ['Pressed', 'Released'])
        def camSelectBtnHandler(button, action):
            if action == 'Pressed':
                self.__selectBtns.SetCurrent(button)
            elif action == 'Released':
                if 'qualifier' in self.__switcher.SwitchCommand:
                    qual = self.__switcher.SwitchCommand['qualifier']
                else:
                    qual = None
                utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(self.__switcher.SwitchCommand['command'], str(selBtn.camera['Input']), qual))
                #self.__switcher.interface.Set(self.__switcher.SwitchCommand['command'], str(selBtn.camera['Input']), qual)
                
                self.UpdatePresetButtons()
        
        self.__presetBtns = PresetList
        for preBtn in self.__presetBtns:
            re_match = re.match(r'Ctl-Camera-Preset-(\d+)', preBtn.Name)
            defaultBtnText = 'Preset {}'.format(re_match.group(1))
            preBtn.defaultText = defaultBtnText
            preBtn.PresetValue = int(re_match.group(1))
            preBtn.SetText(defaultBtnText)
            
        @event(self.__presetBtns, ['Pressed', 'Tapped', 'Held'])
        def presetBtnHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Tapped':
                button.SetState(0)
                camHW = self.__selectBtns.GetCurrent().camera['Hw']
                if 'qualifier' in camHW.PresetRecallCommand:
                    qual = camHW.PresetRecallCommand['qualifier']
                else:
                    qual = None
                utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetRecallCommand['command'], str(button.PresetValue), qual))
                #camHW.interface.Set(camHW.PresetRecallCommand['command'], str(button.PresetValue), qual)
            elif action == 'Held':
                button.SetState(0)
                camHW = self.__selectBtns.GetCurrent().camera['Hw']
                PresetName = button.defaultText
                if button.PresetValue in camHW.Presets:
                    PresetName = camHW.Presets[button.PresetValue]
                self.__editor_Name.SetText(PresetName)
                self.__editor_Name.PresetText = PresetName
                self.__editor_Name.PresetValue = button.PresetValue
                self.__editor_Title.SetText("Editing {cam}: {preset}".format(cam=camHW.Name, preset=button.defaultText))
                self.UIHost.ShowPopup('CameraPresetEditor')
        
        self.__homeBtn = vars.TP_Btns['Ctl-Camera-Home']
        self.__homeBtn.PresetValue = 0
        
        @event(self.__homeBtn, ['Pressed', 'Tapped', 'Held'])
        def homeBtnHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Tapped':
                button.SetState(0)
                camHW = self.__selectBtns.GetCurrent().camera['Hw']
                if 'qualifier' in camHW.PresetRecallCommand:
                    qual = camHW.PresetRecallCommand['qualifier']
                else:
                    qual = None
                #camHW.interface.Set(camHW.PresetRecallCommand['command'], str(button.PresetValue), qual)
            elif action == 'Held':
                button.SetState(0)
                camHW = self.__selectBtns.GetCurrent().camera['Hw']
                if 'qualifier' in camHW.PresetSaveCommand:
                    qual = camHW.PresetSaveCommand['qualifier']
                else:
                    qual = None
                #camHW.interface.Set(camHW.PresetSaveCommand['command'], str(self.__editor_Name.PresetValue), qual)
                self.UIHost.Click(3, 0.25)
                
        
        self.__controlsBtns = ControlsList
        for ctlBtn in self.__controlsBtns:
            re_match = re.match(r'Ctl-Camera-([TPZ])-(Up|Dn|L|R|In|Out)', ctlBtn.Name)
            ctlBtn.moveMode = re_match.group(1)
            ctlBtn.moveDir = re_match.group(2)
        
        @event(self.__controlsBtns, ['Pressed', 'Released'])
        def camCtlHandler(button, action):
            camHW = self.__selectBtns.GetCurrent().camera['Hw']
            if action == 'Pressed':
                button.SetState(1)
                if button.moveMode == 'P' or button.moveMode == 'T': # Pan & Tilt
                    if button.moveDir == 'L': # Pan Left
                        if 'qualifier' in camHW.PTCommand:
                            qual = camHW.PTCommand['qualifier']
                        else:
                            qual = None
                        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Left', qual))
                        #camHW.interface.Set(camHW.PTCommand['command'], 'Left', qual)
                    elif button.moveDir == 'R': # Pan Right
                        if 'qualifier' in camHW.PTCommand:
                            qual = camHW.PTCommand['qualifier']
                        else:
                            qual = None
                        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Right', qual))
                        #camHW.interface.Set(camHW.PTCommand['command'], 'Right', qual)
                    elif button.moveDir == 'Up': # Tilt Up
                        if 'qualifier' in camHW.PTCommand:
                            qual = camHW.PTCommand['qualifier']
                        else:
                            qual = None
                        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Up', qual))
                        #camHW.interface.Set(camHW.PTCommand['command'], 'Up', qual)
                    elif button.moveDir == 'Dn': # Tilt Down
                        if 'qualifier' in camHW.PTCommand:
                            qual = camHW.PTCommand['qualifier']
                        else:
                            qual = None
                        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Down', qual))
                        #camHW.interface.Set(camHW.PTCommand['command'], 'Down', qual)
                elif button.moveMode == 'Z': # Zoom
                    if button.moveMode == 'In': # Zoom In
                        if 'qualifier' in camHW.ZCommand:
                            qual = camHW.ZCommand['qualifier']
                        else:
                            qual = None
                        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.ZCommand['command'], 'Tele', qual))
                        #camHW.interface.Set(camHW.ZCommand['command'], 'Tele', qual)
                    elif button.moveMode == 'Out': # Zoom Out
                        if 'qualifier' in camHW.ZCommand:
                            qual = camHW.ZCommand['qualifier']
                        else:
                            qual = None
                        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.ZCommand['command'], 'Wide', qual))
                        #camHW.interface.Set(camHW.ZCommand['command'], 'Wide', qual)
            elif action == 'Released':
                button.SetState(0)
                if button.moveMode == 'P' or button.moveMode == 'T': # Pan & Tilt
                    if 'qualifier' in camHW.PTCommand:
                        qual = camHW.PTCommand['qualifier']
                    else:
                        qual = None
                    utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Stop', qual))
                    #camHW.interface.Set(camHW.PTCommand['command'], 'Stop', qual)
                elif button.moveMode == 'Z': # Zoom
                    if 'qualifier' in camHW.ZCommand:
                        qual = camHW.ZCommand['qualifier']
                    else:
                        qual = None
                    utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.ZCommand['command'], 'Stop', qual))
                    #camHW.interface.Set(camHW.ZCommand['command'], 'Stop', qual)
        
        self.__editor_Title = EditorDict['Title']
        self.__editor_Name = EditorDict['DisplayName']
        @event(self.__editor_Name, ['Pressed', 'Released'])
        def editorNameHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                camHW = self.__selectBtns.GetCurrent().camera['Hw']
                PresetName = ''
                if button.PresetValue in camHW.Presets:
                    PresetName = camHW.Presets[button.PresetValue]
                vars.KBCtl.Open(PresetName, functools.partial(self.UpdatePreset, NameBtn=button))
                button.SetState(0)
        
        self.__editor_Home = EditorDict['Home']
        @event(self.__editor_Home, ['Pressed', 'Released'])
        def editorHomeHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                camHW = self.__selectBtns.GetCurrent().camera['Hw']
                if 'qualifier' in camHW.PresetRecallCommand:
                    qual = camHW.PresetRecallCommand['qualifier']
                else:
                    qual = None
                utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetRecallCommand['command'], str(0), qual))
                #camHW.interface.Set(camHW.PresetRecallCommand['command'], str(0), qual)
                button.SetState(0)
        
        self.__editor_Save = EditorDict['Save']
        @event(self.__editor_Save, ['Pressed', 'Released'])
        def editorSaveHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                camHW = self.__selectBtns.GetCurrent().camera['Hw']
                if 'qualifier' in camHW.PresetSaveCommand:
                    qual = camHW.PresetSaveCommand['qualifier']
                else:
                    qual = None
                camHW.Presets[self.__editor_Name.PresetValue] = self.__editor_Name.PresetText
                utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetSaveCommand['command'], str(self.__editor_Name.PresetValue), qual))
                #camHW.interface.Set(camHW.PresetSaveCommand['command'], str(self.__editor_Name.PresetValue), qual)
                button.SetState(0)
                self.UpdatePresetButtons()
                self.UIHost.HidePopup('CameraPresetEditor')
                self.SavePresetStates()
        
        self.__editor_Cancel = EditorDict['Cancel']
        @event(self.__editor_Cancel, ['Pressed', 'Released'])
        def editorCancelHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                self.UIHost.HidePopup('CameraPresetEditor')
                
        
        self.LoadPresetStates()
        self.SelectDefaultCamera()

    def SavePresetStates(self):
        # only need to save the preset names, presets are stored presistently on camera
        if File.Exists(self.__presetsFilePath):
            # file exists -> read file to object, modify object, save object to file
            #### read file to object
            presetsFile = File(self.__presetsFilePath, 'rt')
            presetString = presetsFile.read()
            presetObj = json.loads(presetString)
            presetsFile.close()
            
            #### modify object
            for cam in self.Cameras.values():
                if cam['Id'] not in presetObj:
                    presetObj[cam['Id']] = {}
                    
                for i in range(1, 4): # Preset 0 is home, Presets 1-3 are displayed buttons
                    if i in cam['Hw'].Presets:
                        presetObj[cam['Id']][i] = cam['Hw'].Presets[i]
                    else:
                        presetObj[cam['Id']][i] = None
            
            #### save object to file
            presetsFile = File(self.__presetsFilePath, 'wt')
            presetsFile.write(json.dumps(presetObj))
            presetsFile.close()
        else:
            # file does not exist -> create object, save object to file
            #### create object
            presetObj = {}
            
            for cam in self.Cameras.values():
                # utilityFunctions.Log('Cam Info: {}'.format(cam))
                presetObj[cam['Id']] = {}
                
                for i in range(1, 4): # Preset 0 is home, Presets 1-3 are displayed buttons
                    if i in cam['Hw'].Presets:
                        presetObj[cam['Id']][i] = cam['Hw'].Presets[i]
                    else:
                        presetObj[cam['Id']][i] = None
            
            #### save object to file
            presetsFile = File(self.__presetsFilePath, 'xt')
            presetsFile.write(json.dumps(presetObj))
            presetsFile.close()
    
    def LoadPresetStates(self):
        # only need to load the preset names, presets are stored presistently on camera
        if File.Exists(self.__presetsFilePath):
            #### read file to object
            presetsFile = File(self.__presetsFilePath, 'rt')
            presetString = presetsFile.read()
            presetObj = json.loads(presetString)
            # utilityFunctions.Log('JSON Obj: {}'.format(presetObj))
            presetsFile.close()
            
            #### iterate over objects and load presets
            for cam in self.Cameras.values():
                if cam['Id'] in presetObj:
                    for i in presetObj[cam['Id']]:
                        # watch the typing here, rest of module expects i to be an int but i is a string in presetObj
                        if presetObj[cam['Id']][str(i)] is not None:
                            cam['Hw'].Presets[int(i)] = presetObj[cam['Id']][str(i)]
            
        else:
            utilityFunctions.Log('No presets file exists')
    
    def UpdatePreset(self, PresetName, NameBtn):
        NameBtn.PresetText = PresetName
        NameBtn.SetText(PresetName)
    
    def UpdatePresetButtons(self):
        camHW = self.__selectBtns.GetCurrent().camera['Hw']
        for presetBtn in self.__presetBtns:
            PresetName = presetBtn.defaultText
            if presetBtn.PresetValue in camHW.Presets:
                PresetName = camHW.Presets[presetBtn.PresetValue]
            presetBtn.SetText(PresetName)
    
    def SelectDefaultCamera(self):
        self.__selectBtns.SetCurrent(self.__defaultCamera)
        input = self.__defaultCamera.camera['Input']
        if 'qualifier' in self.__switcher.SwitchCommand:
            qual = self.__switcher.SwitchCommand['qualifier']
        else: 
            qual = None
            
        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(self.__switcher.SwitchCommand['command'], str(input), qual))
        #self.__switcher.interface.Set(self.__switcher.SwitchCommand['command'], str(input), qual)
        self.UpdatePresetButtons()
        
    def SendCameraHome(self, camera: Union[SysHW.SystemHardwareController, str]=None): 
        if camera is None:
            for cam in settings.cameras:
                if cam['Id'] in vars.Hardware:
                    camHW = vars.Hardware[cam['Id']]
                    if 'qualifier' in camHW.PresetRecallCommand:
                        qual = camHW.PresetRecallCommand['qualifier']
                    else:
                        qual = None
                    
                    utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetRecallCommand['command'], str(0), qual))
                    #camHW.interface.Set(camHW.PresetRecallCommand['command'], str(0), qual)
        else:
            if type(camera) is SysHW.SystemHardwareController:
                camHW = camera
            elif type(camera) is str:
                if camera in vars.Hardware:
                    camHW = vars.Hardware[camera]
                else:
                    raise KeyError('No hardware item found for Switcher Id ({})'.format(camera))
                
            if 'qualifier' in camHW.PresetRecallCommand:
                qual = camHW.PresetRecallCommand['qualifier']
            else:
                qual = None
            utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetRecallCommand['command'], str(0), qual))
            #camHW.interface.Set(camHW.PresetRecallCommand['command'], str(0), qual)
    
class DisplayController:
    def __init__(self, UIHost: UIDevice) -> None:
        self.UIHost = UIHost
        
        self.__labels = \
            {
                'conf': {},
                'proj': {},
                'scn': {},
                'mon': {}
            }
        self.__controls = {}
        for k in self.__labels:
            self.__labels[k] = utilityFunctions.DictValueSearchByKey(vars.TP_Lbls, r'DisplayCtl-{}-(\d+)'.format(k), regex=True, capture_dict=True)
            if k != 'scn':  
                self.__controls[k] = {}
                for i in range(1, len(self.__labels[k])+1):
                    self.__controls[k][str(i)] = utilityFunctions.DictValueSearchByKey(vars.TP_Btns, r'Tech-Display-{}-{}-(\w+)'.format(k, str(i)), regex=True, capture_dict=True)
                    if k == 'proj':
                        self.__controls[k][str(i)].update(utilityFunctions.DictValueSearchByKey(vars.TP_Btns, r'Tech-Display-scn-{}-(\w+)'.format(str(i)), regex=True, capture_dict=True))
                    if k == 'mon':
                        self.__controls[k][str(i)].update({'Vol': vars.TP_Slds['Tech-Display-mon-{}-Vol'.format(str(i))]})
        # self.__controls[hw_type][ctl_group][ctl_type] = button
        
        self.Destinations = {}
        conf_assign = 1
        mon_assign = 1
        proj_assign = 1
        for dest in settings.destinations:
            self.Destinations[dest['id']] = dest
            self.Destinations[dest['id']]['hw'] = (vars.Hardware[dest['id']] if dest['id'] in vars.Hardware else None)
            
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
                    self.Destinations[dest['id']]['Scn']['up'] = RelayInterface(vars.CtlProc_Main, 'RLY{}'.format(self.Destinations[dest['id']]['rly'][0]))
                    self.Destinations[dest['id']]['Scn']['up'].SetState('Open')
                else:
                    # TODO: figure out standardization for relays attached to devices other than the main control processor
                    pass
                if type(self.Destinations[dest['id']]['rly'][1]) is int:
                    self.Destinations[dest['id']]['Scn']['dn'] = RelayInterface(vars.CtlProc_Main, 'RLY{}'.format(self.Destinations[dest['id']]['rly'][1]))
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
                utilityFunctions.Log('Display Control - Hardware: {} ({}), CtlType: {}, HwType: {}'.format(control.DestID, control.CtlGroup, control.CtlType, control.HwType))
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
                    # utilityFunctions.Log('Pulse Up Relay')
                    @Wait(3)
                    def delayFeedbackHandler():
                        control.SetState(0)
                elif control.CtlType == 'Dn':
                    # send screen down
                    self.Destinations[control.DestID]['Scn']['dn'].Pulse(2)
                    # utilityFunctions.Log('Pulse Down Relay')
                    @Wait(3)
                    def delayFeedbackHandler():
                        control.SetState(0)
                elif control.CtlType == 'Stop':
                    # send screen stop
                    # This assumes that the screen stop command is to close both the up and down contact closures
                    self.Destinations[control.DestID]['Scn']['up'].Pulse(2)
                    self.Destinations[control.DestID]['Scn']['dn'].Pulse(2)
                    # utilityFunctions.Log('Pulse Up & Down Relays')
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
                    # utilityFunctions.Log('Slider - new value = {}'.format(value))
                    # set display volume
                    self.DisplayVolume(control.DestID, value)
                    control.SetFill(value)

    def DisplayPower(self, dest, state: str='On'):
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Dest:
            Hw = dest['hw'] # TEST: make sure this notation works
        
        if 'qualifier' in Hw.PowerCommand:
            qual = Hw.PowerCommand['qualifier']
        else:
            qual = None
        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.PowerCommand['command'], state, qual))
        Hw.interface.Set(Hw.PowerCommand['command'], state, qual)
    
    def DisplaySource(self, dest):
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Dest:
            Hw = dest['hw'] # TEST: make sure this notation works
        
        if 'qualifier' in Hw.SourceCommand:
            qual = Hw.SourceCommand['qualifier']
        else:
            qual = None
        if 'value' in Hw.SourceCommand:
            state = Hw.SourceCommand['value']
        else:
            raise KeyError('Display source value not found for {}'.format(dest))
        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.SourceCommand['command'], state, qual))
        Hw.interface.Set(Hw.SourceCommand['command'], state, qual)
        
    def DisplayMute(self, dest, state):
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Dest:
            Hw = dest['hw'] # TEST: make sure this notation works
            
        if 'qualifier' in Hw.MuteCommand:
            qual = Hw.MuteCommand['qualifier']
        else:
            qual = None
        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.MuteCommand['command'], state, qual))
        Hw.interface.Set(Hw.MuteCommand['command'], state, qual)
    
    def DisplayVolume(self, dest, value):
        if type(dest) is str:
            Hw = self.Destinations[dest]['hw']
        elif type(dest) is Dest:
            Hw = dest['hw'] # TEST: make sure this notation works
            
        if 'qualifier' in Hw.VolumeCommand:
            qual = Hw.VolumeCommand['qualifier']
        else:
            qual = None
        utilityFunctions.Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(Hw.VolumeCommand['command'], value, qual))
        Hw.interface.Set(Hw.VolumeCommand['command'], int(value), qual)
        
    def DisplayPowerFeedback(self, HwID: str, state: str):
        # utilityFunctions.Log('Feedback Display - Display Power - Hardware: {}, State: {}'.format(HwID, state))
        dest = self.Destinations[HwID]
        StateMap = \
            {
                'On': ['On', 'on', 'Power On'],
                'Off': ['Off', 'off', 'Power Off', 'Standby (Power Save)', 'Suspend (Power Save)'],
                'Warming': ['Warming', 'Warming up'],
                'Cooling': ['Cooling', 'Cooling down']
            }
        if state in StateMap['On']:
            # utilityFunctions.Log('Show button state On')
            self.__controls[dest['hw_type']][dest['ctl_group']]['On'].SetState(1)
            self.__controls[dest['hw_type']][dest['ctl_group']]['Off'].SetState(0)
        elif state in StateMap['Off']:
            # utilityFunctions.Log('Show button state Off')
            self.__controls[dest['hw_type']][dest['ctl_group']]['On'].SetState(0)
            self.__controls[dest['hw_type']][dest['ctl_group']]['Off'].SetState(1)
        elif state in StateMap['Warming']:
            # utilityFunctions.Log('Show button state Warming')
            self.__controls[dest['hw_type']][dest['ctl_group']]['On'].SetBlinking('Medium', [0,1])
            self.__controls[dest['hw_type']][dest['ctl_group']]['Off'].SetState(0)
        elif state in StateMap['Cooling']:
            # utilityFunctions.Log('Show button state Cooling')
            self.__controls[dest['hw_type']][dest['ctl_group']]['On'].SetState(0)
            self.__controls[dest['hw_type']][dest['ctl_group']]['Off'].SetBlinking('Medium', [0,1])
        else:
            raise ValueError('An unexpected state value has been provided - {}'.format(state))
        
    def DisplayMuteFeedback(self, HwID: str, state: str):
        # utilityFunctions.Log('Feedback Display - Display Mute - Hardware: {}, State: {}'.format(HwID, state))
        dest = self.Destinations[HwID]
        if state == 'On':
            self.__controls[dest['hw_type']][dest['ctl_group']]['Mute'].SetState(1)
        elif state == 'Off':
            self.__controls[dest['hw_type']][dest['ctl_group']]['Mute'].SetState(0)
            
    def DisplayVolumeFeedback(self, HwID: str, value: int):
        # utilityFunctions.Log('Feedback Display - Display Volume - Hardware: {}, Value: {}'.format(HwID, value))
        dest = self.Destinations[HwID]
        self.__controls[dest['hw_type']][dest['ctl_group']]['Vol'].SetFill(int(value))
        
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



