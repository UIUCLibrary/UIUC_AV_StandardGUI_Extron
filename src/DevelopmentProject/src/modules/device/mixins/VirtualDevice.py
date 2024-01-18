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

from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING: # pragma: no cover
    pass

import System

class VirtualDeviceInterface:
    def __init__(self, VirtualDeviceID, AssignmentAttribute: str, AssignmentDict: Dict) -> None:
        self.VirtualDeviceID = VirtualDeviceID
        self.__AssignmentAttribute = AssignmentAttribute
        self.__AssignmentDict = AssignmentDict
    
    def FindAssociatedHardware(self):
        # iterate through System.CONTROLLER.Devices and find devices with matching __AssignmentAttribute
        for Hw in System.CONTROLLER.Devices.values(): # GUIHost attribute must exist in parent class
            if getattr(Hw, self.__AssignmentAttribute, None) == self.VirtualDeviceID:
                for key, value in self.__AssignmentDict.items():
                    if hasattr(Hw, key):
                        value[getattr(Hw, key)] = Hw