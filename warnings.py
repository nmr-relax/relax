###############################################################################
#                                                                             #
# Copyright (C) 2003-2007 Edward d'Auvergne                                   #
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

import __builtin__
from re import match
from types import ClassType
import warnings
import inspect



# The RelaxWarning system.
##########################

class RelaxWarnings:
    def __init__(self):
        """Class for placing all the warnings below into __builtin__"""

        # Loop over all objects in 'self'.
        for name in dir(self):
            # Get the object.
            object = getattr(self, name)

            # Skip over all non-warning class objects.
            if type(object) != ClassType or not match('Relax', name):
                continue

            # Place the warnings into __builtin__
            __builtin__.__setattr__(name, object)

            # Tuple of all the warnings.
            if hasattr(__builtin__, 'AllRelaxWarnings'):
                __builtin__.AllRelaxWarnings = __builtin__.AllRelaxWarnings, object
            else:
                __builtin__.AllRelaxWarnings = object,

        # Format warning messages.
        warnings.formatwarning = self.format

        # Set warning filters.
        if Pedantic:
            warnings.filterwarnings('error', category=self.BaseWarning)
        else:
            warnings.filterwarnings('always', category=self.BaseWarning)


    def format(self, message, category, filename, lineno):
        """ Replacement for warnings.formatwarning to customise output format."""

        # Add the text 'RelaxWarning: ' to the start of the warning message.
        if issubclass(category, self.BaseWarning):
            message = "RelaxWarning: %s\n\n" % message

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

    class BaseWarning(Warning, RelaxErrors.BaseError):
        def __str__(self):
            return self.text


    # Standard warnings.
    ####################

    class RelaxWarning(BaseWarning):
        def __init__(self, text):
            self.text = text


    # PDB warnings.
    ###############

    # Zero length XH bond vector.
    class RelaxZeroVectorWarning(BaseWarning):
        def __init__(self, res):
            self.text = "The XH bond vector for residue " + `res` + " is of zero length."


    # The atom is missing from the PDB file.
    class RelaxNoAtomWarning(BaseWarning):
        def __init__(self, atom, res):
            self.text = "The atom %s could not be found for residue %i" % (atom, res)


    # The PDB file is missing.
    class RelaxNoPDBFileWarning(BaseWarning):
        def __init__(self, file):
            self.text = "The PDB file %s cannot be found, no structures will be loaded." % file
