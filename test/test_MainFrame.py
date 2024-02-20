import unittest
import multiprocessing as mp
import sys
import os
application_path = os.path.dirname(__file__)
sys.path.append(os.path.realpath(application_path+'\\..'))
from MacroQueue import *

class MainFrame_test(unittest.TestCase):
    def test_GUI(self):
        app = wx.App() 
        MyMainFrame = MainFrame()
        MyMainFrame.CheckQueue(event=None)
        MyMainFrame.IdleLoop(event=None)
        MyMainFrame.Close()
        app.OnExit()
        wx.Exit()
        
        pass
    

if __name__ == '__main__':
    unittest.main()