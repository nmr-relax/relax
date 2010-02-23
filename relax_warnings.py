###############################################################################
#                                                                             #
# Copyright (C) 2003-2009 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing all of the RelaxWarning objects."""


# Python module imports.
import warnings
import inspect

# relax module imports.
from relax_errors import BaseError


# Global variables.
Debug = False
Pedantic = False


# The warning formatting function.
def format(message, category, filename, lineno, line=None):
    """ Replacement for warnings.formatwarning to customise output format."""

    # Add the text 'RelaxWarning: ' to the start of the warning message.
    #if issubclass(category, BaseWarning):
    message = "RelaxWarning: %s\n" % message

    # Print stack-trace in debug mode.
    if Debug:
        tb = ""
        for frame in inspect.stack()[4:]:
            file = frame[1]
            lineNo = frame[2]
            func = frame[3]
            tb_frame = '  File "%s", line %i, in %s\n' % (file, lineNo, func)
            try:
                context = frame[4][frame[5]]
            except TypeError:
                pass
            else:
                tb_frame = '%s    %s\n' % (tb_frame, context.strip())
            tb = tb_frame + tb
        tb = "Traceback (most recent call last):\n%s" % tb
        message = tb + message

    # Return the warning message.
    return message


# Base class for all warnings.
##############################

class BaseWarning(Warning, BaseError):
    def __str__(self):
        return self.text


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

# Zero length XH bond vector.
class RelaxZeroVectorWarning(BaseWarning):
    def __init__(self, res):
        self.text = "The XH bond vector for residue " + repr(res) + " is of zero length."


# The atom is missing from the PDB file.
class RelaxNoAtomWarning(BaseWarning):
    def __init__(self, atom, res):
        self.text = "The atom %s could not be found for residue %i" % (atom, res)


# The PDB file is missing.
class RelaxNoPDBFileWarning(BaseWarning):
    def __init__(self, file):
        self.text = "The PDB file %s cannot be found, no structures will be loaded." % file


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



# Format warning messages.
warnings.formatwarning = format

# Set warning filters.
if Pedantic:
    warnings.filterwarnings('error', category=BaseWarning)
else:
    warnings.filterwarnings('always', category=BaseWarning)


