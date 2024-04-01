---
title: 'MacroQueue: Automating Scanning Probe Microscopy'
tags:
  - Python
  - Scanning Probe Microscopy
  - Automation
authors:
  - name: Brad M. Goff
    orcid: 0000-0002-4108-6758
    affiliation: 1
  - name: Jay A. Gupta
    orcid: 0000-0002-3908-7719
    corresponding: true 
    affiliation: 1
affiliations:
 - name: The Ohio State University, USA
   index: 1
date: 21 Feburary 2024
bibliography: paper.bib
---

# Summary

Scanning Probe Microscopy (SPM) operators often use several different instruments for a single measurement; such as, an external lock-in amplifer, an electromagnet, a RF generator, etc..  Often, these intruments have to be manually controlled and then their parameters have to be manually recorded.  MacroQueue is a modular software designed for controlling and automating SPM systems and various other laboratory equipment in sync.  It provides a single GUI to control the 3 major commerical SPMs, CreaTec, RHK, and Scienta Omicron in combination with any other instruments that are apart of the systems.  

Users can easily add python functions to control new and existing equipment.  Although any arbitary python function can be added, the base functions were created with the functional programming paradigm in mind, so the functions are small and each perform a single task.  For example, the function "Set RF Frequency", changes the frequency on the RF generator and records the new value.  This allows the functions to be reused for many types of measurements.

The functions are grouped into a macro for each type of measurement.  Macros are added to a queue with different values for each parameter (e.g. bias, magnetic field, etc.) to perform measurements throughout a parameter space.  Each measurement is performed consecutively on a seperate thread to enable measurements in the queue to be modified.
These features allow users to easily control several instruments in sync, perform a long series of measurements with minimal input, and add new instruments to a system. 



# Statement of need

Numerous instruments have to be controlled in sync to access the full parameter space of an SPM system.  This is typically automated with python scripts for longer measurements, such as QPI mapping @MacroQueueDocs which is a series of a dozen measurements, each taking an hour.  Writing a python script for each type of measurement leads to the spagetti code that physists are notoriously known for at best, and at worst, is prohibitively difficult for novice SPM operators.  MacroQueue provides a simple GUI and allows users to easily add or modify functions to control new and existing equipment.  This software is currently in active use in several laboratories at The Ohio State University and the NSF NeXUS Facility.  Several similar packages already exist, such as @PyMeasure, @bluesky, and @ScopeFoundry2023  A good overview of available Python packages can be found in [@buchner_2022_6399528].  The goal of MacroQueue is to provide a GUI that allow users to perform measurements in high-dimensional parameter spaces without requiring coding ability while still providing users with coding ability the flexibility to write arbitrarily complex functions.  
 

# Overview




MacroQueue can be packaged into an executable, by either using the provided script or using PyInstaller directly, so that coding is completely optional.  To further allow the user experience to be as simple as possible, a basic python function is all that is nessesary to add a function.  Everything else is handled automatically.  Even as a executable, users can open the "source folder" via the File menu where they can find different python files to control various intstruments.  Upon launching, MacroQueue searches this folder for new files.  Every function, from each python file, is dynamically imported using the package importlib, part of python's standard library.  For each parameter in a function, MacroQueue reads the default value to interpret the datatype (e.g. string, numerical, boolean, list) and the appriate control in the GUI (e.g. text box, numbers only text box, checkmark, dropdown menu respectively).  \autoref{fig:ExampleCode} shows example code and the various controls that are produced in the GUI.  

![The workflow for adding a new function and defining a new macro.\label{fig:ExampleCode}](Figure1.png)

For additional features, users can write metadata for each parameter in comments above each function.  The metadata includes units and an explation of what the parameter does, which will be included in the parameters's hover tooltip.  Numerical values can also have a soft minimum and/or maximum value in their metadata; when a users tries to input a value outside the range, there will be a pop-up warning to confirm that they want to proced.  Hard limits can be applied in indiviual funtions by throwing an exception in typical pythonic fashion.  If an exception is thrown in any of the functions, the queue will be paused, the current macro will be canceled, and a pop-up will provide the user with the exception's details.


MacroQueue makes a GUI, shown in \autoref{fig:AddMacro}, using the WxPython toolkit @WxPython.  The queue is on the left, showing the macros that will be run.  Macros can be defined for each type of measurement to combine several functions into a single package.  When macros are in the queue, they will be ran one at a time until the queue is empty or paused.  New macros can be defined via the Macro menu and existing Macros can be edited by right clicking on their corresponding button in the center of the GUI.  By left clicking a macro's button, it will bring up the menu where you can edit which functions in the macro will be run and the values for each parameter that will be used, shown in \autoref{fig:ExampleCode}.  Multple copies of the same macro, with different values for parameters, can conveniently be added to the queue simultaneously by adding multiple values for each parameter, seperated by commas, as shown in \autoref{fig:AddMacro}.  In additon, numerical parameters can expanded by using the format: start, stop, stepsize; e.g. 1,10,0.5 is equilvent to inputting all values between 1 and 10, inclusively, in steps of 0.5.  This can be used to quickly add thousands of macros to the queue.

![The workflow for adding macros to the queue.\label{fig:AddMacro}](Figure2.png)


# Acknowledgements

This work was primarily supported by the Department of Energy (DOE) Basic
Energy Sciences under Grant No. DE-SC0016379.

# References
