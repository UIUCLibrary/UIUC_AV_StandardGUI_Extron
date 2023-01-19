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
from collections import namedtuple
import re

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules

#import utilityFunctions
import vars
import settings

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------
RelayTuple = namedtuple('RelayTuple', ['Up', 'Down'])
LayoutTuple = namedtuple('LayoutTuple', ['Row', 'Pos'])
MatrixTuple = namedtuple('MatrixTuple', ['Vid', 'Aud'])


class Source:
    def __init__(self,
                 SrcCtl, #: SourceController,
                 id: str,
                 name: str,
                 icon: int,
                 input: int,
                 alert: int,
                 srcCtl: str=None,
                 advSrcCtl: str=None) -> None:
        
        self.SourceController = SrcCtl
        self.Id = id
        self.Name = name
        self.Icon = icon
        self.Input = input
        self.AlertText = alert
        self.AlertFlag = False
        
        self._defaultAlert = alert
        self._sourceControlPage = srcCtl
        self._advSourceControlPage = advSrcCtl
        
    def AppendAlert(self, msg: str, raiseFlag: bool=False) -> None:
        self.AlertText = "{existing}\n{append}".format(existing = self.AlertText, append = msg)
        if raiseFlag:
            self.AlertFlag = True
        
    def OverrideAlert(self, msg: str, raiseFlag: bool=False) -> None:
        self.AlertText = msg
        if raiseFlag:
            self.AlertFlag = True
        
    def ResetAlert(self, raiseFlag: bool=False) -> None:
        self.AlertText = self._defaultAlert
        if raiseFlag:
            self.AlertFlag = True
        
