Multiple Parameters
==================================================



When inputing numerical parameters, you may simultaneously add several items to the queue in two ways. 
You may input either 1,3,7,9 or 1;3;7;9 and 4 macros will be added to the queue, each with a different value of the parameter. 

If you want the values to be evenly spaced, you may also input -1,1,0.1.  This will add 21 parameters to the queue, from -1 to 1 with a step size of 0.1. The format is '{Start}, {End}, {Step size}'.  Writing -1,1,0.1 is identical to writing -1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1

You may use a negative step size if you would like to have the values decrease: 0,-10,-1.
If you want to input only 3 values, you may use semicolons ;.  -1;1;0.1 will not be expanded.



It is important to note that in the macros after the first, only the functions after the expanded function are included.  
For example, if there was a macro to (1) Set a BField, (2) wait some time, (3) set the bias, and (4) scan,
and we wanted to take two scans with a BField = 1T and biases -0.8 and 0.8, you can input -0.8,0.8 to the bias.
There will be 2 macros added to the queue.  The first will have all 4 functions.  It will set the bias to -0.8.  
The second macro will only set the bias to 0.8 and scan.  
If you wanted 4 scans, with BField = -1,1 and biases=-0.8,0.8,
you may input all the parameters and 4 macros will be added to the queue.
The first and third macro will (1) set the BField, (2) wait some time, (3) set the bias to -0.8, and scan.  The second and fourth will only set the set the bias to 0.8 and scan.
