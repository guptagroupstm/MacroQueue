Special Functions
===============================

The Initialize Function
-------------------------
For each STM system, there is a function called Initialize.  It is run to connect to the STM.

It should be modified conservatively.

::

    def Initialize():
        global STM
        pythoncom.CoInitialize()
        STM = win32com.client.Dispatch("pstmafm.stmafmrem")
        time.sleep(0.3)

The OnClose Function
----------------------------
Each STM system also has a function called "OnClose".  It runs when MacroQueue is closed.  It is used to ensure that the BField, RF generator, etc. are all turned off.

You can either turn off the instruments (as shown with the RF generator below), or you can prevent MacroQueue from closing and produces a popup error (As shown with the BField below).

::

    def OnClose():
        if STM is not None:
            pass

        if RFGenerator is not None:
            Turn_Off_RF_Generator()

        if BField is not None:
            OutgoingQueue.put(("DontClose","The Magnetic Field is not off.  Run the function 'Turn B Field Off'."))
            MacroQueueSelf.Closing=False


