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

# Module docstring.
"""The NMR-STAR dictionary API for version 3.1.

The v3.1 NMR-STAR dictionary is documented at
http://www.bmrb.wisc.edu/dictionary/3.1html/SuperGroupPage.html.
"""

# relax module imports.
from bmrblib.kinetics.heteronucl_NOEs_v3_1 import HeteronuclNOESaveframe_v3_1
from bmrblib.kinetics.heteronucl_T1_relaxation_v3_1 import HeteronuclT1Saveframe_v3_1
from bmrblib.kinetics.heteronucl_T2_relaxation_v3_1 import HeteronuclT2Saveframe_v3_1
from bmrblib.nmr_star_dict import NMR_STAR


class NMR_STAR_v3_1(NMR_STAR):
    """The v3.1 NMR-STAR dictionary."""

    def create_saveframes(self):
        """Create all the saveframe objects."""

        # Initialise the objects of this class.
        self.heteronucl_NOEs = HeteronuclNOESaveframe_v3_1(self.data.datanodes)
        self.heteronucl_T1_relaxation = HeteronuclT1Saveframe_v3_1(self.data.datanodes)
        self.heteronucl_T2_relaxation = HeteronuclT2Saveframe_v3_1(self.data.datanodes)
