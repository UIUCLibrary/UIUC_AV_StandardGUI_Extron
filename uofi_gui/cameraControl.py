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
                #cam.update({'Hw', vars.Hardware[cam['Id']]})
                cam['Hw'] = vars.Hardware[cam['Id']]
                #self.Cameras.update({cam['Id']: cam})
                self.Cameras[cam['Id']] = cam
            else:
                raise KeyError('No hardware item found for Camera Id ({})'.format(cam['id']))
        
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
        
        # TODO: figure out if we can persist preset names through a reboot
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
                utilityFunctions.Log('Cam Info: {}'.format(cam))
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
            utilityFunctions.Log('JSON Obj: {}'.format(presetObj))
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
    
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



