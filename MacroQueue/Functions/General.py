from time import sleep

Cancel = False
MacroQueueSelf = None



# {"Name":"SomeParameter","Max":10}
def Exception_Function(SomeParameter=5):
    if SomeParameter > 10:
        raise ValueError(f"{SomeParameter} is too large.")
    pass


def Bare_Function(SomeParameter,SomeParameter2="a"):
    print(SomeParameter)
    print("Hehehe")

# {"Name":"SomeNumber","Units":"V","Min":-10,"Max":10,"Tooltip":"An example function which only takes numbers"}
def Numerical_Function(SomeNumber=5):
    print(SomeNumber)

# {"Name":"SomeBoolean","Tooltip":"A Boolean parameter produces a checkbox"}
# {"Name":"SomeString","Tooltip":"A String parameter produces a textbox"}
# {"Name":"SomeFilePath","Tooltip":"A filepath parameter produces a 'browse' button"}
# {"Name":"SomeChoice","Tooltip":"A Choice parameter produces a dropdown menu"}
def Complex_Function(SomeBoolean=True,SomeString="String",SomeFilePath="C:\\",SomeChoice=['Choice','Combo','3rd','4th']):
    if SomeBoolean:
        print(SomeString, SomeChoice)


# {"Name":"WaitTime","Units":"s","Tooltip":"The time to wait"}
def Wait(WaitTime=1):
    while WaitTime > 1 and not Cancel:
        WaitTime-=1
        sleep(1)
    if not Cancel:
        sleep(WaitTime)


# Index=This has no impact.  It's solely used to repeat the functions.
def Null(Index=0):
    pass

# Pauses the queue until the resume button is pressed.
def Pause():
    MacroQueueSelf.Pause()

def Print(Number=0):
    print(Number)
    print('')

