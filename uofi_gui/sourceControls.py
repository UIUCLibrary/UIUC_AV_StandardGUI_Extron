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
# import utilityFunctions
from utilityFunctions import Log, RunAsync, debug
import vars
import settings

from hardware.mersive_solstice_pod import PodFeedbackHelper

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
        self.SourceControlPage = srcCtl
        self.AdvSourceControlPage = advSrcCtl
        
        self.__AlertText = {}
        self.__AlertIndex = 0
        self.__OverrideAlert = None
        self.__OverrideState = False
        self.__DefaultAlert = alert
        
        self.__AlertTimer = Timer(1, self.__AlertTimerHandler)
        self.__AlertTimer.Stop()

    @property
    def AlertText(self):
        if not self.__OverrideState:
            txt =  list(self.__AlertText.keys())[self.__AlertIndex]
            Log('AlertText: {}'.format(txt))
            self.CycleAlert()
        else:
            txt = self.__OverrideAlert
        return txt
    
    @property
    def AlertBlock(self):
        block = '\n'.join(self.__AlertText)
        block = block.strip()
        if self.__OverrideState:
            block = '{}\n{}'.format(self.__OverrideAlert, block)
        return block
    
    @property
    def Alerts(self):
        count = len(self.__AlertText)
        if self.__OverrideState:
            count += 1
        return count
    
    @property
    def AlertFlag(self):
        if len(self.__AlertText) > 0:
            return True
        elif self.__OverrideState:
            return True
        else:
            return False
    
    def CycleAlert(self):
        self.__AlertIndex += 1
        if self.__AlertIndex >= len(self.__AlertText):
            self.__AlertIndex = 0
    
    def AppendAlert(self, msg: str=None, timeout: int=0) -> None:
        if msg is None:
            msg = self.__DefaultAlert
            
        if timeout > 0:
            self.__AlertText[msg] = timeout
        else: 
            self.__AlertText[msg] = -1
        
        if self.__AlertTimer.State in ['Paused', 'Stopped']:
            self.__AlertTimer.Restart()
        
    def OverrideAlert(self, msg: str, timeout: int=60) -> None:
        self.__OverrideAlert = msg
        self.__OverrideState = True
        if timeout > 0:
            @Wait(timeout)
            def OverrideTimeoutHandler():
                self.__OverrideState = False
    
    def ClearOverride(self):
        self.__OverrideState = False
    
    def ClearAlert(self, msg: str=None):
        if msg is None:
            msg = self.__DefaultAlert
            
        self.__AlertText.pop(msg)
        
        if len(self.__AlertText) == 0:
            self.__AlertTimer.Stop()
    
    def ResetAlert(self) -> None:
        self.__AlertText = {}
        self.__AlertTimer.Stop()
        
    def __AlertTimerHandler(self, timer: Timer, count: int):
        for msg in self.__AlertText.keys():
            if self.__AlertText[msg] > 0:
                self.__AlertText[msg] -= 1
                if self.__AlertText[msg] == 0:
                    self.__AlertText.pop(msg)
        if len(self.__AlertText) == 0:
            timer.Stop()
                
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
        self.Mute = False
        
        self._type = destType
        if type(rly) != type(None):
            self._relay = RelayTuple(Up=rly[0], Down=rly[1])
        else:
            self._relay = RelayTuple(Up=None, Down=None)
        self._AssignedVidInput = 0
        self._AssignedAudInput = 0
        self._AdvSelectBtn = None
        self._AdvCtlBtn = None
        self._AdvAudBtn = None
        self._AdvAlertBtn = None
        self._AdvScnBtn = None
        self._MatrixRow = None
    
    def ToggleDestinationMute(self) -> None:
        # Log('Toggle Destination Mute ({})'.format(self.Name), stack=True)
        if self.Mute:
            self.UnmuteDestination()
        else:
            self.MuteDestination
    
    def MuteDestination(self) -> None:
        # Log('Destination Mute On ({})'.format(self.Name), stack=True)
        self.Mute = True
    
    def UnmuteDestination(self) -> None:
        # Log('Destination Mute Off ({})'.format(self.Name), stack=True)
        self.Mute = False
        
    def AssignSource(self, source: Source) -> None:
        self.AssignedSource = source
        self._AssignedVidInput = source.Input
        self._AssignedAudInput = source.Input
        self.UpdateAdvUI()
        
    def AssignMatrix(self, input: int, tieType: str='AV') -> None:
        if not (tieType == 'Aud' or tieType == 'Vid' or tieType == 'AV' or tieType == 'untie'):
            raise ValueError("TieType must either be 'AV', 'Aud', 'Vid', or 'untie'. Provided TieType: {}".format(tieType))
        
        if tieType == 'AV' or tieType == 'Vid':
            self.AssignedSource = self.SourceController.GetSourceByInput(input)
        else:
            self.AssignedSource = self.SourceController._none_source
            
        if tieType == 'Vid' or tieType == 'AV':
            self._AssignedVidInput = input
        if tieType == 'Aud' or tieType == 'AV':
            self._AssignedAudInput = input
            
        self.UpdateAdvUI()
            
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
            # Log('Adv Select Handler - Source: {}, Destination: {}'
            #                      .format(self.SourceController.SelectedSource.Name,
            #                              self.Name))
            self.SourceController.SwitchSources(self.SourceController.SelectedSource,
                                                [self])
            #self.AssignSource(curSource)
            
        # Source Control Buttons
        self._AdvCtlBtn.SetVisible(False)
        self._AdvCtlBtn.SetEnable(False)
        
        @event(self._AdvCtlBtn, 'Pressed')
        def advSrcCtrHandler(button, action):
            # configure source control page
            modal = 'Modal-SrcCtl-{}'.format(self.AssignedSource.AdvSourceControlPage)
            
            if modal == 'Modal-SrcCtl-WPD':
                PodFeedbackHelper(self.AssignedSource.Id, blank_on_fail=True)
            
            # show source control page
            self.SourceController.UIHost.ShowPopup(modal)
            self.SourceController.OpenControlPopup = {
                'page': modal,
                'source': self.AssignedSource
            }
        
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
        self._AdvAlertBtn.SetEnable(False)
        
        @event(self._AdvAlertBtn, 'Pressed')
        def destAlertHandler(button, action):
            vars.TP_Lbls['SourceAlertLabel'].SetText(self.AssignedSource.AlertText)
            self.SourceController.UIHost.ShowPopup('Modal-SrcErr')
        
        # Screen Control Buttons
        if self._type == "proj+scn":
            self._AdvScnBtn.SetVisible(True)
            self._AdvScnBtn.SetEnable(True)
        else:
            self._AdvScnBtn.SetVisible(False)
            self._AdvScnBtn.SetEnable(False)
            
        @event(self._AdvScnBtn, 'Pressed')
        def destScnHandler(button, action):
            # Configure Screen Control Modal
            # TODO: Configure screen control modal
            # Show Screen Control Modal
            self.SourceController.UIHost.ShowPopup('Modal-ScnCtl')
    
    def UpdateAdvUI(self) -> None:
        # Log('Updating Advanced UI - Dest: {}, Source {}'.format(self.Name, self.AssignedSource.Name))
        
        self._AdvSelectBtn.SetText(self.AssignedSource.Name)
        
        if self.AssignedSource.AdvSourceControlPage == None:
            self._AdvCtlBtn.SetVisible(False)
            self._AdvCtlBtn.SetEnable(False)
        else:
            self._AdvCtlBtn.SetVisible(True)
            self._AdvCtlBtn.SetEnable(True)
            
    def AdvSourceAlertHandler(self) -> None:
        # Log('Checking alerts for Src ({})'.format(self.AssignedSource.Name))
        # Does current source for this destination have an alert flag
        if self.AssignedSource != None and self.AssignedSource.AlertFlag:
            # Log('Alerts Found for Src ({})'.format(self.AssignedSource.Name))
            self._AdvAlertBtn.SetVisible(True)
            self._AdvAlertBtn.SetEnable(True)
            self._AdvAlertBtn.SetBlinking('Medium', [0,1])
        else:
            # Log('No Alerts Found for Src ({})'.format(self.AssignedSource.Name))
            self._AdvAlertBtn.SetVisible(False)
            self._AdvAlertBtn.SetEnable(False)
            self._AdvAlertBtn.SetState(1)
            
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
        # Log('Set Public Properties')
        self.UIHost = UIHost
        vars.TP_Lbls['SourceAlertLabel'].SetText('')
        
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
        self.Privacy = False
        self.OpenControlPopup = None
        
        # Private Properties
        # Log('Set Private Properties')
        self._sourceBtns = sourceDict['select']
        self._sourceInds = sourceDict['indicator']
        self._arrowBtns = sourceDict['arrows']
        self._privacyBtn = vars.TP_Btns['Privacy-Display-Mute']
        self._sndToAllBtn = vars.TP_Btns['Send-To-All']
        self._rtnToGrpBtn = vars.TP_Btns['Return-To-Group']
        self._offset = 0
        self._advLayout = self.GetAdvShareLayout()
        self._none_source = Source(self, 'none', 'None', 0, 0, None, None)
        self._DisplaySrcList = self.UpdateDisplaySourceList()
        self._Matrix = MatrixController(self,
                                        matrixDict['btns'],
                                        matrixDict['ctls'],
                                        matrixDict['del'],
                                        matrixDict['labels']['input'],
                                        matrixDict['labels']['output'])
        
        for dest in self.Destinations: # Set advanced gui buttons for each destination
            dest.AssignAdvUI(self._GetUIForAdvDest(dest))
            
        self.MatrixSwitch(0, 'All', 'untie')
        
        # Configure Source Selection Buttons
        # Log('Create Class Events')
        @event(self._sourceBtns.Objects, 'Pressed')
        def sourceBtnHandler(button, action):
            vars.TP_Lbls['SourceAlertLabel'].SetText('')
            
            # capture last character of button.Name and convert to index
            btnIndex = int(button.Name[-1:]) - 1
            
            # Update button state
            self._sourceBtns.SetCurrent(button)
            
            # Update source indicator
            self._sourceInds.SetCurrent(self._sourceInds.Objects[btnIndex])

            # Get Source Index, Update Selected Source Object
            srcIndex = btnIndex + self._offset
            self.SelectSource(self._DisplaySrcList[srcIndex])

            # advanced share doesn't switch until destination has been selected
            # all other activities switch immediately
            if vars.ActCtl.CurrentActivity != "adv_share":
                if vars.ActCtl.CurrentActivity == 'share':
                    self.SwitchSources(self.SelectedSource)
                elif vars.ActCtl.CurrentActivity == 'group_work':
                    self.SwitchSources(self.SelectedSource, [self.PrimaryDestination])
                    
                page = self.SelectedSource.SourceControlPage 
                if page == 'PC':
                    page = '{p}_{c}'.format(p=page, c=len(settings.cameras))
                elif page == 'WPD':
                    PodFeedbackHelper(self.SelectedSource.Id, blank_on_fail=True)
                
                self.UIHost.ShowPopup("Source-Control-{}".format(page))

        @event(self._arrowBtns, 'Pressed')
        def sourcePageHandler(button, action):
            # capture last 4 characters of button.Name
            btnAction = button.Name[-4:]
            # determine if we are adding or removing offset
            if btnAction == "Prev":
                if self._offset > 0:
                    self._offset -= 1
            elif btnAction == "Next":
                if (self._offset + 5) < len(self._DisplaySrcList):
                    self._offset += 1
            # update the displayed source menu
            self.UpdateSourceMenu()

        @event(vars.TP_Btns['Modal-Close'], 'Pressed')
        def modalCloseHandler(button, action):
            self.UIHost.HidePopup('Modal-SrcCtl-WPD')
            self.UIHost.HidePopup('Modal-SrcCtl-Camera')
            self.UIHost.HidePopup('Modal-SrcErr')
            self.UIHost.HidePopup('Modal-ScnCtl')
            self.OpenControlPopup = None
            
        @event(self._privacyBtn, 'Pressed')
        def PrivacyHandler(button, action):
            self.TogglePrivacy()
    
        @event(self._sndToAllBtn, ['Pressed', 'Released'])
        def SendToAllHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                self.SwitchSources(self.SelectedSource)
                @Wait(3)
                def SendToAllBtnFeedbackWait():
                    button.SetState(0)
                    
        @event(self._rtnToGrpBtn, ['Pressed', 'Released'])
        def ReturnToGroupHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                self.SelectSource(self.PrimaryDestination.GroupWorkSource)
                for dest in self.Destinations:
                    self.SwitchSources(dest.GroupWorkSource, [dest])
                
                @Wait(3)
                def SendToAllBtnFeedbackWait():
                    button.SetState(0)
                    
        @event(vars.TP_Btns['WPD-ClearPosts'], ['Pressed', 'Released'])
        def WPDClearPostsHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                if vars.ActCtl.CurrentActivity != 'adv_share':
                    curHW = vars.Hardware[self.SelectedSource.Id]
                else:
                    curHW = vars.Hardware[self.OpenControlPopup['source'].Id]
                
                curHW.interface.Set('ClearPosts', value=None, qualifier={'hw': curHW})
                
        @event(vars.TP_Btns['WPD-ClearAll'], ['Pressed', 'Released'])
        def WPDClearAllHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                if vars.ActCtl.CurrentActivity != 'adv_share':
                    curHW = vars.Hardware[self.SelectedSource.Id]
                else:
                    curHW = vars.Hardware[self.OpenControlPopup['source'].Id]
                
                curHW.interface.Set('BootUsers', value=None, qualifier={'hw': curHW})
                
    def SourceAlertHandler(self) -> None:
        # Log('Checking Alerts for Src ({})'.format(self.SelectedSource.Name))
        # Does currently selected source have an alert flag
        if self.SelectedSource.AlertFlag:
            # Log('Alerts Found for Src ({})'.format(self.SelectedSource.Name))
            txt = self.SelectedSource.AlertText
            # Log('Text to set: {} ({})'.format(txt, type(txt)))
            vars.TP_Lbls['SourceAlertLabel'].SetText(txt)
        else:
            # Log('Alerts Found for Src ({})'.format(self.SelectedSource.Name))
            vars.TP_Lbls['SourceAlertLabel'].SetText('')
    
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
    
    def TogglePrivacy(self) -> None:
        # Log('Toggle Privacy', stack=True)
        if self.Privacy:
            self.SetPrivacyOff()
        else:
            self.SetPrivacyOn()
    
    def SetPrivacyOn(self) -> None:
        # Log('Privacy On', stack=True)
        self.Privacy = True
        self._privacyBtn.SetBlinking('medium', [1,2])
        for d in self.Destinations:
            if d._type != 'conf':
                d.MuteDestination()
    
    def SetPrivacyOff(self) -> None:
        # Log('Privacy Off', stack=True)
        self.Privacy = False
        self._privacyBtn.SetState(0)
        for d in self.Destinations:
            if d._type != 'conf':
                d.UnmuteDestination()
    
    def GetAdvShareLayout(self) -> str:
        layout = {}
        for dest in self.Destinations:
            r = str(dest.AdvLayoutPosition.Row)
            if r not in layout:
                layout[r] = [dest]
            else:
                layout[r].append(dest)
                
        rows = []
        i = 0
        while i < len(layout.keys()):
            rows.append(len(layout[str(i)]))
            i += 1
        rows.reverse()
        
        return "Source-Control-Adv_{}".format(",".join(str(r) for r in rows))
    
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
                
    def GetDestinationByOutput(self, outputNum: int) -> Destination:
        for dest in self.Destinations:
            if dest.Output == outputNum:
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
                
    def GetSourceByInput(self, inputNum: int) -> Source:
        for src in self.Sources:
            if src.Input == inputNum:
                return src
        return self._none_source
    
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
        # Log('Set Primary Destination - {}'.format(dest), stack=True)
        
        if type(dest) != Destination:
            raise TypeError("Object of class Destination must be provided")
        self.PrimaryDestination = dest
        
    def SelectSource(self, src: Union[Source, str]) -> None:
        if type(src) == Source:
            # Log('Select Source - {}'.format(src.Name), stack=True)
            self.SelectedSource = src
        elif type(src) == str:
            srcObj = self.GetSource(id = src, name = src)
            # Log('Select Source - {}'.format(srcObj.Name), stack=True)
            self.SelectedSource = srcObj
    
    def UpdateDisplaySourceList(self) -> None:
        """Get the current source list

        Returns:
            List: The list of currently displayable source definitions
        """    
        srcList = []
        
        if vars.ActCtl.CurrentActivity == 'adv_share':
            srcList.append(self._none_source)
        srcList.extend(self.Sources)
        
        self._DisplaySrcList = srcList
        
    def UpdateSourceMenu(self) -> None:
        """Updates the formatting of the source menu. Use when the number of sources
        or the pagination of the source bar changes
        """    
        # Log('Updating Source Menu', stack=True)
        
        self.UpdateDisplaySourceList()
        
        offsetIter = self._offset
        # Log('Source Control Offset - {}'.format(self._offset))
        for btn in self._sourceBtns.Objects:
            btn_to_config = self._DisplaySrcList[offsetIter]
            offState = int('{}0'.format(btn_to_config.Icon))
            onState = int('{}1'.format(btn_to_config.Icon))
            self._sourceBtns.SetStates(btn, offState, onState)
            btn.SetText(str(btn_to_config.Name))
            offsetIter += 1
        self._sourceBtns.SetCurrent(None)
        self._sourceInds.SetCurrent(None)
        
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
        # Log('Current Source Index - {}'.format(currentSourceIndex))
        
        btnIndex = currentSourceIndex - self._offset
        # Log('Button Index - {}'.format(btnIndex))
        # if btnIndex > 4:
        #     raise KeyError("Button Index Out of Range")
        
        if btnIndex >= 0 and btnIndex <= 4:
            self._sourceBtns.SetCurrent(self._sourceBtns.Objects[btnIndex])
            self._sourceInds.SetCurrent(self._sourceInds.Objects[btnIndex])
        
    def ShowSelectedSource(self) -> None:
        # Log('Show Selected Source', stack=True)
        if len(self._DisplaySrcList) > 5:
            curSourceIndex = self._DisplaySrcList.index(self.SelectedSource)
            
            if curSourceIndex < self._offset:
                self._offset -= (self._offset - curSourceIndex)
            elif curSourceIndex >= (self._offset + 5):
                self._offset = curSourceIndex - 4
            
            self.UpdateSourceMenu()
    
    @RunAsync
    def SwitchSources(self, src: Union[Source, str], dest: Union[str, List[Union[Destination, str]]]='All') -> None:
        # TODO: Figure out why this function has turned into a complete mess
        if type(dest) == str and dest != 'All':
            raise TypeError("Destination string must be 'All' or a list of Destination objects, names, and/or IDs")
        
        # Log('Switch Sources - Src Type: {}, Dest Type: {}'.format(type(src), type(dest)), stack=True)
        
        if type(src) == str:
            srcObj = self.GetSource(id = src, name = src)
        elif type(src) == Source:
            srcObj = src
        else:
            Log('Oops, something fell through the if/elif. IF - {}; ELIF - {}'.format((type(src) == str),(type(src) == Source)), level='warning')
        
        if type(dest) == str and dest == 'All':
            # Log('Source Switch - Destination: All, Source: {}'.format(srcObj.Name))
            for d in self.Destinations:
                d.AssignSource(srcObj)
                d._MatrixRow.MakeTie(srcObj.Input, 'AV')
                self._Matrix.Hardware.interface.Set('MatrixTieCommand', 
                                                    value=None,
                                                    qualifier={'Input': srcObj.Input, 
                                                            'Output': d.Output,
                                                            'Tie Type': 'Audio/Video'})
                if vars.ActCtl.CurrentActivity in ['adv_share']:
                        d.AdvSourceAlertHandler()
        elif type(dest) == type([]):
            for d in dest:
                if type(d) == Destination:
                    # Log('Source Switch - Destination: {}, Source: {}'.format(d.Name, srcObj.Name))
                    d.AssignSource(srcObj)
                    d._MatrixRow.MakeTie(srcObj.Input, 'AV')
                    self._Matrix.Hardware.interface.Set('MatrixTieCommand', 
                                                        value=None,
                                                        qualifier={'Input': srcObj.Input, 
                                                                   'Output': d.Output,
                                                                   'Tie Type': 'Audio/Video'})
                    if vars.ActCtl.CurrentActivity in ['adv_share']:
                        d.AdvSourceAlertHandler()
                elif type(d) == str:
                    dObj = self.GetDestination(id = d, name = d)
                    # Log('Source Switch - Destination: {}, Source: {}'.format(dObj.Name, srcObj.Name))
                    dObj.AssignSource(srcObj)
                    dObj._MatrixRow.MakeTie(srcObj.Input, 'AV')
                    self._Matrix.Hardware.interface.Set('MatrixTieCommand',  
                                                        value=None,
                                                        qualifier={'Input': srcObj.Input, 
                                                                   'Output': dObj.Output,
                                                                   'Tie Type': 'Audio/Video'})
                    if vars.ActCtl.CurrentActivity in ['adv_share']:
                        dObj.AdvSourceAlertHandler()
        else:
            Log('Oops, something fell through the if/elif. IF - {}; ELIF - {}'.format((type(dest) == str and dest == 'All'),(type(dest) == List)))
                    
        if vars.ActCtl.CurrentActivity in ['share', 'group_work']:
            self.SourceAlertHandler()

    def MatrixSwitch(self, src: Union[Source, str, int], dest: Union[str, List[Union[Destination, str, int]]]='All', mode: str='AV') -> None:
        if type(dest) == str and dest != 'All':
            raise TypeError("Destination must either be 'All' or a list of Destination objects, names, IDs, or switcher output integer")
        
        cmdDict = \
            {
                'Aud': 'Audio',
                'Vid': 'Video',
                'AV': 'Audio/Video'
            }
            
        if type(src) == str:
            srcObj = self.GetSource(id = src, name = src)
            srcNum = srcObj.Input
        elif type(src) == Source:
            srcNum = src.Input
            srcObj = src
        elif type(src) == int:
            srcNum = src
            srcObj = self.GetSourceByInput(src)
        else:
            raise TypeError("Source must be a source object, source name string, source Id string, or switcher input integer")
        
        if mode == 'untie':
            cmdInput = 0
            cmdTieType = 'Audio/Video'
            # TODO: May have to check for existing ties before knowing if this will work
        else:
            cmdInput = srcNum
            cmdTieType = cmdDict[mode]
        
        # Log('Source Object ({}) - Input: {}'.format(srcObj, srcNum))
        
        if type(dest) == str and dest == 'All':
            for d in self.Destinations:
                #d.AssignSource(self._none_source)
                d.AssignMatrix(srcNum, mode)
                d._MatrixRow.MakeTie(srcNum, mode)
                self._Matrix.Hardware.interface.Set('MatrixTieCommand', 
                                                    value=None, 
                                                    qualifier={'Input': cmdInput, 
                                                               'Output': d.Output,
                                                               'Tie Type': cmdTieType})
        elif type(dest) == type([]):
            for d in dest:
                if type(d) == Destination:
                    #d.AssignSource(self._none_source)
                    d.AssignMatrix(srcNum, mode)
                    d._MatrixRow.MakeTie(srcNum, mode)
                    destNum = d.Output
                elif type(d) == str:
                    destObj = self.GetDestination(id = d, name = d)
                    #destObj.AssignSource(self._none_source)
                    destObj.AssignMatrix(srcNum, mode)
                    destObj._MatrixRow.MakeTie(srcNum, mode)
                    destNum = destObj.Output
                elif type(d) == int:
                    destObj = self.GetDestinationByOutput(d)
                    if destObj is not None:
                        #destObj.AssignSource(srcObj)
                        destObj.AssignMatrix(srcNum, mode)
                        destObj._MatrixRow.MakeTie(srcNum, mode)
                    destNum = d
                self._Matrix.Hardware.interface.Set('MatrixTieCommand', 
                                                    value=None, 
                                                    qualifier={'Input': cmdInput, 
                                                               'Output': destNum,
                                                               'Tie Type': cmdTieType})
        else:
            Log('Oops, something fell through the if/elif. IF - {}; ELIF - {}'.format((type(dest) == str and dest == 'All'),(type(dest) == type([]))))

