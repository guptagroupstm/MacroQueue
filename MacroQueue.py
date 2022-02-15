import inspect
import wx
import os
import sys
import pandas as pd
from shutil import copytree,rmtree
# from functools import partial
import win32com.client
# import plotly.graph_objects as go
# import plotly.express as px
import multiprocessing as mp
import numpy as np
from math import log10 , floor
import queue
# from scipy.stats import sem
# import random
import datetime

import pyvisa
import time

from wx.core import DirDialog,FileDialog, NumberEntryDialog, StatusBar
import GUIDesign

from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import matplotlib
# matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backend_bases import NavigationToolbar2
from matplotlib.backend_bases import MouseButton

import wx
import wx.xrc as xrc
matplotlib.rc('image', origin='lower')
from time import time as timer

import itertools

from SettingsDialog import SettingsDialog
from Macros import *

import Functions.RHK as RHKFunctions

from inspect import getmembers, isfunction, signature

IconFileName = "OJ.ico"

# TODO:
# Expand queue in X
# Estimate time in status.
# Fix SettingsDialog - an extra "," messes it up.  The nonnumbers are not being removed.

# Cancel settings parameter - Currently gives error

# Don't remake the bitmap for every function

# Copy function in menu
# After settings, remake function buttons



class MainFrame(GUIDesign.MyFrame):
    DefaultSettings = {'Software':'RHK',"Update Rate (s)":1}
    SettingsType = {'Software':['Choice',['RHK','CreaTec']],"Update Rate (s)":["Numerical"]}

