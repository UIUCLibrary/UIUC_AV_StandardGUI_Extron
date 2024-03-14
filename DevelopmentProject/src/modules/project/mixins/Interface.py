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

## Begin Imports ---------------------------------------------------------------

#### Type Checking
from typing import TYPE_CHECKING
if TYPE_CHECKING: # pragma: no cover
    from modules.project.Collections import DeviceCollection
    from modules.project.SystemHardware import SystemHardwareController

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import isinstanceEx

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class InterfaceSystemHost(object):
    def __init__(self, Collection: "DeviceCollection" = None) -> None:
        __Collection = None
        
        if Collection is not None:
            self.Collection = Collection
        
    @property
    def Collection(self) -> "DeviceCollection":
        return self.__Collection
    
    @Collection.setter
    def Collection(self, Collection: "DeviceCollection") -> None:
        if type(Collection).__name__ != 'DeviceCollection':
            raise TypeError("Collection must be of type DeviceCollection")
        self.__Collection = Collection

class DeviceMixIn(object):
    def __init__(self,
                 device: 'SystemHardwareController'=None,
                 id: str=None,
                 name: str=None) -> None:
        if device is not None and isinstanceEx(device, 'SystemHardwareController'):
            self.Device = device
            self.Id = device.Id
            self.Name = device.Name
        elif id is not None and name is not None:
            self.Device = None
            self.Id = id
            self.Name = name
        else:
            raise ValueError('Device or id and name must be provided')

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



