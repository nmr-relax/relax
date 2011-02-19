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
"""The relaxation data BMRB API interface."""


# relax module imports.
from bmrblib.kinetics.general_relaxation import GeneralRelaxationSaveframe
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOESaveframe
from bmrblib.kinetics.heteronucl_NOEs_v3_1 import HeteronuclNOESaveframe_v3_1
from bmrblib.kinetics.heteronucl_T1_relaxation import HeteronuclT1Saveframe
from bmrblib.kinetics.heteronucl_T1_relaxation_v3_1 import HeteronuclT1Saveframe_v3_1
from bmrblib.kinetics.heteronucl_T2_relaxation import HeteronuclT2Saveframe
from bmrblib.kinetics.heteronucl_T2_relaxation_v3_1 import HeteronuclT2Saveframe_v3_1


class Relaxation:
    """Class for the relaxation data part of the BMRB API."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.__datanodes = datanodes

        # Initialise the kinetic saveframe supergroups.
        self.__heteronucl_NOEs = HeteronuclNOESaveframe(self.datanodes)
        self.__heteronucl_T1_relaxation = HeteronuclT1Saveframe(self.datanodes)
        self.__heteronucl_T2_relaxation = HeteronuclT2Saveframe(self.datanodes)


class Relaxation_v3_0(Relaxation):
    """Class for the relaxation data part of the BMRB API (v3.0)."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.__datanodes = datanodes

        # Initialise the kinetic saveframe supergroups.
        self.__heteronucl_NOEs = HeteronuclNOESaveframe_v3_0(self.datanodes)
        self.__heteronucl_T1_relaxation = HeteronuclT1Saveframe_v3_0(self.datanodes)
        self.__heteronucl_T2_relaxation = HeteronuclT2Saveframe_v3_0(self.datanodes)



class Relaxation_v3_1(Relaxation_v3_0):
    """Class for the relaxation data part of the BMRB API (v3.1)."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.__datanodes = datanodes

        # Initialise the kinetic saveframe supergroups.
        self.__general_relaxation = GeneralRelaxationSaveframe(self.datanodes)
