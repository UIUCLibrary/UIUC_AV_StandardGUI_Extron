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
    from extronlib.ui import Button


    
## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.system import File

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
import re
import functools
import json

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from uofi_gui.systemHardware import SystemHardwareController
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class CameraController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:
        self.__PresetsFilePath = '/user/states/camera_presets.json'
        
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        
        self.Cameras = {}
        i = 1
        for cam in self.GUIHost.Cameras:
            if cam['Id'] in self.GUIHost.Hardware:
                cam['Hw'] = self.GUIHost.Hardware[cam['Id']]
                cam['Number'] = i
                self.Cameras[cam['Id']] = cam
                i += 1
            else:
                raise KeyError('No hardware item found for Camera Id ({})'.format(cam['Id']))
        
        if self.GUIHost.CameraSwitcherId is not None:
            self.__Switcher = self.GUIHost.Hardware[self.GUIHost.CameraSwitcherId]
            
            self.__DefaultCamera = None
            self.__SelectBtns = self.UIHost.Btn_Grps['Camera-Select']
            for selBtn in self.__SelectBtns.Objects:
                re_match = re.match(r'Ctl-Camera-Select-(\d+)', selBtn.Name)
                camNum = int(re_match.group(1))
                cam = [cam for cam in self.Cameras.values() if camNum == cam['Number']][0]
                # Log('Cam selection: {} ({})'.format(cam, type(cam)))
                        
                if cam['Id'] in self.Cameras:
                    selBtn.camera = cam
                    selBtn.camName = cam['Name']
                    selBtn.SetText(cam['Name'])
                if cam['Id'] == self.GUIHost.DefaultCameraId:
                    self.__DefaultCamera = selBtn   
        else:
            self.__Switcher = None
            self.__Camera = list(self.Cameras.values())[0]

        
                
        self.__PresetBtns = DictValueSearchByKey(self.UIHost.Btns, r'Ctl-Camera-Preset-\d+', regex=True)
        for preBtn in self.__PresetBtns:
            re_match = re.match(r'Ctl-Camera-Preset-(\d+)', preBtn.Name)
            defaultBtnText = 'Preset {}'.format(re_match.group(1))
            preBtn.defaultText = defaultBtnText
            preBtn.PresetValue = int(re_match.group(1))
            preBtn.SetText(defaultBtnText)
            
        self.__HomeBtn = self.UIHost.Btns['Ctl-Camera-Home']
        self.__HomeBtn.PresetValue = 0
                
        self.__ControlsBtns = DictValueSearchByKey(self.UIHost.Btns, r'Ctl-Camera-[TPZ]-(?:Up|Dn|L|R|In|Out)', regex=True)
        for ctlBtn in self.__ControlsBtns:
            re_match = re.match(r'Ctl-Camera-([TPZ])-(Up|Dn|L|R|In|Out)', ctlBtn.Name)
            ctlBtn.moveMode = re_match.group(1)
            ctlBtn.moveDir = re_match.group(2)
        
        self.__EditorTitle = self.UIHost.Lbls['CameraPreset-Title']
        self.__EditorName = self.UIHost.Btns['CamPreset-Name']
        self.__EditorHome = self.UIHost.Btns['CamPreset-Home']
        self.__EditorSave = self.UIHost.Btns['CamPreset-Save']
        self.__EditorCancel = self.UIHost.Btns['CamPreset-Cancel']
        
        self.LoadPresetStates()
        self.SelectDefaultCamera()
        
        if self.__Switcher is not None:
            @event(self.__SelectBtns.Objects, ['Pressed', 'Released']) # pragma: no cover
            def camSelectBtnHandler(button: 'Button', action: str):
                self.__CamSelectBtnHandler(button, action)
        
        @event(self.__PresetBtns, ['Pressed', 'Tapped', 'Held']) # pragma: no cover
        def presetBtnHandler(button: 'Button', action: str):
            self.__PresetBtnHandler(button, action)
        
        @event(self.__HomeBtn, ['Pressed', 'Tapped', 'Held']) # pragma: no cover
        def homeBtnHandler(button: 'Button', action: str):
            self.__HomeBtnHandler(button, action)
        
        @event(self.__ControlsBtns, ['Pressed', 'Released']) # pragma: no cover
        def camCtlHandler(button: 'Button', action: str):
            self.__CamCtlHandler(button, action)
            
        @event(self.__EditorName, ['Pressed', 'Released']) # pragma: no cover
        def editorNameHandler(button: 'Button', action: str):
            self.__EditorNameHandler(button, action)
            
        @event(self.__EditorHome, ['Pressed', 'Released']) # pragma: no cover
        def editorHomeHandler(button: 'Button', action: str):
            self.__EditorHomeHandler(button, action)
        
        @event(self.__EditorSave, ['Pressed', 'Released']) # pragma: no cover
        def editorSaveHandler(button: 'Button', action: str):
            self.__EditorSaveHandler(button, action)
        
        @event(self.__EditorCancel, ['Pressed', 'Released']) # pragma: no cover
        def editorCancelHandler(button: 'Button', action: str):
            self.__EditorCancelHandler(button, action)
        
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __CamSelectBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            self.__SelectBtns.SetCurrent(button)
        elif action == 'Released':
            qual = self.__Switcher.SwitchCommand.get('qualifier', None)
            Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(self.__Switcher.SwitchCommand['command'], str(button.camera['Input']), qual))
            self.__Switcher.interface.Set(self.__Switcher.SwitchCommand['command'], str(button.camera['Input']), qual)
            
            self.UpdatePresetButtons()
    
    def __PresetBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Tapped':
            button.SetState(0)
            if self.__Switcher is not None:
                camHW = self.__SelectBtns.GetCurrent().camera['Hw']
            else:
                camHW = self.__Camera['Hw']
            qual = camHW.PresetRecallCommand.get('qualifier', None)
            Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetRecallCommand['command'], str(button.PresetValue), qual))
            camHW.interface.Set(camHW.PresetRecallCommand['command'], str(button.PresetValue), qual)
        elif action == 'Held':
            button.SetState(0)
            if self.__Switcher is not None:
                camHW = self.__SelectBtns.GetCurrent().camera['Hw']
            else:
                camHW = self.__Camera['Hw']
            PresetName = button.defaultText
            if button.PresetValue in camHW.Presets:
                PresetName = camHW.Presets[button.PresetValue]
            self.__EditorName.SetText(PresetName)
            self.__EditorName.PresetText = PresetName
            self.__EditorName.PresetValue = button.PresetValue
            self.__EditorTitle.SetText("Editing {cam}: {preset}".format(cam=camHW.Name, preset=button.defaultText))
            self.UIHost.ShowPopup('CameraPresetEditor')
    
    def __HomeBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Tapped':
            button.SetState(0)
            if self.__Switcher is not None:
                camHW = self.__SelectBtns.GetCurrent().camera['Hw']
            else:
                camHW = self.__Camera['Hw']
            qual = camHW.PresetRecallCommand.get('qualifier', None)
            Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetRecallCommand['command'], str(0), qual))
            camHW.interface.Set(camHW.PresetRecallCommand['command'], str(0), qual)
        elif action == 'Held':
            button.SetState(0)
            if self.__Switcher is not None:
                camHW = self.__SelectBtns.GetCurrent().camera['Hw']
            else:
                camHW = self.__Camera['Hw']
            qual = camHW.PresetSaveCommand.get('qualifier', None)
            Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetSaveCommand['command'], str(0), qual))
            camHW.interface.Set(camHW.PresetSaveCommand['command'], str(0), qual)
            self.UIHost.Click(3, 0.25)
    
    def __CamCtlHandler(self, button: 'Button', action: str):
        if self.__Switcher is not None:
            camHW = self.__SelectBtns.GetCurrent().camera['Hw']
        else:
            camHW = self.__Camera['Hw']
        if action == 'Pressed':
            button.SetState(1)
            if button.moveMode == 'P' or button.moveMode == 'T': # Pan & Tilt
                qual = camHW.PTCommand.get('qualifier', None)
                if button.moveDir == 'L': # Pan Left
                    Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Left', qual))
                    camHW.interface.Set(camHW.PTCommand['command'], 'Left', qual)
                elif button.moveDir == 'R': # Pan Right
                    Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Right', qual))
                    camHW.interface.Set(camHW.PTCommand['command'], 'Right', qual)
                elif button.moveDir == 'Up': # Tilt Up
                    Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Up', qual))
                    camHW.interface.Set(camHW.PTCommand['command'], 'Up', qual)
                elif button.moveDir == 'Dn': # Tilt Down
                    Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Down', qual))
                    camHW.interface.Set(camHW.PTCommand['command'], 'Down', qual)
            elif button.moveMode == 'Z': # Zoom
                qual = camHW.ZCommand.get('qualifier', None)
                if button.moveDir == 'In': # Zoom In
                    Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.ZCommand['command'], 'Tele', qual))
                    camHW.interface.Set(camHW.ZCommand['command'], 'Tele', qual)
                elif button.moveDir == 'Out': # Zoom Out
                    Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.ZCommand['command'], 'Wide', qual))
                    camHW.interface.Set(camHW.ZCommand['command'], 'Wide', qual)
        elif action == 'Released':
            button.SetState(0)
            if button.moveMode == 'P' or button.moveMode == 'T': # Pan & Tilt
                qual = camHW.PTCommand.get('qualifier', None)
                Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PTCommand['command'], 'Stop', qual))
                camHW.interface.Set(camHW.PTCommand['command'], 'Stop', qual)
            elif button.moveMode == 'Z': # Zoom
                qual = camHW.ZCommand.get('qualifier', None)
                Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.ZCommand['command'], 'Stop', qual))
                camHW.interface.Set(camHW.ZCommand['command'], 'Stop', qual)
    
    def __EditorNameHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            if self.__Switcher is not None:
                camHW = self.__SelectBtns.GetCurrent().camera['Hw']
            else:
                camHW = self.__Camera['Hw']
            PresetName = ''
            if button.PresetValue in camHW.Presets:
                PresetName = camHW.Presets[button.PresetValue]
            self.UIHost.KBCtl.Open(PresetName, functools.partial(self.UpdatePreset, NameBtn=button))
            button.SetState(0)
    
    def __EditorHomeHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            if self.__Switcher is not None:
                camHW = self.__SelectBtns.GetCurrent().camera['Hw']
            else:
                camHW = self.__Camera['Hw']
            qual = camHW.PresetRecallCommand.get('qualifier', None)
            Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetRecallCommand['command'], str(0), qual))
            camHW.interface.Set(camHW.PresetRecallCommand['command'], str(0), qual)
            button.SetState(0)
    
    def __EditorSaveHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            if self.__Switcher is not None:
                camHW = self.__SelectBtns.GetCurrent().camera['Hw']
            else:
                camHW = self.__Camera['Hw']
            qual = camHW.PresetSaveCommand.get('qualifier', None)
            camHW.Presets[self.__EditorName.PresetValue] = self.__EditorName.PresetText
            Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetSaveCommand['command'], str(self.__EditorName.PresetValue), qual))
            camHW.interface.Set(camHW.PresetSaveCommand['command'], str(self.__EditorName.PresetValue), qual)
            button.SetState(0)
            self.UpdatePresetButtons()
            self.UIHost.HidePopup('CameraPresetEditor')
            self.SavePresetStates()
    
    def __EditorCancelHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            self.UIHost.HidePopup('CameraPresetEditor')
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def SavePresetStates(self):
        # only need to save the preset names, presets are stored presistently on camera
        if File.Exists(self.__PresetsFilePath):
            # file exists -> read file to object, modify object, save object to file
            #### read file to object
            presetsFile = File(self.__PresetsFilePath, 'rt')
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
            presetsFile = File(self.__PresetsFilePath, 'wt')
            presetsFile.write(json.dumps(presetObj))
            presetsFile.close()
        else:
            # file does not exist -> create object, save object to file
            #### create object
            presetObj = {}
            
            for cam in self.Cameras.values():
                # Log('Cam Info: {}'.format(cam))
                presetObj[cam['Id']] = {}
                
                for i in range(1, 4): # Preset 0 is home, Presets 1-3 are displayed buttons
                    if i in cam['Hw'].Presets:
                        presetObj[cam['Id']][i] = cam['Hw'].Presets[i]
                    else:
                        presetObj[cam['Id']][i] = None
            
            #### save object to file
            presetsFile = File(self.__PresetsFilePath, 'xt')
            presetsFile.write(json.dumps(presetObj))
            presetsFile.close()
    
    def LoadPresetStates(self):
        # only need to load the preset names, presets are stored presistently on camera
        if File.Exists(self.__PresetsFilePath):
            #### read file to object
            presetsFile = File(self.__PresetsFilePath, 'rt')
            presetString = presetsFile.read()
            presetObj = json.loads(presetString)
            # Log('JSON Obj: {}'.format(presetObj))
            presetsFile.close()
            
            #### iterate over objects and load presets
            for cam in self.Cameras.values():
                if cam['Id'] in presetObj:
                    for i in presetObj[cam['Id']]:
                        # watch the typing here, rest of module expects i to be an int but i is a string in presetObj
                        if presetObj[cam['Id']][str(i)] is not None:
                            cam['Hw'].Presets[int(i)] = presetObj[cam['Id']][str(i)]
            
        else:
            Log('No presets file exists')
    
    def UpdatePreset(self, PresetName, NameBtn):
        NameBtn.PresetText = PresetName
        NameBtn.SetText(PresetName)
    
    def UpdatePresetButtons(self):
        if self.__Switcher is not None:
            camHW = self.__SelectBtns.GetCurrent().camera['Hw']
        else:
            camHW = self.__Camera['Hw']
        for presetBtn in self.__PresetBtns:
            PresetName = presetBtn.defaultText
            if presetBtn.PresetValue in camHW.Presets:
                PresetName = camHW.Presets[presetBtn.PresetValue]
            presetBtn.SetText(PresetName)
    
    def SelectDefaultCamera(self):
        Log('Selecting Default Camera')
        if self.__Switcher is None:
            self.UpdatePresetButtons()
            return
        self.__SelectBtns.SetCurrent(self.__DefaultCamera)
        input = self.__DefaultCamera.camera['Input']
        qual = self.__Switcher.SwitchCommand.get('qualifier', None)
        Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(self.__Switcher.SwitchCommand['command'], str(input), qual))
        self.__Switcher.interface.Set(self.__Switcher.SwitchCommand['command'], str(input), qual)
        self.UpdatePresetButtons()
        
    def SendCameraHome(self, camera: Union['SystemHardwareController', str]=None): 
        if camera is None:
            for cam in self.GUIHost.Cameras:
                if cam['Id'] in self.GUIHost.Hardware:
                    camHW = self.GUIHost.Hardware[cam['Id']]
                    qual = camHW.PresetRecallCommand.get('qualifier', None)
                    Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetRecallCommand['command'], str(0), qual))
                    camHW.interface.Set(camHW.PresetRecallCommand['command'], str(0), qual)
        else:
            if type(camera) is SystemHardwareController:
                camHW = camera
            elif type(camera) is str:
                if camera in self.GUIHost.Hardware:
                    camHW = self.GUIHost.Hardware[camera]
                else:
                    raise KeyError('No hardware item found for Switcher Id ({})'.format(camera))
            else:
                raise TypeError('Camera must be a SystemHardwareController object or string camera Id')
            
            qual = camHW.PresetRecallCommand.get('qualifier', None)
            Log('Send Command - Command: {}, Value: {}, Qualifier: {}'.format(camHW.PresetRecallCommand['command'], str(0), qual))
            camHW.interface.Set(camHW.PresetRecallCommand['command'], str(0), qual)


## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------