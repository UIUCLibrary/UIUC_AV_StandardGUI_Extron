################################################################################
# Copyright © 2023 The Board of Trustees of the University of Illinois
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

## Begin Imports ---------------------------------------------------------------

#### Type Checking
from typing import TYPE_CHECKING, List, Dict, Tuple, Union
if TYPE_CHECKING: # pragma: no cover
    from modules.project.SystemHost import SystemController
    from modules.project.Devices import SystemHardwareController
    from modules.project.Devices.Classes import Destination, Source

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import isinstanceEx, SortKeys, Logger
from modules.project.MixIns import InitializeMixin
from modules.project.PrimitiveObjects import MatrixTie, MatrixAction, TieType, ActivityMode
import Constants
import Variables
import System

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class SourceController(InitializeMixin, object):
    def __init__(self, SystemHost: 'SystemController') -> None:
        InitializeMixin.__init__(self, self.__Initialize)
        
        self.SystemHost = SystemHost
        
        self.Switcher = self.SystemHost.Devices[self.SystemHost.PrimarySwitcherId]
        self.PrimaryDestination = self.SystemHost.Devices[self.SystemHost.PrimaryDestinationId]
        self.DefaultSource = self.SystemHost.Devices[self.SystemHost.DefaultSourceId]
        
        self.__MenuBlankBtns = {}
        
        if Variables.TESTING:
            self.__TEST_video = {}
            self.__TEST_audio = {}
        
    @property
    def Sources(self) -> List['Source']:
        return [src.Source for src in self.SystemHost.Devices.Sources]
    
    @Sources.setter
    def Sources(self, val) -> None:
        raise AttributeError('Setting SourceController.Sources is disallowed.')
    
    @property
    def MenuSources(self) -> List['Source']:
        srcs = self.Sources
        if System.CONTROLLER.ActCtl.CurrentActivity == ActivityMode.AdvShare:
            srcs.insert(0, Constants.BLANK_SOURCE)
            
    @MenuSources.setter
    def MenuSources(self) -> None:
        raise AttributeError('Setting SourceController.MenuSources is disallowed.')
    
    @property
    def Destinations(self) -> List['Destination']:
        return [dest.Destination for dest in self.SystemHost.Devices.Destinations]
    
    @Destinations.setter
    def Destinations(self, val) -> None:
        raise AttributeError('Setting SourceController.Destinations is disallowed.')
    
    @property
    def MatrixSize(self) -> Tuple[int, int]:
        return self.Switcher.interface.MatrixSize
    
    @MatrixSize.setter
    def MatrixSize(self, val) -> None:
        raise AttributeError('Setting MatrixSize is disallowed.')
    
    def RemoveBlankBtn(self) -> None:
        for uiDev in self.SystemHost.UIDevices:
            if self.__MenuBlankBtns[uiDev.Id] in uiDev.Interface.Objects.ControlGroups['Source-Select'].RefObjects:
                uiDev.Interface.Objects.ControlGroups['Source-Select'].RemoveRef(self.__MenuBlankBtns[uiDev.Id])
            uiDev.Interface.Objects.ControlGroups['Source-Select'].ShowPopup()
            uiDev.Interface.Objects.ControlGroups['Source-Select'].LoadButtonView()
    
    def AddBlankBtn(self) -> None:
        for uiDev in self.SystemHost.UIDevices:
            if self.__MenuBlankBtns[uiDev.Id] not in uiDev.Interface.Objects.ControlGroups['Source-Select'].RefObjects:
                uiDev.Interface.Objects.ControlGroups['Source-Select'].PrependRef(self.__MenuBlankBtns[uiDev.Id])
            uiDev.Interface.Objects.ControlGroups['Source-Select'].ShowPopup()
            uiDev.Interface.Objects.ControlGroups['Source-Select'].LoadButtonView()
            
    def __Initialize(self) -> None:
        for uiDev in self.SystemHost.UIDevices:
            self.__MenuBlankBtns[uiDev.Id] = [refBtn for refBtn in uiDev.Interface.Objects.ControlGroups['Source-Select'].RefObjects if refBtn.srcId == 'blank'][0]
        
        self.RemoveBlankBtn()
        
        if Variables.TESTING:
            Logger.Debug('Setting TESTING MATRIX:', self.MatrixSize)
            for i in range(self.MatrixSize[1]):
                self.__TEST_video[i] = 0
                self.__TEST_audio[i] = 0
    
    def __GetOutputNumberList(self) -> List[int]:
        rtnList = []
        for dest in self.SystemHost.Devices.Destinations:
            rtnList.append(dest.Destination.Output)
        
        rtnList.sort()
        return rtnList
    
    def GetMatrixLabels(self) -> Dict[str, List[Tuple[int, str]]]:
        rtnDict = {'Inputs': [], 'Outputs': []}
        
        for dest in self.SystemHost.Devices.Destinations:
            rtnDict['Outputs'].append((dest.Destination.Output, dest.Name))
            
        for src in self.SystemHost.Devices.Sources:
            rtnDict['Inputs'].append((src.Source.Input, src.Name))
    
        rtnDict['Inputs' ].sort(key = SortKeys.MatrixLabelSort)
        rtnDict['Outputs'].sort(key = SortKeys.MatrixLabelSort)
        
        return rtnDict
    
    def GetCurrentSources(self, update=True) -> Dict['Destination', MatrixTie]:
        if update:
            self.Switcher.interface.Update("OutputTieStatus")
    
        rtnDict = {}
        for outputNum in self.__GetOutputNumberList():
            rtnDict[self.SystemHost.Devices.GetDestinationByOutput(outputNum)] = self.GetCurrentSourceForDestination(outputNum, update=False)

        return rtnDict
    
    def GetCurrentSourceForDestination(self, 
                                       dest: Union[int, str, 'Destination', 'SystemHardwareController'], 
                                       update=True) -> MatrixTie:
        if update:
            self.Switcher.interface.Update("OutputTieStatus")
        
        if isinstance(dest, int):
            outputNum = dest
        elif isinstance(dest, str):
            try:
                output = self.SystemHost.Devices.GetDestination(id = dest)
            except LookupError:
                try:
                    output = self.SystemHost.Devices.GetDestination(name = dest)
                except LookupError:
                    raise LookupError('String ("{}") not found as a destination Name or Id'.format(dest))
            
            outputNum = output.Output
        elif isinstanceEx(dest, 'Destination'):
            outputNum = dest.Output
        elif isinstanceEx(dest, 'SystemHardwareController'):
            outputNum = dest.Destination.Output
        
        AudQual = {'Output': outputNum, 'Tie Type': TieType.Audio.name}
        VidQual = {'Output': outputNum, 'Tie Type': TieType.Video.name}
        
        if Variables.TESTING:
            Logger.Debug('Test Data - Video', self.__TEST_video, VidQual['Output'])
            Logger.Debug('Test Data - Audio', self.__TEST_audio, AudQual['Output'])
            videoNum = self.__TEST_video.get(VidQual['Output'], 0)
            audioNum = self.__TEST_audio.get(AudQual['Output'], 0)
        else:
            videoNum = self.Switcher.interface.ReadStatus("OutputTieStatus", VidQual)
            audioNum = self.Switcher.interface.ReadStatus("OutputTieStatus", AudQual)
        
        return MatrixTie(video=self.SystemHost.Devices.GetSourceByInput(videoNum), 
                          audio=self.SystemHost.Devices.GetSourceByInput(audioNum))

    def MatrixAction(self, action: Union[MatrixAction, List[MatrixAction]]) -> Dict['Destination', MatrixTie]:
        if isinstance(action, list):
            for act in action:
                self.MatrixAction(act)
        elif isinstance(action, MatrixAction):
            qual = {'Input': action.input, 'Output': action.output, 'Tie Type': action.type.name}
            
            if Variables.TESTING:
                Logger.Debug("(Test) Sending Matrix Tie Command", "Value=None", 'Qualifier={}'.format(qual), separator=' | ')
                self.__TEST_Set_MatrixTieCommand(qual)
            else:
                self.Switcher.interface.Set('MatrixTieCommand', None, qual)
            
            outputList = [outputHw.MatrixOutput for outputHw in list(self.Switcher.interface.VirtualOutputDevices.values())]
            Logger.Log("Validating output", "action.output", action.output, "outputList", outputList, 'result', (action.output == 'all' or action.output in outputList))
            # update source menu
            if action.output == 'all' or\
                action.output in outputList:
                    newSource = self.SystemHost.Devices.GetSourceByInput(action.input)
                    sourceRefBtn = "Source-Select-Ref-{}".format(newSource.Id)
                    for uiDev in self.SystemHost.UIDevices:
                        sourceSelect = uiDev.Interface.Objects.ControlGroups['Source-Select']
                        sourceSelect.SetCurrentRef(sourceRefBtn)
        else:
            raise ValueError('actions must be a MatrixAction namedtuple or list of these')
        
        return self.GetCurrentSources()

    def __TEST_Set_MatrixTieCommand(self, qual) -> None:
        if qual['Output'] == 'all':
            for vidOutput in self.__TEST_video.keys():
                if qual['Tie Type'] == TieType.AudioVideo.name or qual['Tie Type'] == TieType.Video.name:
                    self.__TEST_video[vidOutput] = qual['Input']
                elif qual['Tie Type'] == TieType.Untie.name:
                    self.__TEST_video[vidOutput] = 0
            for audOutput in self.__TEST_audio.keys():
                if qual['Tie Type'] == TieType.AudioVideo.name or qual['Tie Type'] == TieType.Audio.name:
                    self.__TEST_audio[audOutput] = qual['Input']
                elif qual['Tie Type'] == TieType.Untie.name:
                    self.__TEST_audio[audOutput] = 0
        else:
            if qual['Tie Type'] == TieType.AudioVideo.name:
                self.__TEST_video[qual['Output']] = qual['Input']
                self.__TEST_audio[qual['Output']] = qual['Input']
            elif qual['Tie Type'] == TieType.Audio.name:
                self.__TEST_audio[qual['Output']] = qual['Input']
            elif qual['Tie Type'] == TieType.Video.name:
                self.__TEST_video[qual['Output']] = qual['Input']
            elif qual['Tie Type'] ==  TieType.Untie.name:
                self.__TEST_video[qual['Output']] = 0
                self.__TEST_audio[qual['Output']] = 0

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



