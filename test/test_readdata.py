import unittest
import os
from Dialogs import LoadMacros, GetFunctionList


class STMThread_test(unittest.TestCase):
    def test_ReadMacro(self):
        application_path = os.path.dirname(__file__)
        os.chdir(os.path.realpath(application_path))
        ThisMacro = LoadMacros("datafiles\\TestMacro.json")
        
    def test_ReadFunctions(self):
        application_path = os.path.dirname(__file__)
        os.chdir(os.path.realpath(application_path))
        TheseFunctions = GetFunctionList("datafiles\\TestFunctions.py")

if __name__ == '__main__':
    unittest.main()