Error Handling
===============================

Soft limits
-------------------

A minimum and maximum can be specified for a numerical parameter in the metadata of a funtion, see :doc:`WriteFunction`:


.. image:: ./Error1.png

When a user attempts to put a value in that's out of range, the parameter will turn yellow:

.. image:: ./Error2.png

If the user decides to ignore the warning and adds the macro to the queue, there is a pop-up to confirm:

.. image:: ./Error3.png
    :width: 300

Exceptions and hard limits
--------------------------------------

You can put a hard limit for any parameter by raising an exception.  

Any exception, either intentional or not, will pause the queue, cancel the current macro, and create a pop-up showing the exception that was raised.::

    # {"Name":"SomeParameter","Max":10}
    def Exception_Function(SomeParameter=5):
        if SomeParameter > 10:
            raise ValueError(f"{SomeParameter} is too large.")

.. image:: ./Error4.png
