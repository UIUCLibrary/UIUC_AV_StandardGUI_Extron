"""
The system is the place to define system logic, automation, services, etc. as a whole.  It should
provide an *Initialize* method that will be called in main to start the start the system after
variables, devices, and UIs have been defined.

Examples of items in the system file:
* Clocks and scheduled things
* Connection of devices that need connecting
* Set up of services (e.g. ethernet servers, CLIs, etc.)
"""

## Begin Imports ---------------------------------------------------------------

#### Type Checking
from typing import TYPE_CHECKING
if TYPE_CHECKING: # pragma: no cover
    pass

#### Python imports

#### Extron Library Imports
from extronlib import Platform, Version

#### Project imports
from modules.helper.CommonUtilities import Logger
from modules.project.SystemHost import SystemController
import Devices
import Alerts

## End Imports -----------------------------------------------------------------

Logger.Log('ControlScript', Platform(), Version(), separator=' - ')

CONTROLLER = SystemController(Devices.ControlDevices, Devices.SystemDevices, Alerts.SystemAlerts)