class Destination:
    def __init__(self,
                 SrcCtl, #: SourceController,
                 id: str,
                 name: str,
                 output: int,
                 destType: str,
                 rly: List,
                 groupWrkSrc: str,
                 advLayout: Dict[str, int]) -> None:
        
        self.SourceController = SrcCtl
        self.Id = id
        self.Name = name
        self.Output = output
        self.AdvLayoutPosition = LayoutTuple(Row=advLayout['row'], Pos=advLayout['pos'])
        self.AssignedSource = None
        self.GroupWorkSource = self.SourceController.GetSource(id = groupWrkSrc)
        
        self._type = destType
        self._relay = RelayTuple(Up=rly[0], Down=rly[1])
        self._AssignedVidInput = 0
        self._AssignedAudInput = 0
        self._AdvSelectBtn = None
        self._AdvCtlBtn = None
        self._AdvAudBtn = None
        self._AdvAlertBtn = None
        self._AdvScnBtn = None
        self._MatrixRow = None
        
    def AssignSource(self, source: Source) -> None:
        self.AssignedSource = source
        self._AssignedVidInput = source.Input
        self._AssignedAudInput = source.Input
        self.UpdateAdvUI()
        
    def AssignMatrix(self, input: int, tieType: str='AV') -> None:
        if tieType != 'Aud' or tieType != 'Vid' or tieType != 'AV':
            raise ValueError("TieType must either be 'AV', 'Aud', or 'Vid'")
        self.AssignedSource = None
        self.UpdateAdvUI()
        if tieType == 'Vid' or tieType == 'AV':
            self._AssignedVidInput = input
        if tieType == 'Aud' or tieType == 'AV':
            self._AssignedAudInput = input
            
    def GetMatrix(self) -> None:
        return MatrixTuple(Vid=self._AssignedVidInput, Aud=self._AssignedAudInput)
    
    def AssignAdvUI(self, ui: Dict[str, Union[Button, Label]]) -> None:
        self._AdvSelectBtn = ui['select']
        self._AdvCtlBtn = ui['ctl']
        self._AdvAudBtn = ui['aud']
        self._AdvAlertBtn = ui['alert']
        self._AdvScnBtn = ui['scn']
        self._AdvLabel = ui['label']
        
        # set distination label text
        self._AdvLabel.SetText(self.Name)
        
        # clear selected source text
        self._AdvSelectBtn.SetText("") 
        
        @event(self._AdvSelectBtn, 'Pressed')
        def advSelectHandler(button, action):
            curSource = self.SourceController.SelectedSource
            self.SourceController.SwitchSources(curSource, [self])
            self.UpdateAdvUI()
            
        # Source Control Buttons
        self._AdvCtlBtn.SetVisible(False)
        self._AdvCtlBtn.Enabled(False)
        
        @event(self._AdvCtlBtn, 'Pressed')
        def advSrcCtrHandler(button, action):
            # configure source control page
            # TODO: configure the source control page
            
            # show source control page
            self.SourceController.UIHost.ShowPage(self.AssignedSource._advSourceControlPage)
        
        # Destination Audio Buttons
        self._AdvAudBtn.SetState(1)
        
        @event(self._AdvAudBtn, ['Tapped', 'Released'])
        def advAudHandler(button, action):
            if action == "Tapped":
                # TODO: handle system audio changes
                if button.State == 0: # system audio unmuted
                    pass # deselect this destination as the system audio follow
                elif button.State == 1: # system audio muted
                    pass # select this destination as the system audio follow, deselect any other destination as the system audio follow
                elif button.State == 2: # local audio unmuted
                    pass # mute local audio
                elif button.State == 3: # local audio muted
                    pass # unmute local audio
            elif action == "Released":
                if (button.State == 0 or button.State == 1) \
                and self._type == 'mon':
                    # TODO: if this destination is the system audio follow, unfollow
                    muteState = 0 # TODO: get current mute state of the destination monitor
                    if muteState:
                        # TODO: set destination to unmute
                        button.SetState(2)
                    else:
                        # TODO: set mute
                        button.SetState(3)
                elif (button.State == 2 or button.State == 3):
                    button.SetState(1)
        
        # Destination Alert Buttons
        self._AdvAlertBtn.SetVisible(False)
        self._AdvAlertBtn.Enabled(False)
        
        @event(self._AdvAlertBtn, 'Pressed')
        def destAlertHandler(button, action):
            vars.TP_Lbls['SourceAlertLabel'] = self.AssignedSource.AlertText
            self.SourceController.UIHost.ShowPopup('Modal-SrcErr')
            
        @Timer(2)
        def SourceAlertHandler(timer, count) -> None:
            # Does current source for this destination have an alert flag
            if self.AssignedSource.AlertFlag:
                self._AdvAlertBtn.SetVisible(True)
                self._AdvAlertBtn.Enabled(True)
                self._AdvAlertBtn.SetBlinking('Medium', [0,1])
                if self.SourceController.PrimaryDestination == self and vars.ActCtl.CurrentActivity != 'adv_share':
                    vars.TP_Lbls['SourceAlertLabel'] = self.AssignedSource.AlertText
            else:
                self._AdvAlertBtn.SetVisible(False)
                self._AdvAlertBtn.Enabled(False)
                self._AdvAlertBtn.SetState(1)
                if self.SourceController.PrimaryDestination == self and vars.ActCtl.CurrentActivity != 'adv_share':
                    vars.TP_Lbls['SourceAlertLabel'] = ''
        
        # Screen Control Buttons
        if self._type == "proj+scn":
            self._AdvScnBtn.SetVisible(True)
            self._AdvScnBtn.Enabled(True)
        else:
            self._AdvScnBtn.SetVisible(False)
            self._AdvScnBtn.Enabled(False)
            
        @event(self._AdvScnBtn, 'Pressed')
        def destScnHandler(button, action):
            # Configure Screen Control Modal
            # TODO: Configure screen control modal
            # Show Screen Control Modal
            self.SourceController.UIHost.ShowPopup('Modal-ScnCtl')
    
    def UpdateAdvUI(self) -> None:
        curSource = self.SourceController.SelectedSource
        
        self._AdvSelectBtn.SetText(curSource.Name)
        
        if curSource.advSrcCtl == None:
            self._AdvCtlBtn.SetVisible(False)
            self._AdvCtlBtn.Enabled(False)
        else:
            self._AdvCtlBtn.SetVisible(True)
            self._AdvCtlBtn.Enabled(True)
            
