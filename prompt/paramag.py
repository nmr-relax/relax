###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module containing the user function class for paramagnetic related functions."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns import paramag
from relax_errors import RelaxError
from status import Status; status = Status()


class Paramag(User_fn_class):
    """Class for handling paramagnetic information."""

    def centre(self, pos=None, atom_id=None, pipe=None, verbosity=1, fix=True, ave_pos=True, force=False):
        """Specify which atom is the paramagnetic centre.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pos:  The atomic position.

        atom_id:  The atom ID string.

        pipe:  The data pipe containing the structures to extract the centre from.

        verbosity:  The amount of information to print out.

        fix:  A flag specifying if the paramagnetic centre should be fixed during optimisation.

        ave_pos:  A flag specifying if the position of the atom is to be averaged across all models.

        force:  A flag which if True will cause the current paramagnetic centre to be overwritten.


        Description
        ~~~~~~~~~~~

        This function is required for specifying where the paramagnetic centre is located in the
        loaded structure file.  If no structure number is given, then the average atom position will
        be calculated if multiple structures are loaded.

        A different set of structures than those loaded into the current data pipe can also be used
        to determine the position, or its average.  This can be achieved by loading the alternative
        structures into another data pipe, and then specifying that pipe through the pipe argument.

        If the ave_pos flag is set to True, the average position from all models will be used as the
        position of the paramagnetic centre.  If False, then the positions from all structures will
        be used.  If multiple positions are used, then a fast paramagnetic centre motion will be
        assumed so that PCSs for a single tensor will be calculated for each position, and the PCS
        values linearly averaged.


        Examples
        ~~~~~~~~

        If the paramagnetic centre is the lanthanide Dysprosium which is labelled as Dy in a loaded
        PDB file, then type one of:

        relax> paramag.centre('Dy')
        relax> paramag.centre(atom_id='Dy')

        If the carbon atom 'C1' of residue '4' in the PDB file is to be used as the paramagnetic
        centre, then type:

        relax> paramag.centre(':4@C1')
        
        To state that the Dy3+ atomic position is [0.136, 12.543, 4.356], type one of:

        relax> paramag.centre([0.136, 12.543, 4.356])
        relax> paramag.centre(pos=[0.136, 12.543, 4.356])

        To find an unknown paramagnetic centre, type:

        relax> paramag.centre(fix=False)
        """

        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "paramag.centre("
            text = text + "pos=" + repr(pos)
            text = text + ", atom_id=" + repr(atom_id)
            text = text + ", pipe=" + repr(pipe)
            text = text + ", verbosity=" + repr(verbosity)
            text = text + ", fix=" + repr(fix)
            text = text + ", ave_pos=" + repr(ave_pos)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num_list(pos, 'atomic position', size=3, can_be_none=True)
        arg_check.is_str(atom_id, 'atom ID string', can_be_none=True)
        arg_check.is_str(pipe, 'data pipe', can_be_none=True)
        arg_check.is_int(verbosity, 'verbosity level')
        arg_check.is_bool(fix, 'fix flag')
        arg_check.is_bool(ave_pos, 'average position flag')
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        paramag.centre(pos=pos, atom_id=atom_id, pipe=pipe, verbosity=verbosity, fix=fix, ave_pos=ave_pos, force=force)
