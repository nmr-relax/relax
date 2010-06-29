"""This system test catches the unicode selection bug submitted by Olivier Serve.

The bug is:
    - Bug #14872 (https://gna.org/bugs/?14872).
"""

# Python module imports.
import __main__
from os import sep
import sys


# Path of the files.
path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'bug_14872_unicode_selection'

# Set the data pipe names.
pipes = ['m4', 'm5']

# Loop over the data pipe names.
for name in pipes:
    print "\n\n# " + name + " #"

    # Create the data pipe.
    pipe.create(name, 'mf')

    # Reload precalculated results from the files 'm1/results', etc.
    results.read(file='results', dir=path+sep+name)

# Model elimination.
eliminate()

# Model selection.
model_selection(method='AIC', modsel_pipe='aic', pipes=pipes)
