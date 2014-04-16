from __future__ import absolute_import
###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing all of the RelaxWarning objects."""

# Python module imports.
import inspect
import sys
import warnings

# relax module imports.
from lib import ansi


# Module variables for changing the behaviour of the warning system.
ESCALATE = False    # If True, warnings will be converted into errors.
TRACEBACK = False    # If True, a traceback will be printed out with the warnings.


# The warning formatting function.
def format(message, category, filename, lineno, line=None):
    """Replacement for warnings.formatwarning to customise output format."""

    # Add the text 'RelaxWarning: ' to the start of the warning message.
    message = "RelaxWarning: %s\n" % message

    # Text colouring
    if ansi.enable_control_chars(stream=2):
        # Strip the last newline, if it exists.
        if message[-1] == '\n':
            message = message[:-1]

        # Reformat.
        message = "%s%s%s\n" % (ansi.relax_warning, message, ansi.end)

    # Return the warning message.
    return message


def showwarning_tb(message, category, filename, lineno, file=None, line=None):
    """Replacement for warnings.showwarning to show tracebacks."""

    # Set up the output file if needed.
    if file is None:
        file = sys.stderr

    # Print the stack traceback.
    tb = ""
    for frame in inspect.stack()[1:]:
        file_name = frame[1]
        lineNo = frame[2]
        func = frame[3]
        tb_frame = '  File "%s", line %i, in %s\n' % (file_name, lineNo, func)
        try:
            context = frame[4][frame[5]]
        except TypeError:
            pass
        else:
            tb_frame = '%s    %s\n' % (tb_frame, context.strip())
        tb = tb_frame + tb
    tb = "Traceback (most recent call last):\n%s" % tb
    file.write(tb)

    # Replicating the failsafe mode of the base Python warnings function here.
    try:
        file.write(format(message, category, filename, lineno, line))
    except IOError:
        pass


def setup():
    """Set up the warning system."""

    # Format warning messages.
    warnings.formatwarning = format

    # Tracebacks.
    if TRACEBACK:
        warnings.showwarning = showwarning_tb

    # Set warning filters.
    if ESCALATE:
        warnings.filterwarnings('error', category=BaseWarning)
    else:
        warnings.filterwarnings('always', category=BaseWarning)



# Base class for all warnings.
##############################

class BaseWarning(Warning):
    def __str__(self):
        return str(self.text)


# Standard warnings.
####################

class RelaxWarning(BaseWarning):
    def __init__(self, text):
        self.text = text


# Sequence errors.
##################

# Cannot find the spin in the sequence.
class RelaxNoSpinWarning(BaseWarning):
    def __init__(self, spin_id):
        self.text = "Cannot find the spin %s within the sequence." % spin_id


# PDB warnings.
###############

# Zero length interactomic vector.
class RelaxZeroVectorWarning(BaseWarning):
    def __init__(self, spin_id1, spin_id2):
        self.text = "The interatomic vector between the spins '%s' and '%s' is of zero length." % (spin_id1, spin_id2)


# The atom is missing from the PDB file.
class RelaxNoAtomWarning(BaseWarning):
    def __init__(self, atom, res):
        self.text = "The atom %s could not be found for residue %i" % (atom, res)


# The PDB file is missing.
class RelaxNoPDBFileWarning(BaseWarning):
    def __init__(self, file):
        self.text = "The PDB file %s cannot be found, no structures will be loaded." % file


# Nuclear warnings.
###################

# Nucleus not set.
class RelaxNucleusWarning(BaseWarning):
    def __init__(self, spin_id=None):
        if spin_id != None:
            self.text = "The type of nucleus for the spin '%s' has not yet been set." % spin_id
        else:
            self.text = "The type of nucleus has not yet been set."

# Spin type not set.
class RelaxSpinTypeWarning(BaseWarning):
    def __init__(self, spin_id=None):
        if spin_id != None:
            self.text = "The nuclear isotope type for the spin '%s' has not yet been set.  Please use the spin.isotope user function to set the type." % spin_id
        else:
            self.text = "The nuclear isotope type has not yet been set.  Please use the spin.isotope user function to set the type."

# File warnings.
################

# No data in file.
class RelaxFileEmptyWarning(BaseWarning):
    def __init__(self, file):
        self.text = "The file '%s' contains no data." % file


# Misc.
#######

# Deselection warnings
class RelaxDeselectWarning(BaseWarning):
    def __init__(self, spin_id, reason):
        self.text = "The spin '%s' has been deselected because of %s." % (spin_id, reason)
