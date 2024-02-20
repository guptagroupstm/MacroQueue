import unittest
import os
from Dialogs import LoadMacros, GetFunctionList


class STMThread_test(unittest.TestCase):
    def test_ReadMacro(self):
        ThisMacro = LoadMacros("datafiles\\TestMacro.json")
        
    def test_ReadFunctions(self):
        TheseFunctions = GetFunctionList("datafiles\\TestFunctions.py")

if __name__ == '__main__':
    application_path = os.path.dirname(__file__)
    os.chdir(os.path.realpath(application_path))
    unittest.main()