Changing Systems & Adding a new one
==================================================

When lauching MacroQueue for the first time, you will be asked what system you will be using:

.. image:: ./Change1.png
    :width: 250

You are able to change it later under the 'system' menu:


.. image:: ./Change2.png

.. image:: ./Change3.png

When you change systems, the macros for the old system is automatically replaced with the macros for the new system.


If you have several systems that use the same software, e.g. 2 different CreaTec systems, you can include other functions for other Instruments seperately.

.. image:: ./Change4.png



Adding a New System
------------------------

You can specify that a python file under Functions is a new system instead of auxiliary equipment by adding it to the list of systems in *General.py*.

For example, I created a new file called *Testing.py* in the Functions folder. I can make it a system by adding 'Testing' to the list::


    Systems =['RHK','CreaTec','SXM',"Testing"]
    IgnoreFiles =["SXMRemote.py"]

.. image:: ./NewSystem1.png
    :width: 250

.. image:: ./NewSystem2.png
