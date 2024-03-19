import wx
import multiprocessing as mp
from MacroQueue import MacroQueue

mp.freeze_support()
app = wx.App() 
MyMainFrame = MacroQueue()
MyMainFrame.Show()
app.MainLoop()