"""
The main program entrance file.  The contents of this should be:
* Identification of the platform and version.
* imports of the project components
* Call to initialize the system
"""

# Python imports

# Extron Library Imports
from extronlib import Platform, Version

# Project imports
import system
from modules.helper.UtilityFunctions import Logger

Logger.Log('ControlScript', Platform(), Version(), sep=' - ')

system.Initialize()
