import unittest
import multiprocessing as mp
import sys
import os
sys.path.append('..')
from MacroQueue import *

class MainFrame_test(unittest.TestCase):
    def test_GUI(self):
        mp.freeze_support()
        self.app = wx.App() 
        self.MyMainFrame = MainFrame()
        self.MyMainFrame.CheckQueue(event=None)
        self.MyMainFrame.IdleLoop(event=None)
        self.MyMainFrame.Close()
        pass
    

if __name__ == '__main__':
    unittest.main()