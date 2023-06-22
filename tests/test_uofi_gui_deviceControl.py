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
import os
import importlib

import sys
sys.path.append(".\\src")
sys.path.append(".\\tests")
sys.path.append(".\\tests\\reqs")


## test imports ----------------------------------------------------------------
from uofi_gui import SystemController
from uofi_gui.uiObjects import ExUIDevice
from DevelopmentProject.src.modules.project.systemHardware import SystemHardwareController
from uofi_gui.deviceControl import AudioController, CameraController, DisplayController
from uofi_gui.sourceControls import Destination
import test_settings as settings

from extronlib.device import UIDevice
from extronlib.ui import Button, Label, Level, Slider
from extronlib.system import MESet, File
## -----------------------------------------------------------------------------

import test_uofi_gui_deviceControl_audioControl
import test_uofi_gui_deviceControl_cameraControl
import test_uofi_gui_deviceControl_displayControl


if __name__ == '__main__':
    unittest.main()