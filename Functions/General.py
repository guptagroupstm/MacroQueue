from time import sleep

Cancel = False


# WaitTime=The time to wait in s
def Wait(WaitTime=10):
    sleep(WaitTime)

def Print(Number=0):
    global Cancel
    print(Number)
    print(Cancel)
    print('')

# Boolean=Does something if it's true
# Choice=Make a choice
def Test(Boolean=True,String="String",Choice=['Choice','Combo','3rd','4th']):
    print(Boolean,String,Choice)
    pass