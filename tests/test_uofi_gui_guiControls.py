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

import unittest
import importlib

import sys
sys.path.append(".\\src")
sys.path.append(".\\tests")
sys.path.append(".\\tests\\reqs")

## test imports ----------------------------------------------------------------
from uofi_gui import SystemController, ExProcessorDevice
from uofi_gui.uiObjects import ExUIDevice
from DevelopmentProject.src.modules.project.systemHardware import SystemPollingController, SystemHardwareController

import test_settings as settings
import test_settings as settings_no_primary

from extronlib.device import ProcessorDevice, UIDevice
## -----------------------------------------------------------------------------

class ExProcessorDevice_TestClass(unittest.TestCase):
    def test_ExProcessorDevice_Init(self):
        try:
            testProc = ExProcessorDevice('CTL001')
        except Exception as inst:
            self.fail("Creating ExProcessorDevice raised {} unexpectedly!".format(type(inst)))
            
        self.assertIsInstance(testProc, ExProcessorDevice)
        self.assertIsInstance(testProc, ProcessorDevice)
        
    def test_ExProcessorDevice_Properties(self):
        testProc = ExProcessorDevice('CTL001')
        # Id
        self.assertIsInstance(testProc.Id, str)
        self.assertEqual(testProc.Id, 'CTL001')