class MatrixController:
    def __init__(self,
                 srcCtl: SourceController,
                 matrixBtns: List[Button],
                 matrixCtls: MESet,
                 matrixDelAll: Button,
                 inputLabels: List[Label],
                 outputLabels: List[Label]) -> None:
        
        # Log('Set Public Properties')
        self.SourceController = srcCtl
        self.Mode = 'AV'
        
        self.Hardware = vars.Hardware[settings.primarySwitcher]
        
        # Log('Create Matrix Rows')
        matrixRows = {}
        for btn in matrixBtns:
            row = int(btn.Name[-1])
            if row not in matrixRows:
                matrixRows[row] = [btn]
            else:
                matrixRows[row].append(btn)

        self._rows = {}
        for r in matrixRows:
            self._rows[r] = MatrixRow(self, matrixRows[r], r)
        
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
        
        self._ctls.SetCurrent(0)
        
        # Log('Create Class Events')
        @event(self._ctls.Objects, 'Pressed')
        def matrixModeHandler(button: Button, action: str):
            self._ctls.SetCurrent(button)
            if button.Name.endswith('AV'):
                self.Mode = 'AV'
            elif button.Name.endswith('Audio'):
                self.Mode = 'Aud'
            elif button.Name.endswith('Vid'):
                self.Mode = 'Vid'
            elif button.Name.endswith('Untie'):
                self.Mode = 'untie'
        
        @event(self._del, ['Pressed','Released'])
        def matrixDelAllTiesHandler(button: Button, action: str):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                for row in self._rows.values():
                    for btn in row.Objects:
                        btn.SetState(0)
                self.SourceController.MatrixSwitch(self.SourceController._none_source, 'All', 'untie')
            
        for inLbl in self._inputLbls:
            inLbl.SetText('Not Connected')
        for src in self.SourceController.Sources:
            for inLbl in self._inputLbls:
                if inLbl.Name.endswith(str(src.Input)):
                    inLbl.SetText(src.Name)
            
        for outLbl in self._outputLbls:
            outLbl.SetText('Not Connected')
        for dest in self.SourceController.Destinations:
            for outLbl in self._outputLbls:
                if outLbl.Name.endswith(str(dest.Output)):
                    outLbl.SetText(dest.Name)
        
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
            btn.Input = int(re_match.group(1))
        
        @event(self.Objects, 'Pressed')
        def matrixSelectHandler(button: Button, action: str):
            # send switch commands
            if self.Matrix.Mode == "untie":
                self.Matrix.SourceController.MatrixSwitch(0, [self.MatrixOutput], self.Matrix.Mode)
            else:
                # Log("Selected button input - {}".format(button.Input))
                self.Matrix.SourceController.MatrixSwitch(button.Input, [self.MatrixOutput], self.Matrix.Mode)
            
            # set pressed button's feedback
            self.MakeTie(button, self.Matrix.Mode)
        
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
    
    def MakeTie(self, input: Union[int, Button], tieType: str="AV") -> None:
        if not (tieType == 'AV' or tieType == 'Aud' or tieType == 'Vid' or tieType == 'untie'):
            raise ValueError("TieType must be one of 'AV', 'Aud', 'Vid', or 'untie")
        
        if input == 0:
            for btn in self.Objects:
                btn.SetState(0)
                btn.SetText('')
        else:
            if type(input) == int:
                for btn in self.Objects:
                    if btn.Input == input:
                        modBtn = btn
            elif type(input) == Button:
                modBtn = input
                
            modBtn.SetState(self.Matrix._stateDict[tieType])
            modBtn.SetText(tieType)
            if tieType == 'untie':
                @Wait(5)
                def untiedTextHandler():
                    modBtn.SetText('')
            
            self._UpdateRowBtns(modBtn, tieType)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------


## End Function Definitions ----------------------------------------------------



