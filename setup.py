from distutils.core import setup
setup(
  name = 'MacroQueue',         # How you named your package folder (MyLib)
  packages = ['MacroQueue'],   # Chose the same as "name"
  version = '0.1.16',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Automating Scanning Probe Microscopy',   # Give a short description about your library
  author = 'Brad Goff',                   # Type in your name
  author_email = 'guptagroupstm@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/guptagroupstm/STMMacroQueue',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/guptagroupstm/STMMacroQueue/archive/refs/tags/v0.1.12.tar.gz',    # I explain this later on
  keywords = ['Automation', 'Scanning Probe Microscopy', 'Macro',"Queue"],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'wxPython',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Science/Research',      # Define that your audience are developers
    'Topic :: Scientific/Engineering :: Physics',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.9',
  ],
    package_data={'MacroQueue': ['Functions\*.py','Macros\*.json',"Bitmaps\*.bmp"]},
    include_package_data=True,
)