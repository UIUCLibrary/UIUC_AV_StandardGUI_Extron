## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

print(Version()) ## Sanity check ControlScript Import
## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
from datetime import datetime
import json
from typing import Dict, Tuple, List, Callable, Union

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from uofi_gui.sourceControls.IO import RelayTuple, LayoutTuple, MatrixTuple, Source, Destination
from uofi_gui.sourceControls.matrix import MatrixController, MatrixRow

import utilityFunctions
import vars
import settings

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class SourceController:
    def __init__(self, 
                 UIHost: UIDevice, 
                 sourceDict: Dict[str, Union[MESet, List[Button]]],
                 advUIList: List[Union[Button, Label]],
                 matrixDict: Dict[str, Union[List[Button], MESet, Button]],
                 sources: List,
                 destinations: List) -> None:
        """Initializes Source Switching module

        Args:
            UIHost (extronlib.device): UIHost to which the buttons are assigned
            sourceBtns (extronlib.system.MESet): MESet of source buttons
            sourceInds (extronlib.system.MESet): MESet of source indicators
            arrowBtns (List[extronlib.ui.Button]): List of arrow button objects, 0
                must be previous/left button and 1 must be next/right button
            advDest (Dict[str, Dict[str, Unions[extronlib.ui.Label, extronlib.ui.Button]]]):
                Dictionary of dictionaries containing advanced switching labels and
                buttons
            sources (List): list of source information
            destinations (List): list of destination information
        """
        
        # Public Properties
        self.UIHost = UIHost
        
        self.Sources = []
        for src in sources:
            self.Sources.append(Source(self,
                                       src['id'], 
                                       src['name'], 
                                       src['icon'], 
                                       src['input'], 
                                       src['alert'],
                                       src['src-ctl'], 
                                       src['adv-src-ctl']))
            
        self.Destinations = []
        for dest in destinations:
            self.Destinations.append(Destination(self,
                                                 dest['id'],
                                                 dest['name'],
                                                 dest['output'],
                                                 dest['type'],
                                                 dest['rly'],
                                                 dest['group-work-src'],
                                                 dest['adv-layout']))
        
        self.PrimaryDestination = self.GetDestination(id = settings.primaryDestination)
        
        
        # Private Properties
        self._sourceBtns = sourceDict['select']
        self._sourceInds = sourceDict['indicator']
        self._arrowBtns = sourceDict['arrows']
        self._offset = 0
        self._advUI = advUIList
        self._advLayout = self.GetAdvShareLayout()
        self._none_source = Source('none', 'None', 0, 0, 0, '')
        self.SelectedSource = self._none_source
        self._DisplaySrcList = None
        self.UpdateDisplaySourceList()
        self._Matrix = MatrixController(self, 
                                        matrixDict['btns'], 
                                        matrixDict['ctls'], 
                                        matrixDict['del'], 
                                        matrixDict['labels']['input'], 
                                        matrixDict['labels']['output'])
        
        for dest in self.Destinations: # Set advanced gui buttons for each destination
            dest.AssignAdvUI(self._GetUIForAdvDest(dest))
        
        # Configure Source Selection Buttons
        @event(self._sourceBtns.Objects, 'Pressed')
        def sourceBtnHandler(button, action):
            # capture last character of button.Name and convert to index
            btnIndex = int(button.Name[-1:]) - 1
            
            # Update source indicator
            self._sourceInds.SetCurrent(self._sourceInds.Objects[btnIndex])

            # Get Source Index, Update Selected Source Object
            srcIndex = btnIndex + self._offset
            self.SelectSource(self._DisplaySrcList[srcIndex])

            # advanced share doesn't switch until destination has been selected
            # all other activities switch immediately
            if vars.ActCtl != None and vars.ActCtl.CurrentActivity != "adv_share": 
                self.SwitchSources(self.SelectedSource)
                # TODO: Format Source Control Popup
                page = self.SelectedSource._sourceControlPage 
                if page == 'PC':
                    page = '{p}_{c}'.format(p=page, c=len(settings.cameras))
                self.UIHost.ShowPopup("Source-Control-{}".format(page))
        
        @event(self._arrowBtns, 'Pressed')
        def sourcePageHandler(button, action):
            # capture last 4 characters of button.Name
            btnAction = button.Name[-4:]
            # determine if we are adding or removing offset
            if btnAction == "Prev":
                self._offset -= 1
            elif btnAction == "Next":
                self._offset += 1
            # update the displayed source menu
            self.UpdateSourceMenu()
    
    
    def _GetUIForAdvDest(self, dest: Destination) -> Dict[str, Button]:
        """Get Advanced Display button objects for a given destination ID

        Args:
            dest (Destination): Destination object to lookup

        Raises:
            LookupError: raised when destination is not found in destinations
            KeyError: raised if the buttons could not be found in the dict of
                available buttons

        Returns:
            Dict[str, extronlib.ui.Button]: Dictionary containing the button objects for
                the specified destination
        """     
        
        destDict = {}
        
        index = self.Destinations.index(dest)
        location = self.Destinations[index].AdvLayoutPosition
        
        if not (type(location) == LayoutTuple): 
            raise LookupError("Provided Destination Object ({}) not found in Destinations."
                            .format(dest.Name))
        
        for item in self._advUI:
            if item.Name == 'Disp-Select-{p},{r}'.format(p = location.Pos, r = location.Row):
                destDict['select'] = item
            if item.Name == 'Disp-Ctl-{p},{r}'.format(p = location.Pos, r = location.Row):
                destDict['ctl'] = item
            if item.Name == 'Disp-Aud-{p},{r}'.format(p = location.Pos, r = location.Row):
                destDict['aud'] = item
            if item.Name == 'Disp-Alert-{p},{r}'.format(p = location.Pos, r = location.Row):
                destDict['alert'] = item
            if item.Name == 'Disp-Scn-{p},{r}'.format(p = location.Pos, r = location.Row):
                destDict['scn'] = item
            if item.Name == 'DispAdv-{p},{r}'.format(p = location.Pos, r = location.Row):
                destDict['label'] = item
            if len(destDict) == 6:
                # for d in destDict.values():
                #     self._advUI.remove(d)
                break
        
        if len(destDict) < 6:
            raise KeyError("At least one destination button not found. ({}, {})".format(location, destDict))
        
        return destDict
            
    
    def _GetPositionByBtnName(self, btnName: str) -> LayoutTuple:
        btnLoc = btnName[-3:]
        btnPR = btnLoc.split(',')
        return LayoutTuple(Row = btnPR[1], Pos = btnPR[0])
    
    def GetAdvShareLayout(self) -> str:
        layout = {}
        for dest in self.Destinations:
            r = str(dest.AdvLayoutPosition.Row)
            if r in layout:
                layout[r].append(dest)
            else:
                layout[r] = [dest]
                
        rows = []
        i = 0
        while i < len(layout.keys()):
            rows.append(str(len(layout[str(i)])))
            i += 1
            
        return "Source-Control-Adv_{}".format(",".join(rows))
    
    def GetDestination(self, id: str=None, name: str=None) -> Destination:
        if id == None and name == None:
            raise ValueError("Either Id or Name must be provided")
        if id != None:
            for dest in self.Destinations:
                if dest.Id == id:
                    return dest
        if name != None:
            for dest in self.Destinations:
                if dest.Name == name:
                    return dest
    
    def GetDestinationIndexByID(self, id: str) -> int:
        """Get Destination Index from ID.

        Args:
            id (str): Destination ID string
        
        Raises:
            LookupError: raised if ID is not found in list

        Returns:
            int: Returns destination dict index
        """    
        i = 0
        for dest in self.Destinations:
            if id == dest.Id:
                return i
            i += 1
        ## if we get here then there was no valid index for the id
        raise LookupError("Provided ID ({}) not found".format(id))
                
    def GetSource(self, id: str=None, name: str=None) -> Source:
        if id == None and name == None:
            raise ValueError("Either Id or Name must be provided")
        if id != None:
            for src in self.Sources:
                if src.Id == id:
                    return src
        if name != None:
            for src in self.Sources:
                if src.Name == name:
                    return src
    
    def GetSourceIndexByID(self, id: str) -> int:
        """Get Source Index from ID.

        Args:
            id (str): Source ID string
        
        Raises:
            LookupError: raised if ID is not found in list

        Returns:
            int: Returns source list index
        """    
        i = 0
        for src in self._DisplaySrcList:
            if id == src.Id:
                return i
            i += 1
        ## if we get here then there was no valid index for the id
        raise LookupError("Provided Id ({}) not found".format(id))
    
    def SetPrimaryDestination(self, dest: Destination) -> None:
        if type(dest) != Destination:
            raise TypeError("Object of class Destination must be provided")
        self.PrimaryDestination = dest
        
    def SelectSource(self, src: Union[Source, str]) -> None:
        if type(src) == Source:
            self.SelectedSource = src
        elif type(src) == str:
            srcObj = self.GetSource(id = src, name = src)
            self.SelectedSource = srcObj
    
    def UpdateDisplaySourceList(self) -> None:
        """Get the current source list

        Returns:
            List: The list of currently displayable source definitions
        """    
        srcList = []
        
        if type(vars.ActCtl) is not type(None):
            if vars.ActCtl.CurrentActivity == 'adv_share':
                srcList.append(self._none_source)
        srcList.extend(self.Sources)
        
        self._DisplaySrcList = srcList
        
    def UpdateSourceMenu(self) -> None:
        """Updates the formatting of the source menu. Use when the number of sources
        or the pagination of the source bar changes
        """    
        
        self.UpdateDisplaySourceList()
        
        offsetIter = self._offset
        for btn in self._sourceBtns.Objects:
            offState = int('{}0'.format(self._DisplaySrcList[offsetIter].Icon))
            onState = int('{}1'.format(self._DisplaySrcList[offsetIter].Icon))
            self._sourceBtns.SetStates(btn, offState, onState)
            btn.SetText(self._DisplaySrcList[offsetIter].Name)
            offsetIter += 1
            
        if len(self._DisplaySrcList) <= 5:
            self.UIHost.ShowPopup('Menu-Source-{}'.format(len(self._DisplaySrcList)))
        else:
            # enable/disable previous arrow
            if self._offset == 0:
                self._arrowBtns[0].SetEnable(False)
                self._arrowBtns[0].SetState(2)
            else:
                self._arrowBtns[0].SetEnable(True)
                self._arrowBtns[0].SetState(0)
            # enable/disable next arrow
            if (self._offset + 5) >= len(self._DisplaySrcList):
                self._arrowBtns[1].SetEnable(False)
                self._arrowBtns[1].SetState(2)
            else:
                self._arrowBtns[1].SetEnable(True)
                self._arrowBtns[1].SetState(0)
            
            self.UIHost.ShowPopup('Menu-Source-5+')
            
        # reset currently selected source
        currentSourceIndex = self.GetSourceIndexByID(self.SelectedSource.Id)
        
        btnIndex = currentSourceIndex - self._offset
        if btnIndex > 4:
            raise KeyError("Button Index Out of Range")
        
        self._sourceBtns.SetCurrent(self._sourceBtns.Objects[btnIndex])
        self._sourceInds.SetCurrent(self._sourceInds.Objects[btnIndex])
        
    def ShowSelectedSource(self) -> None:
        if len(self._DisplaySrcList) > 5:
            curSourceIndex = self._DisplaySrcList.index(self.SelectedSource)
            
            if curSourceIndex < self._offset:
                self._offset -= (self._offset - curSourceIndex)
            elif curSourceIndex >= (self._offset + 5):
                self._offset = curSourceIndex - 4
            
            self.UpdateSourceMenu()
        
    def SwitchSources(self, src: Union[Source, str], dest: Union[str, List[Union[Destination, str]]]='All') -> None:
        if type(dest) == str and dest != 'All':
            raise TypeError("Destination must either be 'All' or a list of Destination objects, names, and/or IDs")
        
        if type(src) == str:
            srcObj = self.GetSource(id = src, name = src)
        elif type(src) == Source:
            srcObj = src
        
        # TODO: Update Matrix (send matrix tie commands to the matrix rows being affected)
        if type(dest) == str and dest == 'All':
            for d in self.Destinations:
                d.AssignSource(srcObj)
                # TODO: send source change command
        elif type(dest) == List:
            for d in dest:
                if type(d) == Destination:
                    d.AssignSource(srcObj)
                    # TODO: send source change command
                elif type(d) == str:
                    destObj = self.GetDestination(id = d, name = d)
                    destObj.AssignSource(srcObj)
                    # TODO: send source change command
                    
        

    def MatrixSwitch(self, src: Union[Source, str, int], dest: Union[str, List[Union[Destination, str, int]]]='All', mode: str='AV') -> None:
        if type(dest) == str and dest != 'All':
            raise TypeError("Destination must either be 'All' or a list of Destination objects, names, IDs, or switcher output integer")
        
        if type(src) == str:
            srcObj = self.GetSource(id = src, name = src)
            if srcObj == None:
                raise KeyError("No source object found for ID/Name: {} {}".format(src, type(src)))
            srcNum = srcObj.Input
        elif type(src) == Source:
            srcObj = src
            srcNum = src.Input
        elif type(src) == int:
            srcObj = None
            srcNum = int
        else:
            raise TypeError("Source must be a source object, source name string, source Id string, or switcher input integer")
        
        # TODO: Update Matrix (send matrix tie commands to the matrix rows being affected)
        if type(dest) == str and dest == 'All':
            for d in self.Destinations:
                if srcObj == None:
                    d.AssignMatrix(srcNum, mode)
                else:
                    d.AssignSource(srcObj)
            # TODO: send source change command
        # DEBUG: check the below settings for consistency of assignment to the destination objects
        # I suspect there are issues with the AssignSource calls when in a mode other than 'AV'
        elif type(dest) == List:
            for d in dest:
                if type(d) == Destination:
                    if srcObj == None:
                        d.AssignMatrix(srcNum, mode)
                    else:
                        d.AssignSource(srcObj)
                    # TODO: send source change command
                elif type(d) == str:
                    destObj = self.GetDestination(id = d, name = d)
                    if srcObj == None:
                        destObj.AssignMatrix(srcNum, mode)
                    else:
                        destObj.AssignSource(srcObj)
                    # TODO: send source change command
                elif type(d) == int:
                    destObj = None
                    for d2 in self.Destinations:
                        if d == d2.Output:
                            destObj = d2
                    if destObj != None:
                        if srcObj == None:
                            destObj.AssignMatrix(srcNum, mode)
                        else:
                            destObj.AssignSource(srcObj)
                    # TODO: send source change command
            
    # def GetSourceByAdvShareLoc(self, location: LayoutTuple) -> str:
    #     for dest in settings.destinations:
    #         if dest['adv-layout']['pos'] == pos \
    #         and dest['adv-layout']['row'] == row:
    #             srcID = GetSourceByDestination(dest['id'])
    #     if srcID == None:
    #         raise LookupError("Button position ({p},{r}) not found"
    #                           .format(p = pos, r = row))
    #     return srcID


## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------


    
# def SourceNameToIndex(name: str, srcList: List = settings.sources) -> int:
#     """Get Source Index from Name. Will fail for the 'none' source if using
#     config.sources.

#     Args:
#         name (str): Source name string
#         srcList (List, optional): List of source data. Defaults to config.sources
    
#     Raises:
#         LookupError: raised if ID is not found in list

#     Returns:
#         int: Returns source dict index
#     """    
#     i = 0
#     for src in srcList:
#         if name == src['name']:
#             return i
#         i += 1
#     ## if we get here then there was no valid index for the name
#     raise LookupError("Provided name ({}) not found".format(name))

# def SourceNameToID(name: str, srcList: List = settings.sources) -> str:
#     """Get Source ID from Source Name. Will fail for the 'none' source if using
#     config.sources

#     Args:
#         name (str): Source name string
#         srcList (List, optional): List of source data. Defaults to config.sources
    
#     Raises:
#         LookupError: raised if ID is not found in list

#     Returns:
#         str: Returns source ID string
#     """
    
#     for src in srcList:
#         if name == src['name']:
#             return src['id']
#         i += 1
#     ## if we get here then there was no valid match for the name
#     raise LookupError("Provided name ({}) not found".format(name))

# def SourceIDToName(id: str, srcList: List = settings.sources) -> str:
#     """Get Source Name from Source ID. Will fail for the 'none' source if using
#     config.sources

