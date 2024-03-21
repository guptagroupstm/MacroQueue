Installation
=============================

System requirements
-------------------------
- Python (version >= 3.9).

Installation from pip (recommended)
----------------------------------------------------

1. Update pip::

    pip install --upgrade pip

2. Install MacroQueue by pip::

    pip install MacroQueue

3. Start MacroQueue by the command below::

    python -m MacroQueue

4. (Optional) Create an executable by running the following command in MacroQueue's folder::

    .\MakeExe.sh

    
Installation from source (not recommended)
--------------------------------------------------------

If you want to install `MacroQueue` from source, follow the instructions below.
In particular, this is recommended if you want to use :doc:`Tutorials/test`.

1. Update pip::

    pip install --upgrade pip

2. Clone MacroQueue. If you do not have git, you can download the source code from GitHub (https://github.com/guptagroupstm/STMMacroQueue)::

    git clone github.com/guptagroupstm/STMMacroQueue

3. (Optional) If you want to check installation, go to :doc:`Tutorials/test`.

4. Start *MacroQueue* by the command below::

    python MacroQueue

5. (Optional) Create an executable by running the following command *in MacroQueue's folder*::

    .\MakeExe.sh

Library version
-------------------------

We confirmed that *MacroQueue* works well under the environment below. If *MacroQueue* does not work, try the library versions below.

Python 3.9.13

- Numpy 1.26.2
- Pandas 2.0.3
- wxPython 4.2.1
- PyWin32 301
- PyVisa 1.11.3
- PyInstaller 6.2.0