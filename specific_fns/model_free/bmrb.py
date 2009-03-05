###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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

# relax module imports.
from bmrblib.nmr_star_dict_v3_1 import NMR_STAR_v3_1
from generic_fns import mol_res_spin, relax_data
from generic_fns.mol_res_spin import spin_loop
from generic_fns.pipes import get_pipe


class Bmrb:
    """Class containing methods related to BMRB STAR file reading and writing."""

    def bmrb_read(self, file_path):
        """Read the model-free results from a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the NMR-STAR data object.
        star = NMR_STAR_v3_1('relax_model_free_results', file_path)

        # Read the contents of the STAR formatted file.
        star.read()


    def bmrb_write(self, file_path):
        """Write the model-free results to a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the NMR-STAR data object.
        star = NMR_STAR_v3_1('relax_model_free_results', file_path)

        # Get the current data pipe.
        cdp = get_pipe()

        # Generate the entity saveframe.
        mol_res_spin.bmrb_write_entity(star)

        # Generate the relaxation data saveframes.
        relax_data.bmrb_write(star)

        # Write the contents to the STAR formatted file.
        star.write()