class GUIController_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        print('Setting Up')
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        importlib.reload(settings)
        importlib.reload(settings_no_primary)

        if hasattr(settings_no_primary, 'primaryProcessor'):
            delattr(settings_no_primary, 'primaryProcessor')
        if hasattr(settings_no_primary, 'primaryTouchPanel'):
            delattr(settings_no_primary, 'primaryTouchPanel')
        self.settingsList = [settings, settings_no_primary]
        
        return super().setUp()
    
    
    def InitializeController(self):
        importlib.reload(settings)
        self.TestController = SystemController(settings, self.TestCtls, self.TestTPs)
        self.TestController.Initialize()
    
    def test_GUIController_Init_Lists(self):
        for i in range(len(self.settingsList)):
            with self.subTest(i=i):
                try:
                    TestController = SystemController(self.settingsList[i], self.TestCtls, self.TestTPs)
                except Exception as inst:
                    self.fail("Creating GUICOntroller raised {} unexpectedly!".format(type(inst)))
        
                self.assertIsInstance(TestController, SystemController)
    
    def test_GUIController_Init_Strings(self):        
        for i in range(len(self.settingsList)):
            with self.subTest(i=i):
                try:
                    TestController = SystemController(self.settingsList[i], self.TestCtls[0], self.TestTPs[0])
                except Exception as inst:
                    self.fail("Creating GUICOntroller raised {} unexpectedly!".format(type(inst)))
        
                self.assertIsInstance(TestController, SystemController)
                
    def test_GUIController_Init_NoTPs(self):
        try:
            TestController = SystemController(settings, self.TestCtls, [])
        except Exception as inst:
            self.fail("Creating GUICOntroller raised {} unexpectedly!".format(type(inst)))

        self.assertIsInstance(TestController, SystemController)
    
    def test_GUIController_Init_Failure_EmptyCtlList(self):
        importlib.reload(settings)
        with self.assertRaises(ValueError):
            SystemController(settings, [], self.TestTPs[0])
            
    def test_GUIController_Init_Failure_BadTypeCtl(self):
        importlib.reload(settings)
        with self.assertRaises(TypeError):
            SystemController(settings, 1, self.TestTPs[0])
            
    def test_GUIController_Init_Failure_BadTypeCtlList(self):
        importlib.reload(settings)
        with self.assertRaises(TypeError):
            SystemController(settings, [1], self.TestTPs[0])
            
    def test_GUIController_Init_Failure_BadTypeTP(self):
        importlib.reload(settings)
        with self.assertRaises(TypeError):
            SystemController(settings, self.TestCtls[0], 1)
            
    def test_GUIController_Init_Failure_BadTypeTPList(self):
        importlib.reload(settings)
        with self.assertRaises(TypeError):
            SystemController(settings, self.TestCtls[0], [1])
            
    def test_GUIController_Properties(self):
        importlib.reload(settings)
        self.TestController = SystemController(settings, self.TestCtls, self.TestTPs)
        
        # CtlJSON
        self.assertIsInstance(self.TestController.CtlJSON, str)
        
        # RoomName
        self.assertIsInstance(self.TestController.RoomName, str)
        
        # ActivityMode
        self.assertIsInstance(self.TestController.ActivityMode, int)
        
        # Timers
        self.assertIsInstance(self.TestController.Timers, dict)
        for timer in self.TestController.Timers:
            with self.subTest(i=timer):
                self.assertIsInstance(timer, str)
                self.assertIsInstance(self.TestController.Timers[timer], int)
        
        # TechMatrixSize
        self.assertIsInstance(self.TestController.TechMatrixSize, tuple)
        
        # TechPIN
        self.assertIsInstance(self.TestController.TechPIN, str)
        self.assertEqual(self.TestController.TechPIN, str(int(self.TestController.TechPIN)))
        self.assertLessEqual(len(self.TestController.TechPIN), 10)
        
        # CameraSwitcherId
        self.assertIsInstance(self.TestController.CameraSwitcherId, str)
        self.assertRegex(self.TestController.CameraSwitcherId, r'^[A-Z]{2,3}[0-9]{3}$')
        
        # Sources
        self.assertIsInstance(self.TestController.Sources, list)
        for src in self.TestController.Sources:
            with self.subTest(i=src):
                self.assertIsInstance(src, dict)
        
        # Destinations
        self.assertIsInstance(self.TestController.Destinations, list)
        for dest in self.TestController.Destinations:
            with self.subTest(i=dest):
                self.assertIsInstance(dest, dict)
        
        # Cameras
        self.assertIsInstance(self.TestController.Cameras, list)
        for cam in self.TestController.Cameras:
            with self.subTest(i=cam):
                self.assertIsInstance(cam, dict)
        
        # Microphones
        self.assertIsInstance(self.TestController.Microphones, list)
        for mic in self.TestController.Microphones:
            with self.subTest(i=mic):
                self.assertIsInstance(mic, dict)
        
        # Lights
        self.assertIsInstance(self.TestController.Lights, list)
        for light in self.TestController.Lights:
            with self.subTest(i=light):
                self.assertIsInstance(light, dict)
        
        # DefaultSourceId
        self.assertIsInstance(self.TestController.DefaultSourceId, str)
        self.assertRegex(self.TestController.DefaultSourceId, r'^[A-Z]{2,3}[0-9]{3}$')
        
        # DefaultCameraId
        self.assertIsInstance(self.TestController.DefaultCameraId, str)
        self.assertRegex(self.TestController.DefaultCameraId, r'^[A-Z]{2,3}[0-9]{3}$')
        
        # PrimaryDestinationId
        self.assertIsInstance(self.TestController.PrimaryDestinationId, str)
        self.assertRegex(self.TestController.PrimaryDestinationId, r'^[A-Z]{2,3}[0-9]{3}$')
        
        # PrimarySwitcherId
        self.assertIsInstance(self.TestController.PrimarySwitcherId, str)
        self.assertRegex(self.TestController.PrimarySwitcherId, r'^[A-Z]{2,3}[0-9]{3}$')
        
        # PrimaryDSPId
        self.assertIsInstance(self.TestController.PrimaryDSPId, str)
        self.assertRegex(self.TestController.PrimaryDSPId, r'^[A-Z]{2,3}[0-9]{3}$')
        
        # CtlProcs
        self.assertIsInstance(self.TestController.CtlProcs, list)
        for ctl in self.TestController.CtlProcs:
            with self.subTest(i=ctl):
                self.assertIsInstance(ctl, ExProcessorDevice)
                self.assertIsInstance(ctl, ProcessorDevice)
        
        # CtlProc_Main
        self.assertIsInstance(self.TestController.CtlProc_Main, ProcessorDevice)
        
        # PollCtl
        self.assertIsInstance(self.TestController.PollCtl, SystemPollingController)
        
        # Hardware
        self.assertIsInstance(self.TestController.Hardware, dict)
        for hw in self.TestController.Hardware:
            with self.subTest(i=hw):
                self.assertIsInstance(hw, str)
                self.assertRegex(hw, r'^[A-Z]{2,3}[0-9]{3}$')
                self.assertIsInstance(self.TestController.Hardware[hw], SystemHardwareController)
        
        # TPs
        self.assertIsInstance(self.TestController.TPs, list)
        for tp in self.TestController.TPs:
            with self.subTest(i=tp):
                self.assertIsInstance(tp, ExUIDevice)
                self.assertIsInstance(tp, UIDevice)
        
        # TP_Main
        self.assertIsInstance(self.TestController.TP_Main, ExUIDevice)
        self.assertIsInstance(self.TestController.TP_Main, UIDevice)
        
    def test_GUIController_StartupActions(self):
        self.InitializeController()
        
        try:
            self.TestController.StartupActions()
        except Exception as inst:
            self.fail("StartupActions raised {} unexpectedly!".format(type(inst)))
    
    def test_GUIController_StartupSyncedActions(self):
        self.InitializeController()
        
        counts = [1, 5, 15, 30]
        
        for i in range(len(counts)):
            with self.subTest(i=i):
                try:
                    self.TestController.StartupSyncedActions(i)
                except Exception as inst:
                    self.fail("StartupActions ({}) raised {} unexpectedly!".format(i, type(inst)))
                    
    def test_GUIController_SwitchActions(self):
        self.InitializeController()
        
        try:
            self.TestController.SwitchActions()
        except Exception as inst:
            self.fail("SwitchActions raised {} unexpectedly!".format(type(inst)))
    
    def test_GUIController_SwitchSyncedActions(self):
        self.InitializeController()
        
        counts = [1, 5, 15, 30]
        
        for i in range(len(counts)):
            with self.subTest(i=i):
                try:
                    self.TestController.SwitchSyncedActions(i)
                except Exception as inst:
                    self.fail("SwitchActions ({}) raised {} unexpectedly!".format(i, type(inst)))
                    
    def test_GUIController_ShutdownActions(self):
        self.InitializeController()
        
        try:
            self.TestController.ShutdownActions()
        except Exception as inst:
            self.fail("ShutdownActions raised {} unexpectedly!".format(type(inst)))
    
    def test_GUIController_ShutdownSyncedActions(self):
        self.InitializeController()
        
        counts = [1, 5, 15, 30]
        
        for i in range(len(counts)):
            with self.subTest(i=i):
                try:
                    self.TestController.ShutdownSyncedActions(i)
                except Exception as inst:
                    self.fail("ShutdownActions ({}) raised {} unexpectedly!".format(i, type(inst)))
    
if __name__ == '__main__':
    unittest.main()