class SourceController:
    def __init__(self, 
                 UIHost: UIDevice, 
                 sourceDict: Dict[str, Union[MESet, List[Button]]],
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
        self.SelectedSource = None
        
        # Private Properties
        self._sourceBtns = sourceDict['select']
        self._sourceInds = sourceDict['indicator']
        self._arrowBtns = sourceDict['arrows']
        self._offset = 0
        self._advLayout = self.GetAdvShareLayout()
        self._none_source = Source('none', 'None', 0, 0)
        self._DisplaySrcList = self.UpdateDisplaySourceList()
        self._Matrix = MatrixController(self, matrixDict['btns'], matrixDict['ctls'], matrixDict['del'])
        
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
            if vars.ActCtl.CurrentActivity != "adv_share": 
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
        
        try:           
            destDict['select'] = vars.TP_Btns['Disp-Select-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['ctl'] = vars.TP_Btns['Disp-Ctl-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['aud'] = vars.TP_Btns['Disp-Aud-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['alert'] = vars.TP_Btns['Disp-Alert-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['scn'] = vars.TP_Btns['Disp-Scn-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['label'] = vars.TP_Lbls['DispAdv-{p},{r}'.format(p = location.Pos, r = location.Row)]
            return destDict
        except:
            raise KeyError("At least one destination button not found.")
    
    def _GetPositionByBtnName(self, btnName: str) -> LayoutTuple:
        btnLoc = btnName[-3:]
        btnPR = btnLoc.split(',')
        return LayoutTuple(Row = btnPR[1], Pos = btnPR[0])
    
    def GetAdvShareLayout(self) -> str:
        layout = {}
        for dest in self.Destinations:
            r = str(dest.AdvLayoutPosition.Row)
            if type(layout[r]) == type([]):
                layout[r].append(dest)
            else:
                layout[r] = [dest]
                
        rows = []
        i = 0
        while i < len(layout.keys()):
            rows.append(len(layout[str(i)]))
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
            for src in self.Source:
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
        srcNone = {"id": "none", "name": "None", "icon": 0, "input": 0}
        
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
            btn.SetText[self._DisplaySrcList[offsetIter].Name]
            offsetIter += 1
            
        if len(self._DisplaySrcList) <= 5:
            self.UIHost.ShowPopup('Menu-Source-{}'.format(len(self._DisplaySrcList)))
        else:
            # enable/disable previous arrow
            if self._offset == 0:
                self._arrowBtns[0].setEnable(False)
                self._arrowBtns[0].SetState(2)
            else:
                self._arrowBtns[0].setEnable(True)
                self._arrowBtns[0].SetState(0)
            # enable/disable next arrow
            if (self._offset + 5) >= len(self._DisplaySrcList):
                self._arrowBtns[1].setEnable(False)
                self._arrowBtns[1].SetState(2)
            else:
                self._arrowBtns[1].setEnable(True)
                self._arrowBtns[1].SetState(0)
            
            self.UIHost.ShowPopup('Menu-Source-5+')
            
        # reset currently selected source
        currentSourceIndex = self.GetSourceIndexByID(vars.ActCtl.CurrentActivity)
        
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
            srcNum = srcObj.Input
        elif type(src) == Source:
            srcNum = src.Input
        elif type(src) == int:
            srcNum = int
        else:
            raise TypeError("Source must be a source object, source name string, source Id string, or switcher input integer")
        # TODO: Update Matrix (send matrix tie commands to the matrix rows being affected)
        if type(dest) == str and dest == 'All':
            for d in self.Destinations:
                d.AssignSource(None)
                d.AssignMatrix(srcNum, mode)
            # TODO: send source change command
        elif type(dest) == List:
            for d in dest:
                if type(d) == Destination:
                    d.AssignSource(None)
                    d.AssignMatrix(srcNum, mode)
                    # TODO: send source change command
                elif type(d) == str:
                    destObj = self.GetDestination(id = d, name = d)
                    destObj.AssignSource(srcObj)
                    # TODO: send source change command
                elif type(d) == int:
                    # TODO: send source change command
                    pass
            

        # TODO: Update other Adv UI Buttons

class MatrixController:
    def __init__(self,
                 srcCtl: SourceController,
                 matrixBtns: List[Button],
                 matrixCtls: MESet,
                 matrixDelAll: Button,
                 inputLabels: List[Label],
                 outputLabels: List[Label]) -> None:
        self.SourceController = srcCtl
        self.Mode = 'AV'
        
        matrixRows = {}
        for btn in matrixBtns:
            row = btn.Name[-1]
            if type(matrixRows[row]) != List:
                matrixRows[row] = [btn]
            else:
                matrixRows[row].append(btn)

        self._rows = {}
        for r in matrixRows:
            self._rows[int(r)] = MatrixRow(self, matrixRows[r], int(r))
        
        for dest in self.SourceController.Destinations:
            dest._MatrixRow = self._rows[dest.Output]
            
        self._ctls = matrixCtls
        self._del = matrixDelAll
        self._inputLbls = inputLabels
        self._outputLbls = outputLabels
        self._stateDict = {
            'AV': 3,
            'Aud': 2,
            'Vid': 1,
            'untie': 0
        }
        
        @event(self._ctls.Objects, 'Pressed')
        def matrixModeHandler(button: Button, action: str):
            if button.Name.endswith('AV'):
                self.Mode = 'AV'
            elif button.Name.endswith('Audio'):
                self.Mode = 'Aud'
            elif button.Name.endswith('Vid'):
                self.Mode = 'Vid'
            elif button.Name.endswith('Untie'):
                self.Mode = 'untie'
        
        @event(self._del, 'Pressed')
        def matrixDelAllTiesHandler(button: Button, action: str):
            for row in self._rows:
                for btn in row.Objects:
                    btn.SetState(0)

            self.SourceController.MatrixSwitch(self.SourceController._none_source)
            
        for inLbl in self._inputLbls:
            inLbl.SetText('Not Connected')
        for src in self.SourceController.Sources:
            self._inputLbls[src.Input - 1].SetText(src.Name)
            
        for outLbl in self._outputLbls:
            outLbl.SetText('Not Connected')
        for dest in self.SourceController.Destinations:
            self._outputLbls[dest.Output - 1].SetText(dest.Name)
        
class MatrixRow:
    def __init__(self,
                 Matrix: MatrixController,
                 rowBtns: List[Button],
                 output: int) -> None:
        
        self.Matrix = Matrix
        self.MatrixOutput = output
        self.VidSelect = 0
        self.AudSelect = 0
        self.Objects = rowBtns
        
        # Overload matrix row buttons with Input property
        for btn in self.Objects:
            regex = r"Tech-Matrix-(\d+),(\d+)"
            re_match = re.match(regex, btn.Name)
            # 0 is full match, 1 is input, 2 is output
            btn.Input = re_match.group(1)
        
        @event(self.Objects, 'Pressed')
        def matrixSelectHandler(button: Button, action: str):
            # send switch commands
            if self.Matrix.Mode == "untie":
                self.Matrix.SourceController.MatrixSwitch(0, self.MatrixOutput, self.Matrix.Mode)
            else:
                self.Matrix.SourceController.MatrixSwitch(btn.Input, self.MatrixOutput, self.Matrix.Mode)
            
            # set pressed button's feedback
            button.SetState(self.Matrix._stateDict[self.Matrix.Mode])
            button.SetText(self.Matrix.Mode)
            
            self._UpdateRowBtns(button, self.Matrix.Mode)
        
    def _UpdateRowBtns(self, modBtn: Button, tieType: str="AV") -> None:
        for btn in self.Objects:
            if btn != modBtn:
                if tieType == 'AV':
                    btn.SetState(0) # untie everything else in output row
                    btn.SetText('')
                elif tieType == 'Aud':
                    if btn.State == 2: # Button has Audio tie, untie button
                        btn.SetState(0)
                        btn.SetText('')
                    elif btn.State == 3: # Button has AV tie, untie audio only
                        btn.SetState(1)
                        btn.SetText('Vid')
                elif tieType == 'Vid':
                    if btn.State == 1: # Button has Video tie, untie button
                        btn.SetState(0)
                        btn.SetText('')
                    elif btn.State == 3: # Button has AV tie, untie video only
                        btn.SetState(2)
                        btn.SetText('Aud')
    
    def MakeTie(self, input: int, tieType: str="AV") -> None:
        if not (tieType == 'AV' or tieType == 'Aud' or tieType == 'Vid'):
            raise ValueError("TieType must be one of 'AV', 'Aud', or 'Vid'")
        
        modBtn = self.Objects[input]
        modBtn.SetState(self.Matrix._stateDict[tieType])
        modBtn.SetText(tieType)
        
        self._UpdateRowBtns(modBtn, tieType)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------


## End Function Definitions ----------------------------------------------------



