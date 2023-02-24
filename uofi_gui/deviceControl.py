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
        i = 1
        for cam in settings.cameras:
            if cam['Id'] in vars.Hardware:
                cam['Hw'] = vars.Hardware[cam['Id']]
                cam['Number'] = i
                self.Cameras[cam['Id']] = cam
                i += 1
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
            re_match = re.match(r'Ctl-Camera-Select-(\d+)', selBtn.Name)
            camNum = int(re_match.group(1))
            cam = [cam for cam in self.Cameras.values() if camNum == cam['Number']][0]
            utilityFunctions.Log('Cam selection: {} ({})'.format(cam, type(cam)))
                    
            if cam['Id'] in self.Cameras:
                selBtn.camera = cam
                selBtn.camName = cam['Name']
                selBtn.SetText(cam['Name'])
            if cam['Id'] == settings.defaultCamera:
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
            self.Destinations[dest['id']]['hw'] = vars.Hardware.get(dest['id'], None)
            
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

class AudioController:
    def __init__(self, UIHost: UIDevice, DSPId: str) -> None:
        self.UIHost = UIHost
        self.DSP = vars.Hardware[DSPId]
        
        self.__step_sm = 1
        self.__step_lg = 3
        
        utilityFunctions.Log('Creating microphones dict')
        self.Microphones = {}
        for mic in settings.microphones:
            self.Microphones[str(mic['Number'])] = mic
            self.Microphones[str(mic['Number'])]['hw'] = vars.Hardware.get(mic['Id'], None)
            self.Microphones[str(mic['Number'])]['mute'] = False
        self.__ProgMute = False
        
        utilityFunctions.Log('Creating levels and controls')
        self.__levels = {'prog': vars.TP_Lvls['Audio-Lvl-Prog'], 'mics': {}}
        self.__levels['prog'].SetRange(self.DSP.Program['Range'][0],
                                       self.DSP.Program['Range'][1],
                                       self.DSP.Program['Step'])
        
        self.__labels = {}
        self.__mic_ctl_list = []
        self.__controls = \
            {
                'prog': 
                    {
                        'up': vars.TP_Btns['Vol-Prog-Up'],
                        'down': vars.TP_Btns['Vol-Prog-Dn'],
                        'mute': vars.TP_Btns['Vol-Prog-Mute']
                    },
                'mics': {},
                'all-mics': vars.TP_Btns['Vol-AllMics-Mute']
            }
        self.__controls['prog']['up'].CtlType = 'up'
        self.__controls['prog']['down'].CtlType = 'down'
        self.__controls['prog']['mute'].CtlType = 'mute'
        
        for i in range(1, len(settings.microphones) + 1):
            utilityFunctions.Log('Creating microphone controls {}'.format(str(i)))
            self.__controls['mics'][str(i)] = \
                {
                    'up': vars.TP_Btns['Vol-Mic-{}-Up'.format(str(i))],
                    'down': vars.TP_Btns['Vol-Mic-{}-Dn'.format(str(i))],
                    'mute': vars.TP_Btns['Vol-Mic-{}-Mute'.format(str(i))]
                }
            self.__controls['mics'][str(i)]['up'].CtlType = 'up'
            self.__controls['mics'][str(i)]['down'].CtlType = 'down'
            self.__controls['mics'][str(i)]['mute'].CtlType = 'mute'
            self.__controls['mics'][str(i)]['up'].MicNum = i
            self.__controls['mics'][str(i)]['down'].MicNum = i
            self.__controls['mics'][str(i)]['mute'].MicNum = i
            self.__mic_ctl_list.extend(list(self.__controls['mics'][str(i)].values()))
            self.__levels['mics'][str(i)] = vars.TP_Lvls['Audio-Lvl-Mic-{}'.format(str(i))]
            self.__levels['mics'][str(i)].SetRange(self.Microphones[str(i)]['Control']['level']['Range'][0],
                                                   self.Microphones[str(i)]['Control']['level']['Range'][1],
                                                   self.Microphones[str(i)]['Control']['level']['Step'])
            self.__labels[str(i)] = vars.TP_Lbls['Aud-Mic-{}'.format(str(i))]
            self.__labels[str(i)].SetText(self.Microphones[str(i)]['Name'])
        
        utilityFunctions.Log('Creating events')
        # Program Buttons
        @event(list(self.__controls['prog'].values()), ['Pressed', 'Released', 'Repeated'])
        def ProgramControlHandler(button, action):
            level = self.__levels['prog']
            
            if action == 'Pressed':
                if button.CtlType == 'mute':
                    self.ProgMuteToggle()
                elif button.CtlType in ['up', 'down']:
                    button.SetState(1)
            elif action == 'Released':
                if button.CtlType in ['up', 'down']:
                    newLevelVal = self.AdjustLevel(level, button.CtlType, 'small')
                    self.ProgLevel(newLevelVal)
                    button.SetState(0)
            elif action == 'Repeated':
                newLevelVal = self.AdjustLevel(level, button.CtlType, 'large')
                self.ProgLevel(newLevelVal)
                
        # Mic Buttons
        @event(self.__mic_ctl_list, ['Pressed', 'Released', 'Repeated'])
        def MicControlHandler(button, action):
            level = self.__levels['mics'][str(button.MicNum)]
            
            if action == 'Pressed':
                if button.CtlType == 'mute':
                    self.MicMuteToggle(str(button.MicNum))
                elif button.CtlType in ['up', 'down']:
                    button.SetState(1)
            elif action == 'Released':
                if button.CtlType in ['up', 'down']:
                    newLevelVal = self.AdjustLevel(level, button.CtlType, 'small')
                    self.MicLevel(str(button.MicNum), newLevelVal)
                    button.SetState(0)
            elif action == 'Repeated':
                newLevelVal = self.AdjustLevel(level, button.CtlType, 'large')
                self.MicLevel(str(button.MicNum), newLevelVal)
                
        # All Mics Mute Button
        @event(self.__controls['all-mics'], ['Pressed'])
        def AllMicsMuteHandler(button, action):
            # utilityFunctions.Log('Original Mute State: {}'.format(self.AllMicsMute))
            self.AllMicsMute = not self.AllMicsMute 
            # utilityFunctions.Log('Updated Mute State: {}'.format(self.AllMicsMute))
    
    @property
    def AllMicsMute(self)->bool:
        test = True
        for mic in self.Microphones.values():
            if not mic['mute']:
                # utilityFunctions.Log('Microphone ({}) not muted'.format(mic['Id']))
                test = False
        return test
    
    @AllMicsMute.setter
    def AllMicsMute(self, state: Union[str, bool]):
        if not (type(state) is bool or (type(state) is str and state in ['on', 'off'])):
            raise TypeError('Mute State must be boolean or "on" or "off"')
        
        if state == True or state == 'on':
            utilityFunctions.Log('Muting all mics')
            state = True
        else:
            utilityFunctions.Log('Unmuting all mics')
            state = False
        
        for numStr in self.Microphones.keys():
            self.MicMute(numStr, state)
    
    def AllMicsMuteButtonState(self):
        if self.AllMicsMute:
            self.__controls['all-mics'].SetBlinking('Medium', [1,2])
        else:
            self.__controls['all-mics'].SetState(0)
    
    def AdjustLevel(self, level, direction: str='up', step: str='small'):
        if step == 'small':
            s = self.__step_sm
        elif step == 'large':
            s = self.__step_lg
        
        if direction == 'up':
            newLevel = level.Level + s
        elif direction == 'down':
            newLevel = level.Level - s
            
        level.SetLevel(newLevel)
        
        return newLevel
    
    def AudioStartUp(self):
        # Set default levels & unmute all sources
        self.__levels['prog'].SetLevel(self.DSP.Program['StartUp'])
        self.ProgLevel(self.DSP.Program['StartUp'])
        
        for numStr, mic in self.Microphones.items():
            self.__levels['mics'][numStr].SetLevel(mic['Control']['level']['StartUp'])
            self.MicLevel(numStr, mic['Control']['level']['StartUp'])
        
        self.ProgMute(False)
        self.AllMicsMute = False
    
    def AudioShutdown(self):
        # Mute all sources
        self.ProgMute(True)
        self.AllMicsMute = True
    
    def ProgMute(self, State: bool=False):
        if type(State) is not bool:
            raise TypeError('State must be an boolean')
        
        btn = self.__controls['prog']['mute']
        hwCmd = self.DSP.ProgramMuteCommand
        qual = hwCmd.get('qualifier', None)
        value = 'On' if State else 'Off'
        
        self.__ProgMute = State
        
        if State:
            btn.SetBlinking('Medium', [1,2])
        else:
            btn.SetState(0)
            
        self.DSP.interface.Set(hwCmd['command'], value, qual)
    
    def ProgMuteToggle(self):
        toggleState = not self.__ProgMute
        self.ProgMute(toggleState)
    
    def ProgLevel(self, Value: int):
        if type(Value) is not int:
            raise TypeError('Value must be an integer')
        
        hwCmd = self.DSP.ProgramLevelCommand
        qual = hwCmd.get('qualifier', None)
        
        self.DSP.interface.Set(hwCmd['command'], Value, qual)
    
    def MicMute(self, MicNum, State: bool=False):
        if type(State) is not bool:
            raise TypeError('State must be an boolean')
        
        mic = self.Microphones[str(MicNum)]
        btn = self.__controls['mics'][str(MicNum)]['mute']
        
        cmd = mic['Control']['mute']
        hw = vars.Hardware[cmd['HwId']]
        hwCmd = getattr(hw, cmd['HwCmd'])
        qual = hwCmd.get('qualifier', None)
        value = 'On' if State else 'Off'
        
        mic['mute'] = State
        
        if State:
            btn.SetBlinking('Medium', [1,2])
        else:
            btn.SetState(0)
        
        hw.interface.Set(hwCmd['command'], value, qual)
        self.AllMicsMuteButtonState()
        
    def MicMuteToggle(self, MicNum):
        toggleState = not self.Microphones[str(MicNum)]['mute']
        self.MicMute(MicNum, toggleState)
    
    def MicLevel(self, MicNum, Value: int):
        if type(Value) is not int:
            raise TypeError('Value must be an integer')
        
        mic = self.Microphones[str(MicNum)]
        cmd = mic['Control']['level']
        hw = vars.Hardware[cmd['HwId']]
        hwCmd = getattr(hw, cmd['HwCmd'])
        qual = hwCmd.get('qualifier', None)
        
        hw.interface.Set(hwCmd['command'], Value, qual)
    
    def AudioLevelFeedback(self, tag: Tuple, value: int):
        # utilityFunctions.Log("Audio Level Feedback - Tag: {}; Value: {}".format(tag, value))
        if tag[0] == 'prog':
            # utilityFunctions.Log('Prog Level Feedback')
            if not (self.__controls[tag[0]]['up'].PressedState or self.__controls[tag[0]]['down'].PressedState):
                self.__levels[tag[0]].SetLevel(int(value))
        elif tag[0] == 'mics':
            # utilityFunctions.Log('Mic Level Feedback')
            if not (self.__controls[tag[0]][tag[1]]['up'].PressedState or self.__controls[tag[0]][tag[1]]['down'].PressedState):
                self.__levels[tag[0]][tag[1]].SetLevel(int(value))
    
    def AudioMuteFeedback(self, tag: Tuple, state: str):
        # utilityFunctions.Log("Audio Mute Feedback - Tag: {}; State: {}".format(tag, state))
        if tag[0] == 'prog':
            # utilityFunctions.Log('Prog Mute Feedback')
            if state in ['On', 'on', 'Muted', 'muted']:
                # utilityFunctions.Log('Prog Mute On')
                if self.__controls[tag[0]]['mute'].BlinkState == 'Not blinking':
                    self.__controls[tag[0]]['mute'].SetBlinking('Medium', [1,2])
                self.__ProgMute = True
            elif state in ['Off', 'off', 'Unmuted', 'unmuted']:
                # utilityFunctions.Log('Prog Mute Off')
                if self.__controls[tag[0]]['mute'].BlinkState == 'Blinking':
                    self.__controls[tag[0]]['mute'].SetState(0)
                self.__ProgMute = False
        elif tag[0] == 'mics':
            # utilityFunctions.Log('Mic {} Mute Feedback'.format(tag[1]))
            if state in ['On', 'on', 'Muted', 'muted']:
                # utilityFunctions.Log('Mic {} Mute On'.format(tag[1]))
                if self.__controls[tag[0]][tag[1]]['mute'].BlinkState == 'Not blinking':
                    self.__controls[tag[0]][tag[1]]['mute'].SetBlinking('Medium', [1,2])
                self.Microphones[tag[1]]['mute'] = True
            elif state in ['Off', 'off', 'Unmuted', 'unmuted']:
                # utilityFunctions.Log('Mic {} Mute On'.format(tag[1]))
                if self.__controls[tag[0]][tag[1]]['mute'].BlinkState == 'Blinking':
                    self.__controls[tag[0]][tag[1]]['mute'].SetState(0)
                self.Microphones[tag[1]]['mute'] = False
            self.AllMicsMuteButtonState()
    
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



