from time import sleep

Cancel = False
MacroQueueSelf = None


def Bare_Function(SomeParameter=""):
    print(SomeParameter)


# {"Name":"SomeNumber","Units":"V","Min":-10,"Max":10,"Tooltip":"An example function which only takes numbers"}
def Numerical_Function(SomeNumber=5):
    print(SomeNumber)

# {"Name":"Boolean","Tooltip":"A Boolean parameter produces a checkbox"}
# {"Name":"String","Tooltip":"A String parameter produces a textbox"}
# {"Name":"Choice","Tooltip":"A Choice parameter produces a dropdown menu"}
def Complex_Function(Boolean=True,String="String",Choice=['Choice','Combo','3rd','4th']):
    if Boolean:
        print(String, Choice)


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

