import wx
import os
import sys
import pandas as pd
import multiprocessing as mp
import queue
import GUIDesign
import threading
import importlib
import importlib.util
from inspect import getmembers, isfunction,getcomments

import wx

# from STMMacroQueue.GUIDesign import MacroSettingsDialog
from time import time as timer

from Dialogs import MyMacroDialog as MacroDialog
from Dialogs import MyMacroSettingsDialog as MacroSettingsDialog
from Dialogs import MyStartMacroDialog as StartMacroDialog
from Dialogs import MyChooseSoftwareDialog as ChooseSoftwareDialog
# from GUIDesign import MacroSettingsDialog

from Macros import *

# from GUIDesign import MacroDialog
from inspect import getmembers, isfunction

# They all go in try/except just in case the required packages aren't installed for one of them 
# (e.g. you can still use RHK's functions even without win32com which you need for CreaTec)
try:
    import Functions.RHK as RHKFunctions
except:
    pass

try:
    import Functions.CreaTec as CreaTecFunctions
except:
    pass

try:
    import Functions.SXM as SXMFunctions
except:
    pass

try:
    import Functions.General as GeneralFunctions
except:
    pass

import json


IconFileName = "MacroQueueIcon.ico"


# BUG:
# After edit macro, text on wrong side (Not reproducing?)
# Dragging does not always work
# Canceled during move to image start of a dIdV scan and it stopped responding.

# TODO:
# Does this work on a Mac?
# Show number of items in queue in status bar

# If a macro failed, copy it and put it and the top of the queue (Let this be an option)

# Improve the help dialog

# RHK functions
# Scan - Only top down
# RHK Scan doesn't stop
# Set position option (absolute or relative)
# Set bias modulation amplitude




# Don't hold m_FunctionWindow,m_FunctionNameText in self.TheQueue.  The text only needs to be MacroLabel.  The window is only used to set the tooltip


# Have a log dialog that can be opened (but doesn't have to be).  The log dialog shows whatever is printed (or the equivlant)

# Ramping & scanning : set status bar 3
# Progress bar: https://stackoverflow.com/questions/1883528/wxpython-progress-bar

# RHK Scan time wrong



# Save PDF


# In the createc Scan, when I get the Y pixels, it crashes if I haven't set it?  There's no default value? 
# On close, I cancel the scan.  Should I try to prevent that?

VersionNumber = "v1.4.0"
class MainFrame(GUIDesign.MyFrame):
    MacroPaths = {"RHK":"Macros//RHKMacro.json","CreaTec":"Macros//CreaTecMacro.json","SXM":"Macros//SXMMacro.json"}

# Scanning, fine motion, course motion, dI/dV scans, point spectra, tip form, 
    TheQueue = []
    AddToQueue = []
    FunctionsLoaded = []
    Paused = True
    Running = False
    Software = None
    Closing = False
    Editting = False
