from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING:
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice

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
from collections import namedtuple

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from uofi_gui.sourceControls.destinations import Destination
from uofi_gui.sourceControls.sources import Source
from uofi_gui.sourceControls.matrix import MatrixController, MatrixRow

from hardware.mersive_solstice_pod import PodFeedbackHelper

from utilityFunctions import Log, RunAsync, debug, DictValueSearchByKey

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------
RelayTuple = namedtuple('RelayTuple', ['Up', 'Down'])
LayoutTuple = namedtuple('LayoutTuple', ['Row', 'Pos'])
MatrixTuple = namedtuple('MatrixTuple', ['Vid', 'Aud'])

class SourceController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:
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
        
        # TODO: Figure out communicating source switch feedback across UIHost.SrcCtls
        
        # Public Properties
        # Log('Set Public Properties')
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.UIHost.Lbls['SourceAlertLabel'].SetText('')
        
        self.Sources = []
        for src in self.GUIHost.Sources:
            srcObj = Source(self,
                            src['id'], 
                            src['name'], 
                            src['icon'], 
                            src['input'], 
                            src['alert'],
                            src['src-ctl'], 
                            src['adv-src-ctl'])
            self.Sources.append(srcObj)
            if src.get('srcObj') is None:
                src['srcObj'] = {}
            src['srcObj'][self.UIHost.Id] = srcObj
            
            
        self.Destinations = []
        for dest in self.GUIHost.Destinations:
            destObj = Destination(self,
                                  dest['id'],
                                  dest['name'],
                                  dest['output'],
                                  dest['type'],
                                  dest['rly'],
                                  dest['group-work-src'],
                                  dest['adv-layout'])
            self.Destinations.append(destObj)
            if dest.get('destObj') is None:
                dest['destObj'] = {}
            dest['destObj'][self.UIHost.Id] = destObj
        
        self.PrimaryDestination = self.GetDestination(id = self.GUIHost.PrimaryDestinationId)
        self.SelectedSource = None
        self.Privacy = False
        self.OpenControlPopup = None
        
        # Private Properties
        # Log('Set Private Properties')
        self._sourceBtns = self.UIHost.Btn_Grps['Source-Select']
        self._sourceInds = self.UIHost.Btn_Grps['Source-Indicator']
        self._arrowBtns = \
            [
                self.UIHost.Btns['SourceMenu-Prev'],
                self.UIHost.Btns['SourceMenu-Next']
            ]
        self._privacyBtn = self.UIHost.Btns['Privacy-Display-Mute']
        self._sndToAllBtn = self.UIHost.Btns['Send-To-All']
        self._rtnToGrpBtn = self.UIHost.Btns['Return-To-Group']
        self._offset = 0
        self._advLayout = self.GetAdvShareLayout()
        self._none_source = Source(self, 'none', 'None', 0, 0, None, None)
        self._DisplaySrcList = self.UpdateDisplaySourceList()
        self._Matrix = MatrixController(self,
                                        DictValueSearchByKey(self.UIHost.Btns, r'Tech-Matrix-\d+,\d+', regex=True),
                                        self.UIHost.Btn_Grps['Tech-Matrix-Mode'],
                                        self.UIHost.Btns['Tech-Matrix-DeleteTies'],
                                        DictValueSearchByKey(self.UIHost.Lbls, r'MatrixLabel-In-\d+', regex=True),
                                        DictValueSearchByKey(self.UIHost.Lbls, r'MatrixLabel-Out-\d+', regex=True))
        
        for dest in self.Destinations: # Set advanced gui buttons for each destination
            dest.AssignAdvUI(self._GetUIForAdvDest(dest))
            
        self.MatrixSwitch(0, 'All', 'untie')
        
        # Configure Source Selection Buttons
        # Log('Create Class Events')
        @event(self._sourceBtns.Objects, 'Pressed')
        def sourceBtnHandler(button: 'Button', action: str):
            self.UIHost.Lbls['SourceAlertLabel'].SetText('')
            
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
            if self.GUIHost.ActCtl.CurrentActivity != "adv_share":
                if self.GUIHost.ActCtl.CurrentActivity == 'share':
                    self.SwitchSources(self.SelectedSource)
                elif self.GUIHost.ActCtl.CurrentActivity == 'group_work':
                    self.SwitchSources(self.SelectedSource, [self.PrimaryDestination])
                    
                page = self.SelectedSource.SourceControlPage 
                if page == 'PC':
                    page = '{p}_{c}'.format(p=page, c=len(self.GUIHost.Cameras))
                elif page == 'WPD':
                    PodFeedbackHelper(self.SelectedSource.Id, blank_on_fail=True)
                
                self.UIHost.ShowPopup("Source-Control-{}".format(page))

        @event(self._arrowBtns, 'Pressed')
        def sourcePageHandler(button: 'Button', action: str):
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

        @event(self.UIHost.Btns['Modal-Close'], 'Pressed')
        def modalCloseHandler(button: 'Button', action: str):
            self.UIHost.HidePopup('Modal-SrcCtl-WPD')
            self.UIHost.HidePopup('Modal-SrcCtl-Camera')
            self.UIHost.HidePopup('Modal-SrcErr')
            self.UIHost.HidePopup('Modal-ScnCtl')
            self.OpenControlPopup = None
            
        @event(self._privacyBtn, 'Pressed')
        def PrivacyHandler(button: 'Button', action: str):
            self.TogglePrivacy()
    
        @event(self._sndToAllBtn, ['Pressed', 'Released'])
        def SendToAllHandler(button: 'Button', action: str):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                self.SwitchSources(self.SelectedSource)
                @Wait(3)
                def SendToAllBtnFeedbackWait():
                    button.SetState(0)
                    
        @event(self._rtnToGrpBtn, ['Pressed', 'Released'])
        def ReturnToGroupHandler(button: 'Button', action: str):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                self.SelectSource(self.PrimaryDestination.GroupWorkSource)
                for dest in self.Destinations:
                    self.SwitchSources(dest.GroupWorkSource, [dest])
                
                @Wait(3)
                def SendToAllBtnFeedbackWait():
                    button.SetState(0)
                    
        @event(self.UIHost.Btns['WPD-ClearPosts'], ['Pressed', 'Released'])
        def WPDClearPostsHandler(button: 'Button', action: str):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                if self.GUIHost.ActCtl.CurrentActivity != 'adv_share':
                    curHW = self.GUIHost.Hardware[self.SelectedSource.Id]
                else:
                    curHW = self.GUIHost.Hardware[self.OpenControlPopup['source'].Id]
                
                curHW.interface.Set('ClearPosts', value=None, qualifier={'hw': curHW})
                
        @event(self.UIHost.Btns['WPD-ClearAll'], ['Pressed', 'Released'])
        def WPDClearAllHandler(button: 'Button', action: str):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                if self.GUIHost.ActCtl.CurrentActivity != 'adv_share':
                    curHW = self.GUIHost.Hardware[self.SelectedSource.Id]
                else:
                    curHW = self.GUIHost.Hardware[self.OpenControlPopup['source'].Id]
                
                curHW.interface.Set('BootUsers', value=None, qualifier={'hw': curHW})
                
    def SourceAlertHandler(self) -> None:
        # Log('Checking Alerts for Src ({})'.format(self.SelectedSource.Name))
        # Does currently selected source have an alert flag
        if self.SelectedSource.AlertFlag:
            # Log('Alerts Found for Src ({})'.format(self.SelectedSource.Name))
            txt = self.SelectedSource.AlertText
            # Log('Text to set: {} ({})'.format(txt, type(txt)))
            self.UIHost.Lbls['SourceAlertLabel'].SetText(txt)
        else:
            # Log('Alerts Found for Src ({})'.format(self.SelectedSource.Name))
            self.UIHost.Lbls['SourceAlertLabel'].SetText('')
    
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
            destDict['select'] = self.UIHost.Btns['Disp-Select-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['ctl'] = self.UIHost.Btns['Disp-Ctl-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['aud'] = self.UIHost.Btns['Disp-Aud-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['alert'] = self.UIHost.Btns['Disp-Alert-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['scn'] = self.UIHost.Btns['Disp-Scn-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['label'] = self.UIHost.Lbls['DispAdv-{p},{r}'.format(p = location.Pos, r = location.Row)]
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
        
        if self.GUIHost.ActCtl.CurrentActivity == 'adv_share':
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
                if self.GUIHost.ActCtl.CurrentActivity in ['adv_share']:
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
                    if self.GUIHost.ActCtl.CurrentActivity in ['adv_share']:
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
                    if self.GUIHost.ActCtl.CurrentActivity in ['adv_share']:
                        dObj.AdvSourceAlertHandler()
        else:
            Log('Oops, something fell through the if/elif. IF - {}; ELIF - {}'.format((type(dest) == str and dest == 'All'),(type(dest) == List)))
                    
        if self.GUIHost.ActCtl.CurrentActivity in ['share', 'group_work']:
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



## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------


## End Function Definitions ----------------------------------------------------



