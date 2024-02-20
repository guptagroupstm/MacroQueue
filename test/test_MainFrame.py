import unittest
import shutil
import os
import warnings
from MacroQueue import *
import multiprocessing as mp

class MainFrame_test(unittest.TestCase):
    def test_GUI(self):
        mp.freeze_support()
        self.app = wx.App() 
        self.MyMainFrame = MainFrame()
        self.MyMainFrame.Show()
        self.MyMainFrame.CheckQueue(event=None)
        self.MyMainFrame.IdleLoop(event=None)
        self.MyMainFrame.OnClose()
    

if __name__ == '__main__':
    unittest.main()