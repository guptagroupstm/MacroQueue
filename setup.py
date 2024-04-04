from distutils.core import setup


try:
   import pypandoc
   long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
# read the contents of your README file
  from pathlib import Path
  this_directory = Path(__file__).parent
  long_description = (this_directory / "README.md").read_text()
print(long_description)
setup(
  name = 'MacroQueue',         # How you named your package folder (MyLib)
  packages = ['MacroQueue'],   # Chose the same as "name"
  version = '0.2.5',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Automating Scanning Probe Microscopy',   # Give a short description about your library
  author = 'Brad Goff',                   # Type in your name
  author_email = 'guptagroupstm@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/guptagroupstm/STMMacroQueue',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/guptagroupstm/STMMacroQueue/archive/refs/tags/v0.2.5.tar.gz',    # I explain this later on
  keywords = ['Automation', 'Scanning Probe Microscopy', 'Macro',"Queue"],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'wxPython',
          'pyvisa',
          'PyWin32',
          'pyinstaller'
      ],
  long_description_content_type='text/markdown',
  long_description=long_description,
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Science/Research',      # Define that your audience are developers
    'Topic :: Scientific/Engineering :: Physics',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.9',
  ],
    package_data={'MacroQueue': ['Functions\*.py','Macros\*.json',"Bitmaps\*.bmp",'MacroQueueIcon.ico','MakeExe.sh']},
    include_package_data=True,
)