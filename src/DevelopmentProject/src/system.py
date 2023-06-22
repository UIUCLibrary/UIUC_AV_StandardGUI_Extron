"""
The system is the place to define system logic, automation, services, etc. as a whole.  It should
provide an *Initialize* method that will be called in main to start the start the system after
variables, devices, and UIs have been defined.

Examples of items in the system file:
* Clocks and scheduled things
* Connection of devices that need connecting
* Set up of services (e.g. ethernet servers, CLIs, etc.)
"""

# Python imports

# Extron Library imports

# Project imports
from modules.project.SystemHost import SystemController
import variables
import devices

DeviceCollection = SystemController(variables, devices, ['CTL001'], ['TP001'])

Initialize = DeviceCollection.Initialize