#     Args:
#         id (str): Source ID string
#         srcList (List, optional): List of source data. Defaults to config.sources

#     Raises:
#         LookupError: raised if ID is not found in list

#     Returns:
#         str: Returns source Name string
#     """
#     if id == "none": return "None"    
#     for src in srcList:
#         if id == src['id']:
#             return src['name']
#         i += 1
#     ## if we get here then there was no valid match for the id and an exception should be raised
#     raise LookupError("Provided ID ({}) not found".format(id))



# def DestNameToIndex(name: str, destList: List = settings.destinations) -> int:
#     """Get Destination Index from Name. Will fail for the 'none' destination if
#     using config.sources.

#     Args:
#         name (str): Destination name string
#         destList (List, optional): List of destination data. Defaults to
#             config.destinations
    
#     Raises:
#         LookupError: raised if ID is not found in list

#     Returns:
#         int: Returns destination dict index
#     """    
#     i = 0
#     for dest in destList:
#         if name == dest['name']:
#             return i
#         i += 1
#     ## if we get here then there was no valid index for the name
#     raise LookupError("Provided name ({}) not found".format(name))

# def DestNameToID(name: str, destList: List = settings.destinations) -> str:
#     """Get Destination ID from Destination Name. Will fail for the 'none'
#     destination if using config.sources

