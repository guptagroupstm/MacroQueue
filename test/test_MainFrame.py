import wx
import unittest
import sys
import os
application_path = os.path.dirname(__file__)
sys.path.append(os.path.realpath(application_path+'\\..\\MacroQueue\\'))
from MacroQueue import MacroQueue

class MainFrame_test(unittest.TestCase):
    def test_GUI(self):
        app = wx.App() 
        MyMainFrame = MacroQueue(test=True)
        MyMainFrame.CheckQueue(event=None)
        MyMainFrame.IdleLoop(event=None)
        MyMainFrame.Close()

        
        pass
    

if __name__ == '__main__':
    unittest.main()