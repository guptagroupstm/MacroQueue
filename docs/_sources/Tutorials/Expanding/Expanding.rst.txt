Multiple Parameters
==================================================

Adding Multiple Macros
-------------------------

When inputing numerical parameters, you may simultaneously add several items to the queue in three ways. 

- You may input lists of values (e.g. 1,3,7,9) and macros with each value will be added to the queue. 

.. image:: ./Expanding1.png

.. image:: ./Expanding5.png


- If you want the values to be evenly (linearly) spaced, you may also input 3 numbers with a format of 'Start, End, Step size'.  Writing 2,10,2 is identical to writing 2, 4, 6, 8, 10.  

    .. image:: ./Expanding2.png


    - You may use a negative step size if you would like to have the values decrease: 0,-10,-1.

    .. image:: ./Expanding3.png

    - If you want to input 3 values without expanding them, you may use semicolons instead of commas.  -1;1;0.1 will *not* be expanded.

    .. image:: ./Expanding4.png

- If you want the values to be logarithmically spaced, see :doc:`../LogParameters`.


Which Functions will Run
--------------------------

It is important to note that when a user inputs multiple values for numerical parameters, MacroQueue will 'expand' the macro into multiple macros, with each value, to the queue.  
The macros are created as if there is a for loop at the expanding function and every function below the expanding function is inside the loop. 

That is to say, if there are two functions each with 2 values, the first funciton will run twice and the second function will run four times (twice for each time the first function ran).


For example, let's say I want to (1) change the setpoint, (2) wait some time, (3) change the bias, and (4) scan and I want 2 different setpoints and 2 different biases.  

.. image:: ./Expanding6.png


The first and third macro will have all 4 functions while the second and fourth will only change the bias and scan.
  
.. image:: ./Expanding7.png

You can confirm which functions will run by pressing "edit"

- For the first macro:

    .. image:: ./Expanding8.png
        :width: 400

- For the second macro:

    .. image:: ./Expanding9.png
        :width: 400
