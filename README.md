# MacroQueue: Automating Measurements in High-Dimensional Parameter Spaces


Laboratory measurements for systems with high-dimensional parameter spaces often require several different instruments for a single measurement; such as, an external lock-in amplifer, an electromagnet, a RF generator, etc..  Often, these intruments have to be manually controlled and then their parameters have to be manually recorded.  MacroQueue is a modular software designed for controlling and automating various laboratory instruments in sync.


Users can easily add python functions to control new and existing equipment.  Although any arbitary python function can be added, the base functions were created with the functional programming paradigm in mind, so the functions are small and each perform a single task.  For example, the function "Set RF Frequency", changes the frequency on the RF generator and records the new value.  This allows the functions to be reused for many types of measurements.

The functions can be grouped into macros for each type of measurement.  Macros are added to a queue with different values for each parameter (e.g. bias, magnetic field, etc.) to perform measurements throughout a parameter space.  Each measurement is performed consecutively on a seperate thread to enable measurements in the queue to be modified.
These features allow users to easily control several instruments in sync, perform a long series of measurements with minimal input, and add new instruments to a system. 
The goal of MacroQueue is to provide a GUI that allow users to perform measurements in high-dimensional parameter spaces without requiring coding ability while still providing users with coding ability the flexibility to write arbitrarily complex functions.  

Check out for the [documentation](https://guptagroupstm.github.io/MacroQueue/index.html) for more information.


![Brief image of MacroQueue](https://raw.githubusercontent.com/guptagroupstm/MacroQueue/main/docs_src/source/ReadMe.png)

![Brief image of MacroQueue](https://raw.githubusercontent.com/guptagroupstm/MacroQueue/main/docs_src/source/ExpandingFigure.png)


## Installation

See the [install documentation](https://guptagroupstm.github.io/MacroQueue/Install.html). System requirements are also found in this page.

## Contributing

Please read [documentation](https://guptagroupstm.github.io/MacroQueue/Contributing.html) for details on our code of conduct, and the process for submitting pull requests to us.

## Acknowledgements

MacroQueue was built by Brad Goff as part of the Gupta Group in the physics department at The Ohio State University. Visit our group’s website here: https://u.osu.edu/guptagroup/.

This work was primarily supported by the Department of Energy (DOE) Basic Energy Sciences under Grant No. DE-SC0016379.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details