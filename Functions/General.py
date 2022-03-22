from time import sleep

Cancel = False


# WaitTime=s;The time to wait in seconds
def Wait(WaitTime=1):
    sleep(WaitTime)

def Print(Number=0):
    global Cancel
    print(Number)
    print(Cancel)
    print('')

# Boolean=Does something if it's true
# Choice=Make a choice
def Test(Boolean=True,String="String",Choice=['Choice','Combo','3rd','4th']):
    a = 'hi'*5.3
    pass