# Scanning, fine motion, course motion, dI/dV scans, point spectra, tip form, 
    GenericFunctions = {"Wait":RHK_Scan,"Email":RHK_Scan}
    RHKFunctions = {"Scan":RHK_Scan,"Fine Motion":RHK_Scan,**GenericFunctions}
    Functions = {"RHK":RHKFunctions}
    TheQueue = []
    Paused = False
    Running = False

    def __init__(self):
        application_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        os.chdir(os.path.realpath(application_path))
        self.SavedSettingsFile = 'QueueSettings.csv'

        RHKFunctionsNames = dir(RHKFunctions)
        MembersList = getmembers(RHKFunctions, isfunction) 
        print(MembersList)
        MembersList[0][1]()
        MembersList[1][1](None)
        # for Name,Function in MembersList:
        #     sig = signature(Function)
        #     for v in sig.parameters.values():
        #         print(v)

        mp.set_start_method('spawn')
        self.OutgoingQueue = mp.Queue()
        self.IncomingQueue = mp.Queue()
        self.Process = mp.Process(target=Thread, args=(self.IncomingQueue,self.OutgoingQueue))
        self.Process.start()
        # Starts Thread with Incoming & Outgoing Queue.  Any time-consuming calculations/measurements should be made on this thread.

        # The GUIDesign is defined in GUIDesign.py as the class MyFrame. It was made with wxFormBuilder
        GUIDesign.MyFrame.__init__(self, parent=None) 
        icon_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), IconFileName)
        if os.path.exists(icon_file):
            icon = wx.Icon(icon_file)
            self.SetIcon(icon)

        # Read the saved settings file here
        if os.path.exists(self.SavedSettingsFile):
            SettingsSeries = pd.read_csv(self.SavedSettingsFile,names=['key','value'])
            self.SettingsDict = SettingsSeries.set_index('key').T.iloc[0].to_dict()
            for key in self.SettingsDict.keys():
                if self.SettingsType[key][0] == 'Numerical':
                    self.SettingsDict[key] = int(self.SettingsDict[key]) if float(self.SettingsDict[key])%1 == 0 else float(self.SettingsDict[key])
        else:
            self.SettingsDict = self.DefaultSettings
            pd.Series(self.SettingsDict).to_csv(self.SavedSettingsFile,header=False)
        YBitmapSize = 20
        self.DownBitmap = wx.Bitmap( u"Bitmaps\\DownArrow.bmp", wx.BITMAP_TYPE_ANY).ConvertToImage().Scale(20,YBitmapSize).ConvertToBitmap()
        self.UpBitmap = wx.Bitmap( u"Bitmaps\\UpArrow.bmp", wx.BITMAP_TYPE_ANY).ConvertToImage().Scale(20,YBitmapSize).ConvertToBitmap()
        self.RemoveBitmap = wx.Bitmap( u"Bitmaps\\Remove.bmp", wx.BITMAP_TYPE_ANY).ConvertToImage().Scale(20,YBitmapSize).ConvertToBitmap()
        self.AddFunctionButtons()
        self.m_FunctionNameSizer = wx.FlexGridSizer( 0, 1, -6, 0 )
        self.m_FunctionNameSizer.AddGrowableCol( 0 )
        self.m_FunctionNameSizer.SetFlexibleDirection( wx.BOTH )
        self.m_FunctionNameSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        self.m_QueueWindow.SetSizer(self.m_FunctionNameSizer)
        def OnQueueSize(event):
            # self.m_QueueWindow.Layout()
            self.m_QueueWindow.FitInside()
        self.m_QueueWindow.Bind( wx.EVT_SIZE, OnQueueSize )
        self.Show()

    def CheckQueue(self,event):
        try:
            Message = self.OutgoingQueue.get(False)
            while Message:
                if Message[0] == 'SetStatus':
                    self.StatusBar.SetStatusText(*Message[1])
                if Message[0] == 'UpdateTime':
                    TimePassed = Message[1]
                    pass
                if Message[0] == 'FunctionFinished':
                    self.Running = False
                    FunctionClass,FunctionPanel,FunctionText = self.TheQueue.pop(0)
                    FunctionPanel.Destroy()
                    self.m_QueueWindow.FitInside()
                    pass
                Message = self.OutgoingQueue.get(False)
        except queue.Empty:
            pass
        if not self.Paused and not self.Running and len(self.TheQueue) > 0:
            self.Running = True
            FunctionClass,FunctionPanel,FunctionText = self.TheQueue[0]
            FunctionPanel.SetBackgroundColour('green')
            FunctionPanel.Refresh()
            self.IncomingQueue.put(("StartFunction",FunctionClass))
            self.StatusBar.SetStatusText(FunctionText.GetLabel(),0)
        return

    def OnClose(self,event):
        self.Process.terminate()
        self.Process.join()
        self.Destroy()

    def AddFunctionButtons(self):
        self.FunctionButtonSizer = wx.FlexGridSizer(0,2,0,0)
        for FunctionName in self.Functions[self.SettingsDict['Software']].keys():
            self.Function = wx.Button( self.m_FunctionButtonWindow, wx.ID_ANY, FunctionName, wx.DefaultPosition, wx.Size( 100,40 ), 0 )
            self.Function.Bind( wx.EVT_BUTTON, self.OnFunctionButton )
            self.FunctionButtonSizer.Add(self.Function,0, wx.ALL, 5)

        self.m_FunctionButtonWindow.SetSizer(self.FunctionButtonSizer)
    def OpenSettings(self,event):
        MysettingsDialog = SettingsDialog(self,self.SettingsDict,self.SettingsType,title = 'Settings')
        MysettingsDialog.ShowModal()
        pd.Series(self.SettingsDict).to_csv(self.SavedSettingsFile,header=False)

    def OnFunctionButton(self,event):
        FunctionLabel = event.GetEventObject().GetLabel()
        Function = self.Functions[self.SettingsDict['Software']][FunctionLabel]
        SettingsDict = Function.DefaultSettings.copy()

        settingsDialog = SettingsDialog(self,SettingsDict,Function.SettingsType, title = f'{FunctionLabel} Parameters',ExpandOutput=True)
        settingsDialog.ShowModal()

        ExpandedInputSpace = {}
        nDataPoints = 1
        #To get a list of all possible combinations of inputs,
        for key, value in SettingsDict.items():
            #pair each input...
            ListLength = len(value)
            for ExpandedKey, ExpandedValues in ExpandedInputSpace.items():
                #...with each input that came before it.
                ExpandedInputSpace[ExpandedKey] = [ExpandedValues[i] for j in range(ListLength) for i in range(nDataPoints)]
            ExpandedInputSpace[key] = [value[j] for j in range(ListLength) for i in range(nDataPoints)]
            nDataPoints *= ListLength
        SettingsDicts = [{ExpandedKey: ExpandedValues[i] for ExpandedKey, ExpandedValues in ExpandedInputSpace.items()} for i in range(nDataPoints)]
        


        for thisSettingDict in SettingsDicts:
            thisSettingString = ""
            for key, value in thisSettingDict.items():
                thisSettingString+=f"{key} = {value}, "
            thisSettingString = thisSettingString[:-2]

            YBitmapSize = 20
            m_FunctionWindow = wx.Panel( self.m_QueueWindow, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1,-1), wx.TAB_TRAVERSAL )
            m_FunctionWindow.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )
            m_FunctionWindow.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
            bSizer1 = wx.FlexGridSizer( 1, 10, 0, 0 )
            bSizer1.SetFlexibleDirection( wx.BOTH )
            bSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
            bSizer1.AddGrowableCol(6)
            # bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
            m_FunctionWindow.Hide()


            m_FunctionNameText = wx.StaticText( m_FunctionWindow, wx.ID_ANY, FunctionLabel, wx.DefaultPosition, wx.Size( -1,YBitmapSize), wx.ALIGN_CENTER_HORIZONTAL)
            m_FunctionNameText.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
            bSizer1.Add( m_FunctionNameText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )

            Text = wx.StaticText( m_FunctionWindow, wx.ID_ANY, "", wx.DefaultPosition, wx.Size( 10,YBitmapSize), wx.ALIGN_CENTER_HORIZONTAL)
            Text.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
            bSizer1.Add( Text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )

            m_Up = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.UpBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
            bSizer1.Add( m_Up, 0, wx.ALL|wx.ALIGN_CENTER, 2 )

            def MoveUp(event):
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
            m_Up.Bind( wx.EVT_BUTTON, MoveUp)

            m_Down = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.DownBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
            bSizer1.Add( m_Down, 0, wx.ALL|wx.ALIGN_CENTER, 2 )
            def MoveDown(event):
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
            m_Down.Bind( wx.EVT_BUTTON, MoveDown)
                
            m_Remove = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.RemoveBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
            bSizer1.Add( m_Remove, 0, wx.ALL|wx.ALIGN_CENTER, 2 )
            def Remove(event):
                ThisPanel = event.GetEventObject().GetParent()
                for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
                    Index = ThisIndex
                    if ThisPanel.GetId() == Panel.GetId():
                        break
                if Index == 0 and self.Running:
                    ThisPanel.SetBackgroundColour('red')
                    ThisPanel.Refresh()
                    self.IncomingQueue.put(("Cancel",))
                else:
                    self.TheQueue.pop(Index)
                    ThisPanel.Destroy()
                    self.m_QueueWindow.FitInside()
            m_Remove.Bind( wx.EVT_BUTTON, Remove)



            m_Edit = wx.Button( m_FunctionWindow, wx.ID_ANY, u"Edit", wx.DefaultPosition, wx.Size(40,YBitmapSize), 0 )
            bSizer1.Add( m_Edit, 0, wx.ALL|wx.ALIGN_CENTER, 2 )
            def Edit(event):
                ThisPanel = event.GetEventObject().GetParent()
                for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
                    Index = ThisIndex
                    if ThisPanel.GetId() == Panel.GetId():
                        break
                if Index == 0 and self.Running:
                    pass
                else:
                    self.Paused = True
                    MysettingsDialog = SettingsDialog(self,self.TheQueue[Index][0].Settings,self.TheQueue[Index][0].SettingsType,title = f'{self.TheQueue[Index][2].GetLabel()} Parameters')
                    MysettingsDialog.ShowModal()
                    self.Paused = False
                    thisSettingString = ""
                    for key, value in self.TheQueue[Index][0].Settings.items():
                        thisSettingString+=f"{key} = {value}, "
                    thisSettingString = thisSettingString[:-2]
                    for child in self.TheQueue[Index][1].GetChildren():
                        child.SetToolTip(thisSettingString)
                    self.TheQueue[Index][1].GetChildren()[-1].SetLabel(thisSettingString)
            m_Edit.Bind( wx.EVT_BUTTON, Edit)


            
            SettingText = wx.StaticText( m_FunctionWindow, wx.ID_ANY, thisSettingString, wx.DefaultPosition, wx.Size( 10,YBitmapSize), wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
            SettingText.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
            bSizer1.Add( SettingText, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 2 )

            m_FunctionWindow.SetToolTip(thisSettingString)
            for child in m_FunctionWindow.GetChildren():
                    child.SetToolTip(thisSettingString)


            m_FunctionWindow.SetSizer( bSizer1 )
            m_FunctionWindow.Layout()
            bSizer1.Fit( m_FunctionWindow )
            # fgSizer3.Add( self.m_FunctionWindow, 1, wx.EXPAND |wx.ALL, 2 )

            m_FunctionWindow.Show()
            self.TheQueue.append([Function(thisSettingDict),m_FunctionWindow,m_FunctionNameText])
            self.m_FunctionNameSizer.Add( m_FunctionWindow, 0, wx.ALL|wx.EXPAND, 5 )
            self.m_QueueWindow.FitInside()
        
    def OnRFunctionClick(self, event):
        ThisText = event.GetEventObject()
        if ThisText.GetLabel() != "panel":
            ThisText = ThisText.GetParent()
        for ThisIndex,(Function,Panel,Text) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisText.GetId() == Panel.GetId():
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
            self.Paused = True
            MysettingsDialog = SettingsDialog(self,self.TheQueue[Index][0].Settings,self.TheQueue[Index][0].SettingsType,title = f'{self.TheQueue[Index][2].GetLabel()} Parameters')
            MysettingsDialog.ShowModal()
            self.Paused = False
            thisSettingString = ""
            for key, value in self.TheQueue[Index][0].Settings.items():
                thisSettingString+=f"{key} = {value}, "
            thisSettingString = thisSettingString[:-2]
            for child in self.TheQueue[Index][1].GetChildren():
                child.SetToolTip(thisSettingString)
            self.TheQueue[Index][1].GetChildren()[-1].SetLabel(thisSettingString)
        self.Bind(wx.EVT_MENU, Edit, menuItem)
        if Index == 0 and self.Running:
            menuItem.Enable(False)


        if Index == 0 and self.Running:
            menuItem = popupmenu.Append(-1, 'Cancel')
            def Cancel(event):
                ThisText.SetBackgroundColour('red')
                ThisText.Refresh()
                self.IncomingQueue.put(("Cancel",))
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
            self.TheQueue = self.TheQueue[:Index+1]
            self.m_QueueWindow.FitInside()
            # print(self.m_FunctionNameSizer.GetChildren())
            # print(len(self.m_FunctionNameSizer.GetChildren()))
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
    def ClearQueue(self,event):
        if len(self.TheQueue) > 0:
            if self.Running:
                for RemoveIndex,(Function,RemovePanel,Text) in enumerate(self.TheQueue):
                    if RemoveIndex >= 1:
                        RemovePanel.Destroy()
                self.TheQueue = self.TheQueue[:1]
                self.TheQueue[0][1].SetBackgroundColour('red')
                self.TheQueue[0][1].Refresh()
                self.IncomingQueue.put(("Cancel",))
            else:
                for Function,RemovePanel,Text in self.TheQueue:
                    RemovePanel.Destroy()
                self.TheQueue = []
            self.m_QueueWindow.FitInside()
    def Pause(self, event):
        if self.Paused:
            self.Paused = False
            self.m_PauseAfterButton.SetLabel("Pause After Function")
            if self.Running:
                self.TheQueue[1][1].SetBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ))
                self.TheQueue[1][1].Refresh()
            else:
                self.TheQueue[0][1].SetBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ))
                self.TheQueue[0][1].Refresh()
        else:
            self.Paused = True
            self.m_PauseAfterButton.SetLabel("Resume")
            if self.Running:
                self.TheQueue[1][1].SetBackgroundColour('yellow')
                self.TheQueue[1][1].Refresh()
            else:
                self.TheQueue[0][1].SetBackgroundColour('yellow')
                self.TheQueue[0][1].Refresh()
        return



def Thread(IncomingQueue,OutgoingQueue):
    while True:
        Message = IncomingQueue.get() # Blocks until there's a message
        if Message[0] == 'StartFunction':
            FunctionClass = Message[1]
            FunctionClass.StartMacro(OutgoingQueue,IncomingQueue)


if __name__ == '__main__':
    mp.freeze_support()
    app = wx.App() 
    MyMainFrame = MainFrame()
    MyMainFrame.Show()
    app.MainLoop()


# pyinstaller -F --noconsole --icon=Compass.ico --additional-hooks-dir=. --add-data="Compass.ico;." --add-data="Actions-go-next-icon.bmp;." --add-data="Actions-go-previous-icon.bmp;." --add-data="Actions-go-next-icon2.bmp;." --add-data="Actions-go-previous-icon2.bmp;."  CapNav.py
