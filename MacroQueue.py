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

from Marcos import *

IconFileName = "OJ.ico"
Title = "AUGER"



DefaultSettings = {"Setting1":0}
DefaultSettingsType = {"Setting1":["Numerical"]}

class MainFrame(GUIDesign.MyFrame):
    def __init__(self):
        application_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        os.chdir(os.path.realpath(application_path))


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

        self.Show()
    def CheckQueue(self,event):
        try:
            Message = self.OutgoingQueue.get(False)
            while Message:
                if Message[0] == 'State1':
                    pass
                if Message[0] == 'State2':
                    pass
                Message = self.OutgoingQueue.get(False)
        except queue.Empty:
            pass
        return


    def OnClose(self,event):
        self.Process.terminate()
        self.Process.join()
        self.Destroy()

    def OpenSettings(self,event):
        settingsDialog = SettingsDialog(self,self.SettingsDict,DefaultSettingsType,None, title = 'Settings')
        settingsDialog.ShowModal()

class SettingsDialog(wx.Dialog):

    def __init__(self, parent, SettingsDict,DefaultSettingsType, *args, **kw):
        super(SettingsDialog, self).__init__(*args, **kw)
        self.SettingsDict = SettingsDict
        self.DefaultSettingsType = DefaultSettingsType
        self.parent = parent
        self.InitUI()
        self.Centre()
        self.SetSize((600,300))
        self.SetTitle('Settings')
        # self.Bind( wx.EVT_INIT_DIALOG, self.InitUI )
        self.Show()

        

    def InitUI(self,event=None):

        #set up panel and sizers
        panel = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.VSCROLL  )
        panel.SetScrollRate( 5, 5 )
        # sb = wx.StaticBox(panel, label = 'Settings')
        sbs = wx.FlexGridSizer(4)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        def RemoveNonNumbers(String,Default):
            AcceptableList = ['0','1','2','3','4','5','6','7','8','9','.']
            NewString = ''.join([digit for digit in String if digit in AcceptableList])
            WasAlreadyNumerical = len(NewString) == len(String)
            if len(NewString)>0:
                if '.' in NewString:
                    Number = float(NewString)
                else:
                    Number = int(NewString)
            else:
                Number = Default
                WasAlreadyNumerical = False
            return Number, WasAlreadyNumerical
        #create static texts for setting labels
        self.CtrlDict = {}
        for label,value in self.SettingsDict.items():
            SettingLabel = wx.StaticText(panel, label = f"{label} :")
            if self.DefaultSettingsType[label][0] == "Numerical":
                self.CtrlDict[label]  = wx.TextCtrl(panel, wx.ID_ANY, value = f"{value}")
                def NumericalOnlyFunction(ThisLabel):
                    def NumericalOnly(event):
                        Number, WasAlreadyNumerical = RemoveNonNumbers(self.CtrlDict[ThisLabel].GetValue(),"")
                        if not WasAlreadyNumerical and Number != "":
                            self.CtrlDict[ThisLabel].SetValue(f"{Number}")
                        return NumericalOnly
                self.CtrlDict[label].Bind( wx.EVT_TEXT, NumericalOnlyFunction(label))
            elif self.DefaultSettingsType[label][0] == "Choice":
                Choices = self.DefaultSettingsType[label][1]
                self.CtrlDict[label] = wx.Choice( panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, Choices )
                if value in Choices:
                    self.CtrlDict[label].SetStringSelection(value)
                else:
                    self.CtrlDict[label].SetSelection(0)
            sbs.Add(SettingLabel, 0, wx.ALL, 5)
            sbs.Add(self.CtrlDict[label], 0, wx.ALL|wx.EXPAND, 5)


        #set panel sizer
        panel.SetSizer(sbs)


        #create apply and close buttons and add them to horizontal sizer
        applyButton = wx.Button(self, label = 'Apply', size=(100,20))
        closeButton = wx.Button(self, label = 'Close', size=(100,20))
        hbox.Add(applyButton, wx.ID_ANY, wx.ALL, border = 10)
        hbox.Add(closeButton, wx.ID_ANY, wx.ALL, border = 10)

        #add panel and horizontal sizer to vertical sizer
        #and then set sizer for dialog box
        vbox.Add(panel, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox, flag=wx.EXPAND)

        self.SetSizer(vbox)

        #bind button events to functions
        def SetValues(event):
            for label,value in self.SettingsDict.items():
                if self.DefaultSettingsType[label][0] == "Numerical":
                    CtrlValue = self.CtrlDict[label].GetValue()
                    CtrlValue, WasAlreadyNumerical = RemoveNonNumbers(CtrlValue,float(self.SettingsDict[label]))
                elif self.DefaultSettingsType[label][0] == "Choice":
                    CtrlValue = self.CtrlDict[label].GetStringSelection()
                self.SettingsDict[label] = CtrlValue
                self.parent.SavedSettings[label] = CtrlValue
            pd.Series(self.parent.SavedSettings).to_csv(self.parent.SavedSettingsFile,header=False)
            self.Destroy()
            pass
        applyButton.Bind(wx.EVT_BUTTON, SetValues)
        closeButton.Bind(wx.EVT_BUTTON, lambda event: self.Close())

        def OnExit(event):
            AnyChanges = False
            for label,value in self.SettingsDict.items():
                if self.DefaultSettingsType[label][0] == "Numerical":
                    CtrlValue = self.CtrlDict[label].GetValue()
                    CtrlValue, WasAlreadyNumerical = RemoveNonNumbers(CtrlValue,"")
                elif self.DefaultSettingsType[label][0] == "Choice":
                    CtrlValue = self.CtrlDict[label].GetStringSelection()
                if self.SettingsDict[label] != CtrlValue:
                    AnyChanges = True
            if AnyChanges:
                #check to make sure they dont want to apply these settings, then close
                resp = wx.MessageBox('Any changes you made will not be saved, click OK to continue', 'Warning!',wx.OK|wx.CANCEL)
                if resp == wx.OK:
                    self.Destroy()
                else:
                    pass
            else:
                self.Destroy()
        self.Bind(wx.EVT_CLOSE, OnExit)

def Thread(IncomingQueue,OutgoingQueue):
    while True:
        Message = IncomingQueue.get() # Blocks until there's a message
        if Message[0] == 'State2':
            pass
        if Message[0] == 'State2':
            pass

def RemoveNonNumbers(String,Default):
    AcceptableList = ['0','1','2','3','4','5','6','7','8','9','.']
    NewString = ''.join([digit for digit in String if digit in AcceptableList])
    WasAlreadyNumerical = len(NewString) == len(String)
    if len(NewString)>0:
        if '.' in NewString:
            Number = float(NewString)
        else:
            Number = int(NewString)
    else:
        Number = Default
        WasAlreadyNumerical = False
    return Number, WasAlreadyNumerical

def Test():
    pass
if __name__ == '__main__':
    mp.freeze_support()
    app = wx.App() 
    top = MainFrame()
    top.Show()
    app.MainLoop()


# pyinstaller -F --noconsole --icon=Compass.ico --additional-hooks-dir=. --add-data="Compass.ico;." --add-data="Actions-go-next-icon.bmp;." --add-data="Actions-go-previous-icon.bmp;." --add-data="Actions-go-next-icon2.bmp;." --add-data="Actions-go-previous-icon2.bmp;."  CapNav.py
