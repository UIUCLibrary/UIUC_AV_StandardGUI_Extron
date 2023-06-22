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

from typing import Dict, Tuple, List, Callable, Union, cast

## test imports ----------------------------------------------------------------
from uofi_gui import SystemController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.headerControls import HeaderController
import test_settings as settings

from extronlib.device import UIDevice
from extronlib.ui import Button

## -----------------------------------------------------------------------------

class HeaderController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        importlib.reload(settings)
        self.TestGUIController = SystemController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestHeaderController = self.TestUIController.HdrCtl
        return super().setUp()
    
    def test_HeaderController_Type(self): 
        self.assertIsInstance(self.TestHeaderController, HeaderController)
    
    def test_HeaderController_Properties(self):
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestHeaderController.UIHost, (UIDevice, ExUIDevice))
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestHeaderController.GUIHost, SystemController)
    
    def test_HeaderController_PRIV_Properties(self):
        # __CloseBtn
        with self.subTest(param='__CloseBtn'):
            self.assertIsInstance(self.TestHeaderController._HeaderController__CloseBtn, Button)
        
        # __HideWhenOff
        with self.subTest(param='__HideWhenOff'):
            self.assertIsInstance(self.TestHeaderController._HeaderController__HideWhenOff, list)
            for item in self.TestHeaderController._HeaderController__HideWhenOff:
                with self.subTest(item=item):
                    self.assertIsInstance(item, str)
        
        # __HideAlways
        with self.subTest(param='__HideAlways'):
            self.assertIsInstance(self.TestHeaderController._HeaderController__HideAlways, list)
            for item in self.TestHeaderController._HeaderController__HideAlways:
                with self.subTest(item=item):
                    self.assertIsInstance(item, str)
        
        # __HeaderBtns
        with self.subTest(param='__HeaderBtns'):
            self.assertIsInstance(self.TestHeaderController._HeaderController__HeaderBtns, list)
            for item in self.TestHeaderController._HeaderController__HeaderBtns:
                with self.subTest(item=item.Name):
                    self.assertIsInstance(item, Button)
        
        # __AllPopovers
        with self.subTest(param='__AllPopovers'):
            self.assertIsInstance(self.TestHeaderController._HeaderController__AllPopovers, list)
            for item in self.TestHeaderController._HeaderController__AllPopovers:
                with self.subTest(item=item):
                    self.assertIsInstance(item, str)
    
    def test_HeaderController_EventHandler_HeaderButtonHandler(self):
        buttonList = self.TestHeaderController._HeaderController__HeaderBtns
        actionList = ['Pressed', 'Tapped', 'Released']
        for btn in buttonList:
            for act in actionList:
                with self.subTest(button=btn, action=act):
                    try:
                        self.TestHeaderController._HeaderController__HeaderButtonHandler(btn, act)
                    except Exception as inst:
                        self.fail('__HeaderButtonHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_HeaderController_EventHandler_PopoverCloseHandler(self):
        buttonList = [self.TestHeaderController._HeaderController__CloseBtn]
        actionList = ['Pressed']
        for btn in buttonList:
            for act in actionList:
                with self.subTest(button=btn, action=act):
                    try:
                        self.TestHeaderController._HeaderController__PopoverCloseHandler(btn, act)
                    except Exception as inst:
                        self.fail('__PopoverCloseHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_HeaderController_ConfigSystemOn(self):
        try:
            self.TestHeaderController.ConfigSystemOn()
        except Exception as inst:
            self.fail('__PopoverCloseHandler raised {} unexpectedly!'.format(type(inst)))
        
        for btn in self.TestHeaderController._HeaderController__HeaderBtns:
            if btn.Hide == 'off':
                with self.subTest(button=btn):
                    self.assertEqual(btn.Hide, 'off')
                    self.assertTrue(btn.Visible)
                    self.assertTrue(btn.Enabled)
    
    def test_HeaderController_ConfigSystemOff(self):
        try:
            self.TestHeaderController.ConfigSystemOff()
        except Exception as inst:
            self.fail('__PopoverCloseHandler raised {} unexpectedly!'.format(type(inst)))
        
        for btn in self.TestHeaderController._HeaderController__HeaderBtns:
            if btn.Hide == 'off':
                with self.subTest(button=btn):
                    self.assertEqual(btn.Hide, 'off')
                    self.assertFalse(btn.Visible)
                    self.assertFalse(btn.Enabled)
    
if __name__ == '__main__':
    unittest.main()