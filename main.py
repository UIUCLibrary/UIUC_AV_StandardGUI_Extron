'''
Since we can't load modules through Global Scripter directly, we will instead
upload modules to the SFTP path on the controller. Create a new directory at
the root of the SFTP called 'modules' and upload modules there. Modules in this
directory may be imported after the sys.path.import call. 
'''
import sys
sys.path.insert(0, "/var/nortxe/uf/admin/modules/")

# Import GUIController
from uofi_gui import GUIController

# System configuration modules (GS Modules)
import settings

## End User Import -------------------------------------------------------------

guiController = GUIController(settings, ['CTL001'], ['TP001'])

guiController.Initialize()
