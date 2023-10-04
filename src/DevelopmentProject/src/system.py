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
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    pass

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.project.SystemHost import SystemController
import Devices

## End Imports -----------------------------------------------------------------

CONTROLLER = SystemController(Devices.ControlDevices, Devices.SystemDevices)