# my_module = importlib.import_module('os.path')
    def __init__(self):
        application_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        os.chdir(os.path.realpath(application_path))
        self.SavedSettingsFile = 'MacroQueueSettings.csv'
        print(application_path)


        # The GUIDesign is defined in GUIDesign.py as the class MyFrame. It was made with wxFormBuilder
        GUIDesign.MyFrame.__init__(self, parent=None) 
        icon_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), IconFileName)
        if os.path.exists(icon_file):
            icon = wx.Icon(icon_file)
            self.SetIcon(icon)
        self.LoadFunctions()



        # Starts the STM Thread with an Incoming & Outgoing Queue.  Any time-consuming calculations/measurements should be made on this thread.
        try:
            mp.set_start_method('spawn')
        except RuntimeError:
            pass


        self.OutgoingQueue = mp.Queue()
        self.IncomingQueue = mp.Queue()

        self.Process = threading.Thread(target=Thread, args=(self,self.IncomingQueue,self.OutgoingQueue))
        self.Process.start()

        # Read the saved settings file here
        if os.path.exists(self.SavedSettingsFile):
            SettingsSeries = pd.read_csv(self.SavedSettingsFile,names=['key','value'])
            
            self.SettingsDict = SettingsSeries.set_index('key').T.iloc[0].to_dict()
            if "Functions" in self.SettingsDict.keys():
                self.FunctionsLoaded = [string.replace(" ", "").replace("'", "") for string in (self.SettingsDict["Functions"][1:-1].split(','))]
            self.Software = self.SettingsDict["Software"]
            ThisChooseSoftwareDialog = ChooseSoftwareDialog(self,self.FunctionsLoaded)
            ThisChooseSoftwareDialog.SetSoftware(self.Software)
            
            for item in self.m_NotSTMMenu.GetMenuItems():
                if item.GetItemLabel() in self.FunctionsLoaded:
                    item.Check()
                else:
                    item.Check(False)
        else:
            ThisChooseSoftwareDialog = ChooseSoftwareDialog(self)
            ThisChooseSoftwareDialog.ShowModal()
        if self.Software is None:
            self.OnClose()
            return
        



        # Loads the bitmap images
        YBitmapSize = 20
        self.DownBitmap = wx.Bitmap( u"Bitmaps/DownArrow.bmp", wx.BITMAP_TYPE_ANY).ConvertToImage().Scale(20,YBitmapSize).ConvertToBitmap()
        self.UpBitmap = wx.Bitmap( u"Bitmaps/UpArrow.bmp", wx.BITMAP_TYPE_ANY).ConvertToImage().Scale(20,YBitmapSize).ConvertToBitmap()
        self.RemoveBitmap = wx.Bitmap( u"Bitmaps/Remove.bmp", wx.BITMAP_TYPE_ANY).ConvertToImage().Scale(20,YBitmapSize).ConvertToBitmap()

        # Makes the sizer to put the queue
        self.m_FunctionNameSizer = wx.FlexGridSizer( 0, 1, -6, 0 )
        self.m_FunctionNameSizer.AddGrowableCol( 0 )
        self.m_FunctionNameSizer.SetFlexibleDirection( wx.BOTH )
        self.m_FunctionNameSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        self.m_QueueWindow.SetSizer(self.m_FunctionNameSizer)
        dt = MyPanelDropTarget(self.m_QueueWindow,self)
        self.m_QueueWindow.SetDropTarget(dt)
        def OnQueueSize(event):
            # self.m_QueueWindow.Layout()
            self.m_QueueWindow.FitInside()
        self.m_QueueWindow.Bind( wx.EVT_SIZE, OnQueueSize )
        self.AddConnectToQueue()
        self.Show()

    def CheckQueue(self,event):
        # This funtion runs on a timer.  Twice a second.
        try:
            # A try loop to ignore any queue.Empty exceptions 
            Message = self.OutgoingQueue.get(False)
            # get(False) gets the message from the queue but throws an exception if it's empty.
            # get(True) would wait until there's a message
            while Message:
                # The first item in the message is what function to run
                # The second item in the message is the parameters for that function
                if Message[0] == 'SetStatus':
                    self.StatusBar.SetStatusText(*Message[1])
                if Message[0] == 'FunctionFinished':
                    self.Running = False
                    Macro,FunctionPanel,FunctionText = self.TheQueue.pop(0)
                    FunctionPanel.Destroy()
                    self.m_QueueWindow.FitInside()
                if Message[0] == "DontClose":
                    MyMessage = wx.MessageDialog(self,message=Message[1],caption="Do not close!",style=wx.OK)
                    MyMessage.ShowModal()
                    pass
                if Message[0] == "ExceptionThrown":
                    # If there is an exception throw in the STM thread, it gets put here for a pop-up message.
                    if not self.Paused:
                        Macro,FunctionPanel,FunctionText = self.TheQueue.pop(0)
                        exception,FunctionName = Message[1]
                        FunctionPanel.SetBackgroundColour('red')
                        FunctionPanel.Refresh()
                        MyMessage = wx.MessageDialog(self,message=f"There was an error from the function '{FunctionName}' in the Macro '{FunctionText.GetLabel()}':\n\n{exception}",caption=f"Error - {FunctionText.GetLabel()}")
                        self.Running = False
                        self.Pause()
                        MyMessage.ShowModal()
                        FunctionPanel.Destroy()
                        self.m_QueueWindow.FitInside()
                Message = self.OutgoingQueue.get(False)
        except queue.Empty:
            pass

        if not self.Paused and not self.Running and len(self.TheQueue) > 0 and self.Editting is not False:
            self.Editting -= 1
            if self.Editting == 0:
                self.Pause()
        if not self.Paused and not self.Running and len(self.TheQueue) > 0:
            self.Running = True
            Macro,FunctionPanel,FunctionText = self.TheQueue[0]
            FunctionPanel.SetBackgroundColour('green')
            FunctionPanel.Refresh()
            self.IncomingQueue.put(("StartFunction",Macro))
            self.StatusBar.SetStatusText(f"Macro: {FunctionText.GetLabel()}",0)
            self.StatusBar.SetStatusText("",1)
    # The queue only has 500 Macros in it at any one time so it doesn't use too much memory
    # If more are added to the queue, it will wait until there are less than 500 to add them.
        if len(self.AddToQueue) > 0  and len(self.TheQueue) < 500:
            AddN = 5
        # It adds 5 every time to not clog the main thread.  Trying to add all of them at once would make the main thread unresponsive.
            AddN = AddN if len(self.AddToQueue) > AddN else len(self.AddToQueue)
            for i in range(AddN):
                MacroName,Macro = self.AddToQueue.pop(0)
                self.AddSingleMacroToQueue(MacroName,Macro)
            self.m_QueueWindow.FitInside()
            # self.m_QueueWindow.Layout()

        return
    def IdleLoop(self, event):
        # This function runs whenever the GUI is idle (a few times a second)
        if len(self.AddToQueue) > 0 and len(self.TheQueue) < 500:
            AddN = 3
        # It adds 3 every time to not clog the main thread.
            AddN = AddN if len(self.AddToQueue) > AddN else len(self.AddToQueue)
            for i in range(AddN):
                MacroName,Macro = self.AddToQueue.pop(0)
                self.AddSingleMacroToQueue(MacroName,Macro)
            self.m_QueueWindow.FitInside()
    def OnClose(self,event=None):
        self.Closing = True
        if self.Software is not None:
            self.ClearQueue()
            self.IncomingQueue.put(['OnClose'])
            while self.Closing and self.Process.is_alive():
                self.Process.join(timeout=0.5)
        if self.Closing:
            self.Destroy()
    def LoadFunctions(self):
        FunctionNames = [file for file in os.listdir('Functions') if file[-3:] == ".py"]

        self.Functions = {f"{FunctionName[:-3]}":import_source_file(os.path.abspath(f'Functions\\{FunctionName}'),os.path.abspath(f'Functions\\{FunctionName}')) for FunctionName in FunctionNames}        
        for file in ["CreaTec.py","RHK.py","SXM.py"]:
            try:
                FunctionNames.remove(file)
            except:
                pass
        try:
            FunctionNames.insert(0, FunctionNames.pop(FunctionNames.index("General.py")))
        except:
            pass
        for file in FunctionNames:
            CheckFunction = self.m_NotSTMMenu.AppendCheckItem(wx.ID_ANY,file[:-3])
            self.Bind(wx.EVT_MENU,self.EditLoadedFunctionFiles,CheckFunction)
    def EditLoadedFunctionFiles(self,event=None):
        self.FunctionsLoaded = []
        for item in self.m_NotSTMMenu.GetMenuItems():
            if item.IsChecked():
                self.FunctionsLoaded.append(item.GetItemLabel())
        
        ThisChooseSoftwareDialog = ChooseSoftwareDialog(self,self.FunctionsLoaded)
        ThisChooseSoftwareDialog.SetSoftware(self.Software)
        
    
    def MakeFunctionButtons(self):
        for child in self.m_FunctionButtonWindow.GetChildren():
            child.Destroy()
        FunctionButtonSizer = wx.FlexGridSizer(0,2,0,0)
        
        if os.path.exists(self.MacroPath):
            with open(self.MacroPath, 'r') as fp:
                AllTheMacros = json.load(fp)
        else:
            AllTheMacros = {}
        
        def WriteFile(AllTheMacros):
            os.makedirs("Macros",exist_ok=True)
            with open(self.MacroPath, 'w') as fp:
                json.dump(AllTheMacros, fp,indent=1)

        # for FunctionName in self.Functions[self.SettingsDict['Software']].keys():
        
        FunctionList = []
        for FunctionFile in [self.Software,*self.FunctionsLoaded]:
            NewFunctions = getmembers(self.Functions[FunctionFile], isfunction)
            FunctionList = FunctionList + NewFunctions
        FunctionList = [function[0].replace("_"," ") for function in FunctionList]
        for FunctionName,Macro in AllTheMacros.items():
            SkipMacro = False
            for function in Macro:
                functionname = function[0]
                if not functionname in FunctionList:
                    SkipMacro = True
                    break
            if not SkipMacro:
                FunctionButton = wx.Button( self.m_FunctionButtonWindow, wx.ID_ANY, FunctionName, wx.DefaultPosition, wx.Size( 120,30 ), 0 )
                FunctionButton.Bind( wx.EVT_BUTTON, self.OnFunctionButton )
                FunctionButton.SetToolTip(FunctionName)
                FunctionButtonSizer.Add(FunctionButton,0, wx.ALL, 5)
                def FunctionRightClick(event):
                    ThisButton = event.GetEventObject()
                    popupmenu = wx.Menu()
                    menuItem = popupmenu.Append(-1, 'Add to Queue')
                    def Queued(event2):
                        self.OnFunctionButton(event)
                    self.Bind(wx.EVT_MENU, Queued, menuItem)
                    menuItem = popupmenu.Append(-1, 'Edit')
                    def Edit(event):
                        MacroLabel = ThisButton.GetLabel()
                        MyMacroDialog = MacroDialog(self,MacroName=MacroLabel,InitalMacro=AllTheMacros[MacroLabel])
                        MyMacroDialog.ShowModal()
                    self.Bind(wx.EVT_MENU, Edit, menuItem)
                    menuItem = popupmenu.Append(-1, 'Delete')
                    def Delete(event):
                        MacroLabel = ThisButton.GetLabel()
                        MyMessage = wx.MessageDialog(self,message=f"Are you sure that you want to delete {MacroLabel}?\nThis cannot be undone.",caption="Delete Macro",style=wx.YES_NO)
                        YesOrNo = MyMessage.ShowModal()
                        if YesOrNo == wx.ID_YES:
                            with open(self.MacroPath, 'r') as fp:
                                AllTheMacros = json.load(fp)
                            AllTheMacros.pop(MacroLabel)
                            with open(self.MacroPath, 'w') as fp:
                                json.dump(AllTheMacros, fp,indent=1)
                            self.MakeFunctionButtons()
                            self.m_FunctionButtonWindow.Layout()
                    self.Bind(wx.EVT_MENU, Delete, menuItem)
                    ThisButton.PopupMenu(popupmenu)
                FunctionButton.Bind( wx.EVT_RIGHT_DOWN, FunctionRightClick )
        self.m_FunctionButtonWindow.SetSizer(FunctionButtonSizer)
        self.m_FunctionButtonWindow.Layout()



    def OnFunctionButton(self,event):
        MacroLabel = event.GetEventObject().GetLabel()
        with open(self.MacroPath, 'r') as fp:
            AllTheMacros = json.load(fp)
        ThisMacro = AllTheMacros[MacroLabel]
        MyStartMacroDialog = StartMacroDialog(self,MacroLabel,ThisMacro)
        MyStartMacroDialog.ShowModal()
        
    def OnRFunctionClick(self, event):
        ThisText = event.GetEventObject()
        if ThisText.GetLabel() != "panel":
            ThisText = ThisText.GetParent()
        for ThisIndex,(Function,ThisPanel,Text) in enumerate(self.TheQueue):
            Index = ThisIndex
            Panel = ThisPanel
            if ThisText.GetId() == ThisPanel.GetId():
                break
        """Setup and Open a popup menu."""
        popupmenu = wx.Menu()
        menuItem = popupmenu.Append(-1, 'Move Up')
        def MoveUp(event):
            Function = self.TheQueue.pop(Index)
            self.TheQueue.insert(Index-1,Function)
            self.m_FunctionNameSizer.Remove(Index)
            self.m_FunctionNameSizer.Insert(Index-1,ThisText, 0, wx.ALL|wx.EXPAND, 5)
            self.m_QueueWindow.FitInside()
            pass
        self.Bind(wx.EVT_MENU, MoveUp, menuItem)
        if Index == 0 or (Index == 1 and self.Running):
            menuItem.Enable(False)
        
        menuItem = popupmenu.Append(-1, 'Move Down')
        def MoveDown(event):
            Function = self.TheQueue.pop(Index)
            self.TheQueue.insert(Index+1,Function)
            self.m_FunctionNameSizer.Remove(Index)
            self.m_FunctionNameSizer.Insert(Index+1,ThisText, 0, wx.ALL|wx.EXPAND, 5)
            self.m_QueueWindow.FitInside()
        if Index == 0 and self.Running:
            menuItem.Enable(False)

        self.Bind(wx.EVT_MENU, MoveDown, menuItem)
        if Index == len(self.TheQueue)-1:
            menuItem.Enable(False)

        menuItem = popupmenu.Append(-1, 'Edit Parameters')
        def Edit(event):
            self.EditMacroInQueue(event,Panel)

        self.Bind(wx.EVT_MENU, Edit, menuItem)
        # menuItem.Enable(False)
        if Index == 0 and self.Running:
            menuItem.Enable(False)

        menuItem = popupmenu.Append(-1, 'Copy')
        def Copy(event):
            MacroLabel = self.TheQueue[Index][2].GetLabel()
            Macro = self.TheQueue[Index][0]
            self.AddSingleMacroToQueue(MacroName=MacroLabel,Macro=Macro)
            CopiedIndex = len(self.TheQueue)-1
            Function = self.TheQueue.pop(CopiedIndex)
            self.TheQueue.insert(Index+1,Function)
            self.m_FunctionNameSizer.Remove(CopiedIndex)
            self.m_FunctionNameSizer.Insert(Index+1,Function[1], 0, wx.ALL|wx.EXPAND, 5)
            self.m_QueueWindow.FitInside()
            pass
        self.Bind(wx.EVT_MENU, Copy, menuItem)
        # menuItem.Enable(False)
    

        if Index == 0 and self.Running:
            menuItem = popupmenu.Append(-1, 'Cancel')
            def Cancel(event):
                ThisText.SetBackgroundColour('red')
                ThisText.Refresh()
                # self.IncomingQueue.put(("Cancel",))
                self.Cancel()
            self.Bind(wx.EVT_MENU, Cancel, menuItem)
        else:
            menuItem = popupmenu.Append(-1, 'Remove')
            def Remove(event):
                self.TheQueue.pop(Index)
                ThisText.Destroy()
                self.m_QueueWindow.FitInside()
            self.Bind(wx.EVT_MENU, Remove, menuItem)

        menuItem = popupmenu.Append(-1, 'Clear All Below')
        def RemoveBelow(event):
            for RemoveIndex,(Function,RemovePanel,Text) in enumerate(self.TheQueue):
                if RemoveIndex > Index:
                    RemovePanel.Destroy()
            self.AddToQueue = []
            self.TheQueue = self.TheQueue[:Index+1]
            self.m_QueueWindow.FitInside()
        self.Bind(wx.EVT_MENU, RemoveBelow, menuItem)
        if Index == len(self.TheQueue)-1:
            menuItem.Enable(False)
        # Show menu
        # XPos = int(np.ceil(ThisText.GetTextExtent(ThisText.GetLabel()).GetWidth()/2+ThisText.GetSize()[0]/2))
        # if event.GetX() > XPos:
        #     XPos = event.GetX()
        # ThisText.PopupMenu(popupmenu,XPos,event.GetY())
        ThisText.PopupMenu(popupmenu,event.GetX()+20,event.GetY())
        return
    def ClearQueue(self,event=None):
        self.AddToQueue = []
        if len(self.TheQueue) > 0:
            if self.Running:
                for RemoveIndex,(Function,RemovePanel,Text) in enumerate(self.TheQueue):
                    if RemoveIndex >= 1:
                        RemovePanel.Destroy()
                self.TheQueue = self.TheQueue[:1]
                self.TheQueue[0][1].SetBackgroundColour('red')
                self.TheQueue[0][1].Refresh()
                self.Cancel()
            else:
                for Function,RemovePanel,Text in self.TheQueue:
                    try:
                        RemovePanel.Destroy()
                    except:
                        pass
                self.TheQueue = []
            self.m_QueueWindow.FitInside()
    def Pause(self, event=None):
        if self.Paused:
            self.Paused = False
            self.m_PauseAfterButton.SetLabel("Pause After Macro")
            for i,Macro in enumerate(self.TheQueue):
                if (i > 0 and self.Running) or not self.Running:
                    Macro[1].SetBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ))
                    Macro[1].Refresh()
        else:
            self.Paused = True
            self.m_PauseAfterButton.SetLabel("Resume")
            for i,Macro in enumerate(self.TheQueue):
                if (i > 0 and self.Running) or not self.Running:
                    Macro[1].SetBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE))
                    Macro[1].Refresh()
        return
    def Cancel(self):
        if not self.Paused and self.m_PauseAfterCancel.IsChecked():
            self.Pause()
        for FunctionFile in [self.Software,*self.FunctionsLoaded]:
            self.Functions[FunctionFile].Cancel = True
        

    def StartMakeNewMacro(self,event):
        MyMacroDialog = MacroDialog(self)
        MyMacroDialog.ShowModal()
        pass
    def DefineMacroSettings(self,Name,TheMacro):
        MyMacroSettingsDialog = MacroSettingsDialog(self,Name,TheMacro)
        MyMacroSettingsDialog.ShowModal()
    def AddMacroToQueue(self,TheMacro,MacroName,Index=None):
        TheExpandedMacros = []
        for Function in TheMacro:
            Included = Function['Included']
            Name = Function['Name']
            Parameters = Function['Parameters']


            nDataPoints = 1
            ExpandedInputSpace = {}
            for key, Parameter in Parameters.items():
                value = Parameter['Value']
                if type(value) != list:
                    value = [value]
                #pair each input...
                ListLength = len(value)
                for ExpandedKey, ExpandedValues in ExpandedInputSpace.items():
                    #...with each input that came before it.
                    ExpandedInputSpace[ExpandedKey] = [ExpandedValues[i] for j in range(ListLength) for i in range(nDataPoints)]
                ExpandedInputSpace[key] = [value[j] for j in range(ListLength) for i in range(nDataPoints)]
                nDataPoints *= ListLength
            ExpandedInputSpace = [{ExpandedKey: ExpandedValues[i] for ExpandedKey, ExpandedValues in ExpandedInputSpace.items()} for i in range(nDataPoints)]
            if Included:
                if len(TheExpandedMacros) == 0:
                    for ParameterSet in ExpandedInputSpace:
                        ExpandedMacroFunction = {"Name":Name}
                        ExpandedMacroFunction['Parameters'] = {}
                        for ParameterName, ParameterValue in ParameterSet.items():
                            ExpandedMacroFunction['Parameters'][ParameterName] = ParameterValue
                        TheExpandedMacros.append([[ExpandedMacroFunction,True]])
                        
                else:
                    TheUpdatedExpandedMacros = []
                    for MacroIndex,Macro in enumerate(TheExpandedMacros):
                        for FunctionIndex,ParameterSet in enumerate(ExpandedInputSpace):
                            MacroCopy = Macro.copy()
                            ExpandedMacroFunction = {"Name":Name}
                            ExpandedMacroFunction['Parameters'] = {}
                            for ParameterName, ParameterValue in ParameterSet.items():
                                ExpandedMacroFunction['Parameters'][ParameterName] = ParameterValue
                            if FunctionIndex == 0:
                                MacroCopy.append([ExpandedMacroFunction,True])
                                TheUpdatedExpandedMacros.append(MacroCopy)
                            else:
                                MacroCopy = [[Function[0],False] for Function in MacroCopy]
                                MacroCopy.append([ExpandedMacroFunction,True])
                                TheUpdatedExpandedMacros.append(MacroCopy)
                    TheExpandedMacros = TheUpdatedExpandedMacros
            else:
                if len(TheExpandedMacros) == 0:
                    ParameterSet = ExpandedInputSpace[0]
                    ExpandedMacroFunction = {"Name":Name}
                    ExpandedMacroFunction['Parameters'] = {}
                    for ParameterName, ParameterValue in ParameterSet.items():
                        ExpandedMacroFunction['Parameters'][ParameterName] = ParameterValue
                    TheExpandedMacros.append([[ExpandedMacroFunction,False]])
                        
                else:
                    TheUpdatedExpandedMacros = []
                    for MacroIndex,Macro in enumerate(TheExpandedMacros):
                        ParameterSet = ExpandedInputSpace[0]
                        ExpandedMacroFunction = {"Name":Name}
                        ExpandedMacroFunction['Parameters'] = {}
                        for ParameterName, ParameterValue in ParameterSet.items():
                            ExpandedMacroFunction['Parameters'][ParameterName] = ParameterValue
                        Macro.append([ExpandedMacroFunction,False])
                        TheUpdatedExpandedMacros.append(Macro)
        i=0
        for Macro in TheExpandedMacros:
            if Index is None:
                self.AddToQueue.append([MacroName,Macro])
            else:
                self.AddSingleMacroToQueue(MacroName,Macro,Index+i)
                i+=1
    def AddSingleMacroToQueue(self,MacroName,Macro,InsertIndex=None):
        thisSettingString = ""
        for Function,Included in Macro:
            if Included:
                for key, value in Function['Parameters'].items():
                    thisSettingString+=f"{key} = {value}, "
        thisSettingString = thisSettingString[:-2]

        YBitmapSize = 30
        m_FunctionWindow = wx.Panel( self.m_QueueWindow, wx.ID_ANY, (5000,5000), wx.Size(-1,-1), wx.TAB_TRAVERSAL | wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        m_FunctionWindow.Hide()
        m_FunctionWindow.SetPosition(wx.DefaultPosition)
        m_FunctionWindow.Show()

        # self.m_FunctionNameSizer.Add( m_FunctionWindow, 0, wx.ALL|wx.EXPAND, 5 )

        # Sometimes works:
        # m_FunctionWindow.Bind(wx.EVT_MOTION, self.OnStartDrag)

        Color = wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) if (not self.Paused or self.m_PauseAfterButton.GetLabel() == "Start") else wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE)
        m_FunctionWindow.SetBackgroundColour(Color)
        m_FunctionWindow.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1 = wx.FlexGridSizer( 1, 10, 0, 0 )
        bSizer1.SetFlexibleDirection( wx.BOTH )
        bSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        bSizer1.AddGrowableCol(6)
        # bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

        m_FunctionNameText = wx.StaticText( m_FunctionWindow, wx.ID_ANY, MacroName, wx.DefaultPosition, wx.Size( -1,-1), wx.ALIGN_RIGHT)
        m_FunctionNameText.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1.Add( m_FunctionNameText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 2 )

        Text = wx.StaticText( m_FunctionWindow, wx.ID_ANY, "", wx.DefaultPosition, wx.Size( 10,YBitmapSize), wx.ALIGN_CENTER_HORIZONTAL)
        Text.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1.Add( Text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )

        m_Up = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.UpBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer1.Add( m_Up, 0, wx.ALL|wx.ALIGN_CENTER, 2 )
        m_Up.Bind( wx.EVT_BUTTON, self.MoveUpInQueue)

        m_Down = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.DownBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer1.Add( m_Down, 0, wx.ALL|wx.ALIGN_CENTER, 2 )

        m_Down.Bind( wx.EVT_BUTTON, self.MoveDowninQueue)
            
        m_Remove = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.RemoveBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer1.Add( m_Remove, 0, wx.ALL|wx.ALIGN_CENTER, 2 )

        m_Remove.Bind( wx.EVT_BUTTON, self.RemoveFromQueue)



        m_Edit = wx.Button( m_FunctionWindow, wx.ID_ANY, u"Edit", wx.DefaultPosition, wx.Size(40,YBitmapSize), 0 )
        bSizer1.Add( m_Edit, 0, wx.ALL|wx.ALIGN_CENTER, 2 )

        m_Edit.Bind( wx.EVT_BUTTON, self.EditMacroInQueue)
        # m_Edit.Enable(False)


        
        SettingText = wx.StaticText( m_FunctionWindow, wx.ID_ANY, thisSettingString, wx.DefaultPosition, wx.Size( 10,YBitmapSize), wx.ALIGN_RIGHT)
        SettingText.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1.Add( SettingText, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 2 )

        m_FunctionWindow.SetToolTip(thisSettingString)
        for child in m_FunctionWindow.GetChildren():
                child.SetToolTip(thisSettingString)

        m_FunctionWindow.SetSizer( bSizer1 )
        # m_FunctionWindow.Layout()
        bSizer1.Fit( m_FunctionWindow )
        if InsertIndex is None:
            Index = len(self.TheQueue)
        else:
            Index = InsertIndex
        self.TheQueue.insert(Index,[Macro,m_FunctionWindow,m_FunctionNameText])
        self.m_FunctionNameSizer.Insert( Index,m_FunctionWindow, 0, wx.ALL|wx.EXPAND, 5 ,)
        # self.m_FunctionNameSizer.Insert(Index,m_FunctionWindow, 0, wx.ALL|wx.EXPAND, 5)
        # gauge = wx.Gauge(m_FunctionWindow, range = 20, size = m_FunctionWindow.GetSize(), style = wx.GA_HORIZONTAL)
        # self.m_FunctionNameSizer.Add( gauge, 0, wx.ALL|wx.EXPAND, 5 )
        # gauge.SetPosition((0,0))
        self.m_QueueWindow.FitInside()
        self.m_QueueWindow.Layout()

    def MoveUpInQueue(self,event):
        ThisPanel = event.GetEventObject().GetParent()
        for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisPanel.GetId() == Panel.GetId():
                break
        if Index == 0 or (Index == 1 and self.Running):
            pass
        else:
            Function = self.TheQueue.pop(Index)
            self.TheQueue.insert(Index-1,Function)
            self.m_FunctionNameSizer.Remove(Index)
            self.m_FunctionNameSizer.Insert(Index-1,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
            self.m_QueueWindow.FitInside()
    def MoveDowninQueue(self,event):
        ThisPanel = event.GetEventObject().GetParent()
        for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisPanel.GetId() == Panel.GetId():
                break
        if (Index == 0 and self.Running) or (Index == len(self.TheQueue)-1):
            pass
        else:
            Function = self.TheQueue.pop(Index)
            self.TheQueue.insert(Index+1,Function)
            self.m_FunctionNameSizer.Remove(Index)
            self.m_FunctionNameSizer.Insert(Index+1,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
            self.m_QueueWindow.FitInside()
    def RemoveFromQueue(self,event):
        ThisPanel = event.GetEventObject().GetParent()
        for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisPanel.GetId() == Panel.GetId():
                break
        if Index == 0 and self.Running:
            ThisPanel.SetBackgroundColour('red')
            ThisPanel.Refresh()
            self.Cancel()
            # self.IncomingQueue.put(("Cancel",))
        else:
            self.TheQueue.pop(Index)
            ThisPanel.Destroy()
            self.m_QueueWindow.FitInside()
    def EditMacroInQueue(self,event,ThisPanel=None):
        if ThisPanel is None:
            ThisPanel = event.GetEventObject().GetParent()
        for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisPanel.GetId() == Panel.GetId():
                break
        if Index == 0 and self.Running:
            pass
        else:
            OriginallyPaused = self.Paused
            # if not OriginallyPaused:
            #     self.Pause()
            self.Editting = Index
            MacroLabel = self.TheQueue[Index][2].GetLabel()
            ThisMacroInfo = [[Function['Name'],{key:{"DefaultValue":f"{Parameter}",'Frozen':False} for key,Parameter in Function['Parameters'].items()},Included] for Function,Included in self.TheQueue[Index][0]]
            QueueObject=self.TheQueue[Index]
            MyStartMacroDialog = StartMacroDialog(self,MacroLabel,ThisMacroInfo,EdittingMode=True,QueueObject=QueueObject)
            MyStartMacroDialog.ShowModal()
            self.Editting = False

            if not OriginallyPaused and self.Paused:
                self.Pause()
            # thisSettingString = ""
            # ThisMacro = QueueObject[0]
            # for Function, Included in ThisMacro:
            #     if Included:
            #         for key, value in Function['Parameters'].items():
            #             thisSettingString+=f"{key} = {value}, "
            # thisSettingString = thisSettingString[:-2]
            # for child in QueueObject[1].GetChildren():
            #     child.SetToolTip(thisSettingString)
            # QueueObject[1].GetChildren()[-1].SetLabel(thisSettingString)
            # self.Layout()
    def OnStartDrag(self, event):
        if event.Dragging():
            ThisPanel = event.GetEventObject()
            ThisPanel.SetBackgroundColour('Blue')
            ThisPanel.Refresh()
            for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
                Index = ThisIndex
                if ThisPanel.GetId() == Panel.GetId():
                    break
            data = wx.TextDataObject()
            data.SetText(f"{Index}")
            dropSource = wx.DropSource(ThisPanel)
            dropSource.SetData(data)
            result = dropSource.DoDragDrop()
    def AddConnectToQueue(self, event=None):
        Initialize = [['Initialize',{},True]]
        MyStartMacroDialog = StartMacroDialog(self,"Connect",Initialize)
        MyStartMacroDialog.AddToQueue()
        return
    def AddDisconnectToQueue(self, event=None):
        OnClose = [['OnClose',{},True],['Pause',{},True]]
        MyStartMacroDialog = StartMacroDialog(self,"Disconnect",OnClose)
        MyStartMacroDialog.AddToQueue()
        self.AddConnectToQueue()
        return
    def OnRHKSoftware(self, event):
        ThisChooseSoftwareDialog = ChooseSoftwareDialog(self)
        ThisChooseSoftwareDialog.OnRHK()
        return
    def OnCreaTecSoftware(self, event):
        ThisChooseSoftwareDialog = ChooseSoftwareDialog(self)
        ThisChooseSoftwareDialog.OnCreaTec()
        return
    def OnSXMSoftware(self, event):
        ThisChooseSoftwareDialog = ChooseSoftwareDialog(self)
        ThisChooseSoftwareDialog.OnSXM()
        return
    def BasicUseageHelp(self, event):
        HelpMessage = "Left click on your choosen macro from the list on the main page.\n"
        HelpMessage += "Each function in the macro has a checkbox on the left side of the function's panel.  You may check/uncheck it.  If it is checked it will be run.  If it is unchecked it will not run.\n"
        HelpMessage += "Each parameter of each function may be changed to the value that you want.  If you input an unreasonable value, the function will be added to the queue but an error will pop-up and the queue will be paused when it attempts to run.  \n"
        HelpMessage += "After inputing your chosen values, press add to queue.\n\n"
        HelpMessage += "The 'Connect' macro needs to run for MacroQueue to connect to the STM's software.  It will stay connected unless the software is closed or the 'Disconnect' macro is run.  \n\n"
        HelpMessage += "You may right click a function in the queue to edit the parameters as long as the function is not currently running.  \n\n"
        HelpMessage += "You may pause the queue by pressing 'Pause after Function'.  It will finish the current function and then pause. \n\n"
        HelpMessage += "Clear Queue will cancel the current function, remove all the functions in the queue, and pause the queue incase you place anything else in the queue.\n\n\n\n\n"

        MyMessage = wx.MessageDialog(self,message=HelpMessage,caption="Help - Basic Usage")
        MyMessage.ShowModal()
        return 
    def ExpandNumericalParameters(self,event):
        HelpMessage = "When inputing numerical parameters, you may simultaneously add several items to the queue in two ways. \n"
        HelpMessage += "You may input either 1,3,7,9 or 1;3;7;9 and 4 macros will be added to the queue, each with a different value of the parameter. \n\n"
        HelpMessage += "If you want the values to be evenly spaced, you may also input -1,1,0.1.  This will add 21 parameters to the queue, from -1 to 1 with a step size of 0.1. The format is '{Start}, {End}, {Step size}'.  Writing -1,1,0.1 is identical to writing -1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1\n\n"
        HelpMessage += "You may use a negative step size if you would like to have the values decrease: 0,-10,-1.\n\n"
        
        HelpMessage += "If you want to input only 3 values, you may use semicolons ;.  -1;1;0.1 will not be expanded.\n\n"

        HelpMessage += "Advance use case: You can expand on a logscale by placing an 'L' or 'l' at the end.\n"
        HelpMessage += "The format is '{Start}, {End}, {N Points}L' \n"
        HelpMessage += "e.g. 1,10000,5L is the same as writing 1,10,100,1000,10000 \n\n\n"

        HelpMessage += "It is important to note that in the macros after the first, only the functions after the expanded function are included.  \n"
        HelpMessage += "For example, if there was a macro to (1) Set a BField, (2) wait some time, (3) set the bias, and (4) scan,\n"
        HelpMessage += "and we wanted to take two scans with a BField = 1T and biases -0.8 and 0.8, you can input -0.8,0.8 to the bias.\n"
        HelpMessage += "There will be 2 macros added to the queue.  The first will have all 4 functions.  It will set the bias to -0.8.  \n"
        HelpMessage += "The second macro will only set the bias to 0.8 and scan.  \n"
        HelpMessage += "If you wanted 4 scans, with BField = -1,1 and biases=-0.8,0.8,\n"
        HelpMessage += "you may input all the parameters and 4 macros will be added to the queue.\n"
        HelpMessage += "The first and third macro will (1) set the BField, (2) wait some time, (3) set the bias to -0.8, and scan.  The second and fourth will only set the set the bias to 0.8 and scan.\n"
        MyMessage = wx.MessageDialog(self,message=HelpMessage,caption="Help - Expand Numerical Parameters")
        MyMessage.ShowModal()
        return 
    def MakeAMacroHelp(self, event):
        HelpMessage = "Go to Macro -> Make New Macro\n"
        HelpMessage += "    Or right click an existing macro, and choose Edit from the menu.\n"
        HelpMessage += "Choose the functions that you would like to be in the macro.\n"
        HelpMessage += "    You may change the order or remove a function in the macro in the panel on the right.\n"
        HelpMessage += "Choose a name for your macro.  If it's a pre-existing macro and you do not change the name, the original macro will be overwriten.\n"
        HelpMessage += "Press Next to choose the default parameters of your macro.\n\n\n"
        HelpMessage += "Each function has a checkbox that indicates whether the function is included by default in the macro.\n"
        HelpMessage += "You may uncheck the box if you do not want the function to be included by default.  This is useful for functions that you only occasionally want to use in the macro.\n\n"
        HelpMessage += "You may choose the default value for each parameter of each function. \n"
        HelpMessage += "You may choose to freeze the parameter.  This will remove the option to change the parameter when adding it to the queue.  It simplifies the macro in exchange for less control.\n"
        HelpMessage += "\n"
        MyMessage = wx.MessageDialog(self,message=HelpMessage,caption="Help - Make a Macro")
        MyMessage.ShowModal()
        return
    def License(self, event):
        HelpMessage = """MIT License
        
Copyright (c) 2024 Bradley Goff

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        MyMessage = wx.MessageDialog(self,message=HelpMessage,caption="License")
        MyMessage.ShowModal()
        return
    def InfoHelp(self, event):
        HelpMessage = f"MacroQueue {VersionNumber} (9/2023)\n"
        HelpMessage += "Written by Brad Goff in Jay Gupta's CME Group at the Ohio State University\n"
        HelpMessage += "\n"
        MyMessage = wx.MessageDialog(self,message=HelpMessage,caption="Info")
        MyMessage.ShowModal()
        return
    def WriteANewFunctionHelp(self, event):
        HelpMessage = '''Go to File -> Open Source Folder.
Add the function to the .py file that corresponds to the software you want it to work with.
Open and close MacroQueue.  Your function can now be added to a macro.


The parameters of your function must have default values so that MacroQueue knows what the datatype to allow.
    MacroQueue works with floats, booleans, and strings. 
    If you only want the user to choose from a finite number of options, you may also put a list as the default parameter.  
    The user will be able to choose a single list entry to be used.

As of 6/1/2022, you may place comments directly above the function to give MacroQueue info on the parameters.
    The comments have to be directly above the relavent function with no spaces inbetween.
    The format has to be exactly:
        # Name=UNIT; this is the tool tip for a parameter called Name that has the unit "UNIT" 
        # Name; this is the tool tip for a parameter called Name that has the unit "UNIT" 
# Speed=The speed the tip moves in nm/s, s/line, or ms/pixel




Here is an example from RHK.py:

# Setpoint=pA;The current setpoint in pA
def Set_Setpoint(Setpoint=100):
    Setpoint *= 1e-12 #Convert from pA to A (RHK uses A)
    Message = f"SetHWSubParameter, Z PI Controller 1, Set Point, Value, {Setpoint}\n"
    Socket.send(Message.encode())
    data = Socket.recv(BUFFER_SIZE)

'''
        MyMessage = wx.MessageDialog(self,message=HelpMessage,caption="Help - Write a new function")
        MyMessage.ShowModal()
        return
    def OpenSourceFolder(self, event):
        if getattr(sys, 'frozen', False):
            MyMessage = wx.MessageDialog(self,message=f"This will take you to the software source files for the MacroQueue.exe on this computer.  Any changes will be forgotten when the EXE file is remade or updated.\nWould you like to continue?.",caption="Warning - Exe Source Files",style=wx.YES_NO)
            YesOrNo = MyMessage.ShowModal()
            if YesOrNo == wx.ID_NO:
                return
        FolderPath = os.path.realpath("Functions/")
        os.startfile(FolderPath)
        return
    def OpenMacroFile(self, event):
        FolderPath = os.path.realpath("Macros/")
        os.startfile(FolderPath)
        return
class MyPanelDropTarget(wx.DropTarget):
    def __init__(self, window,Parent): 
        wx.DropTarget.__init__(self)
        self.window = window
        self.Parent = Parent
        self.data = wx.TextDataObject()
        self.SetDataObject(self.data)
	
    def OnDragOver(self, x, y, d):
        if not self.GetData():
            return wx.DragNone

        Index = int(self.data.GetText())
        
        ThisPanel = self.Parent.TheQueue[Index][1]
        for ThisIndex,(Function,Panel,t) in enumerate(self.Parent.TheQueue):
            NewIndex = ThisIndex
            MinY = Panel.GetPosition()[1]
            MaxY = MinY + Panel.GetSize()[1]
            if y < (MinY+MaxY)/2:
                break
        if self.Parent.Running and NewIndex == 0:
            NewIndex == 1

        data = wx.TextDataObject()
        data.SetText(f"{NewIndex}")
        self.data = data
        Function = self.Parent.TheQueue.pop(Index)
        self.Parent.TheQueue.insert(NewIndex,Function)
        self.Parent.m_FunctionNameSizer.Remove(Index)
        self.Parent.m_FunctionNameSizer.Insert(NewIndex,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
        self.Parent.m_QueueWindow.FitInside()
        return d

    def OnData(self, x, y, d):
        if not self.GetData():
            return wx.DragNone
        Index = int(self.data.GetText())
        
        ThisPanel = self.Parent.TheQueue[Index][1]
        # for ThisIndex,(Function,Panel,t) in enumerate(self.Parent.TheQueue):
        #     NewIndex = ThisIndex
        #     MinY = Panel.GetPosition()[1]
        #     MaxY = MinY + Panel.GetSize()[1]
        #     if y < (MinY+MaxY)/2:
        #         break
        # Function = self.Parent.TheQueue.pop(Index)
        # self.Parent.TheQueue.insert(NewIndex,Function)
        # self.Parent.m_FunctionNameSizer.Remove(Index)
        # self.Parent.m_FunctionNameSizer.Insert(NewIndex,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
        # self.Parent.m_QueueWindow.FitInside()
        Color = wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) if (not self.Parent.Paused or self.Parent.m_PauseAfterButton.GetLabel() == "Start") else wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE)
        ThisPanel.SetBackgroundColour( Color)
        ThisPanel.Refresh()

        return d

def Thread(self,IncomingQueue,OutgoingQueue):
    Functions = {"RHK":RHKFunctions,"CreaTec":CreaTecFunctions,"SXM":SXMFunctions,"General":GeneralFunctions}
    while True:
        Message = IncomingQueue.get() # Blocks until there's a message
        if Message[0] == "SoftwareChange":
            # Changes the global parameters that are assessable to the new software's functions (e.g. RHK -> CreaTec)
            Software,FunctionsToLoad = Message[1]
            Functions[Software].MacroQueueSelf = self
            FunctionList = []
            for FunctionFile in [self.Software,*self.FunctionsLoaded]:
                NewFunctions = getmembers(self.Functions[FunctionFile], isfunction)
                FunctionList = FunctionList + NewFunctions
                Functions[FunctionFile] = self.Functions[FunctionFile]
            FunctionDict = {Name.replace("_"," "):Function for Name,Function in FunctionList}
            Functions[Software].OutgoingQueue = OutgoingQueue
            for FunctionFile in FunctionsToLoad:
                Functions[FunctionFile].MacroQueueSelf = self
                Functions[FunctionFile].OutgoingQueue = OutgoingQueue
        if Message[0] == "OnClose":
            for FunctionFile in [self.Software,*self.FunctionsLoaded]:
                ClosingFunctionDict = {Name.replace("_"," "):Function for Name,Function in getmembers(self.Functions[FunctionFile], isfunction)}
                if "OnClose" in ClosingFunctionDict.keys():
                    try:
                        # Runs the OnClose functions for the given softwares
                        ClosingFunctionDict["OnClose"]()
                    except:
                        pass
            if self.Closing:
                # Breaks out of the while loop which finishes/closes this thread
                break
        if Message[0] == 'StartFunction':
            # Starts the macro
            Name = None
            try:
                Macro = Message[1]
                Functions[Software].CurrentMacro = Macro
                for ThisFunction,Included in Macro:
                    # Runs each function
                    Name = ThisFunction['Name']
                    Parameters = ThisFunction['Parameters']
                    if Included:
                        Function = FunctionDict[Name]
                        if not Functions[Software].Cancel:
                            # Doesn't run the function if it's been cancelled
                            OutgoingQueue.put(("SetStatus",(f"Function: {Name}",1)))
                            Function(**Parameters)
                OutgoingQueue.put(("FunctionFinished",None))
                
                Functions[Software].Cancel = False
                for FunctionFile in FunctionsToLoad:
                    Functions[FunctionFile].Cancel = False
                OutgoingQueue.put(("SetStatus",(f"",1)))


            except Exception as e:
                OutgoingQueue.put(("ExceptionThrown",[e,Name]))



import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import types
def import_source_file(fname= str, modname= str) -> "types.ModuleType":
    """
    Import a Python source file and return the loaded module.
    Args:
        fname: The full path to the source file.  It may container characters like `.`
            or `-`.
        modname: The name for the loaded module.  It may contain `.` and even characters
            that would normally not be allowed (e.g., `-`).
    Return:
        The imported module
    Raises:
        ImportError: If the file cannot be imported (e.g, if it's not a `.py` file or if
            it does not exist).
        Exception: Any exception that is raised while executing the module (e.g.,
            :exc:`SyntaxError).  These are errors made by the author of the module!
    """
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    spec = importlib.util.spec_from_file_location(modname, fname)
    if spec is None:
        raise ImportError(f"Could not load spec for module '{modname}' at: {fname}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as e:
        raise ImportError(f"{e.strerror}: {fname}") from e
    return module

if __name__ == '__main__':
    mp.freeze_support()
    app = wx.App() 
    MyMainFrame = MainFrame()
    MyMainFrame.Show()
    app.MainLoop()


# pyinstaller -F --noconsole --icon=Compass.ico --additional-hooks-dir=. --add-data="Compass.ico;." --add-data="Actions-go-next-icon.bmp;." --add-data="Actions-go-previous-icon.bmp;." --add-data="Actions-go-next-icon2.bmp;." --add-data="Actions-go-previous-icon2.bmp;."  CapNav.py
