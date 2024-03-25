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
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:                                                               # pragma: no cover
    from modules.project.Collections import DeviceCollection
    from modules.project.Devices import SystemHardwareController

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import isinstanceEx, Logger

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class InitializeMixin(object):
    def __init__(self, init_method: Callable) -> None:
        self.__Initialized = False
        if callable(init_method):
            self.__Init_Method = init_method
        else:
            raise TypeError('init_method parameter must be callable')
        
    @property
    def Initialized(self) -> bool:
        return self.__Initialized
    
    @Initialized.setter
    def Initialized(self) -> None:
        raise AttributeError('Setting Initialized directly is disallowed. Use the Initialize method instead.')
    
    def Initialize(self) -> None:
        self.__Init_Method()
        Logger.Debug('Initializing {} Object: '.format(type(self).__name__), getattr(self, 'Name', self.__repr__()))
        self.__Initialized = True

class InterfaceSystemHost(object):
    def __init__(self, Collection: "DeviceCollection" = None) -> None:
        self.__Collection = None

        if Collection is not None:
            self.Collection = Collection

    @property
    def Collection(self) -> "DeviceCollection":
        return self.__Collection

    @Collection.setter
    def Collection(self, Collection: "DeviceCollection") -> None:
        if isinstanceEx(Collection, 'DeviceCollection'):
            self.__Collection = Collection
        else:
            raise TypeError("Collection must be of type DeviceCollection")


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



