import win32com.client
import time

STM = win32com.client.Dispatch("pstmafm.stmafmrem")

def dI_dV(Bias,Setpoint,ImageSize,XOffset=0,YOffset=0,nTCperPixel=2,NPixels=512,LIAmp=20,CheckTime=10):
    # Bias in V
    # Setpoint in A
    # ImageSize in nm
    # X/YOffset in nm

    STM.setp('LOCK-IN.CHANNEL','ADC1')
    STM.setp('LOCK-IN.AMPLITUDE.MVPP',LIAmp)
    STM.setp('LOCK-IN.MODE','Internal ')
    STM.setp('SCAN.BIASVOLTAGE.VOLT',Bias)
    STM.setp('SCAN.SETPOINT.AMPERE',Setpoint)
    STM.setp('SCAN.CHANNELS',('TOPOGRAPHY','CURRENT','Lock-in X'))
    STM.setp('STMAFM.CMD.MOVE_TIP.NEWPOS.NM',(XOffset,YOffset,1))
    STM.setp('SCAN.IMAGESIZE.NM.X',ImageSize)
    STM.setp('SCAN.IMAGESIZE.PIXEL', (NPixels, NPixels))
    TC = 1./float(STM.getp('LOCK-IN.RC.HZ',''))
    Speed = (ImageSize/NPixels)  / (TC*nTCperPixel)
    STM.setp('SCAN.SPEED.NM/SEC',Speed)
    Status = STM.getp('STMAFM.SCANSTATUS','')
    STM.setp('STMAFM.BTN.START' ,'')
    Status = STM.getp('STMAFM.SCANSTATUS','')
    while Status == 2:
        time.sleep(CheckTime)
        Status = STM.getp('STMAFM.SCANSTATUS','')

if __name__ == "__main__":
    # dI_dV(Bias=1,Setpoint=1,ImageSize=100)
    # dI_dV(Bias=2,Setpoint=1,ImageSize=100)
    X = STM.getp('BASICPARAM.GET',"Offsetx")
    Y = STM.getp('BASICPARAM.GET',"Offsety")
    print(X,Y)
    time.sleep(1)
    X = STM.setp('BASICPARAM.SET',("Offsetx",100))
    Y = STM.setp('BASICPARAM.SET',("Offsety",100))
    time.sleep(1)
    X = STM.getp('BASICPARAM.GET',"Offsetx")
    Y = STM.getp('BASICPARAM.GET',"Offsety")
    print(X,Y)