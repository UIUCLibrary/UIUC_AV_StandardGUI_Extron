"""
The main program entrance file.  The contents of this should be:
* Identification of the platform and version.
* imports of the project components
* Call to initialize the system
"""

from extronlib import Platform, Version
from modules.helper.CommonUtilities import Logger

Logger.Log('ControlScript', Platform(), Version(), separator=' - ')

import System

System.CONTROLLER.Initialize()