#     Args:
#         name (str): Destination name string
#         destList (List, optional): List of destination data. Defaults to
#             config.destinations
    
#     Raises:
#         LookupError: raised if ID is not found in list

#     Returns:
#         str: Returns destination ID string
#     """
    
#     for dest in destList:
#         if name == dest['name']:
#             return dest['id']
#         i += 1
#     ## if we get here then there was no valid match for the name
#     raise LookupError("Provided name ({}) not found".format(name))

# def DestIDToName(id: str, destList: List = settings.destinations) -> str:
#     """Get Destination Name from Destination ID. Will fail for the 'none'
#     destination if using config.sources

#     Args:
#         id (str): Destination ID string
#         destList (List, optional): List of destination data. Defaults to
#             config.destinations.

#     Raises:
#         LookupError: raised if ID is not found in list

#     Returns:
#         str: Returns destination Name string
#     """
#     if id == "none": return "None"    
#     for dest in destList:
#         if id == dest['id']:
#             return dest['name']
#         i += 1
#     ## if we get here then there was no valid match for the id
#     raise LookupError("Provided ID ({}) not found".format(id))
        
# def GetSourceByDestination(dest: str) -> str:
#     """Get source ID based on destination ID

#     Args:
#         dest (str): The string ID of the destination of which to find the
#             current source

#     Returns:
#         str: The string ID of the source sent to the provided destination
#     """    
    
#     # get switcher output from config.destinations for provided dest
#     swDest = settings.destinations[DestIDToIndex(dest)]['output']
    
#     # get tied input for dest output
#     #### TODO: query the switcher for input tied to swDest store as swSrc
#     swSrc = None
    
#     # iterate over settings.sources to match switcher input to source
#     for src in settings.sources:
#         if swSrc == src['input']:
#             # return source id string
#             return src['id']
    
#     raise LookupError("Source for destination ({}) could not be found"
#                       .format(dest))



## End Function Definitions ----------------------------------------------------



