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
"""The v3.2 Heteronuclear NOE data saveframe category.

See http://www.bmrb.wisc.edu/dictionary/3.2html/SaveFramePage.html#heteronucl_NOEs.
"""

# relax module imports.
from bmrblib.misc import translate
from bmrblib.kinetics.heteronucl_NOEs_v3_1 import HeteronuclNOESaveframe_v3_1, HeteronuclNOEList_v3_1, HeteronuclNOEExperiment_v3_1, HeteronuclNOESoftware_v3_1, HeteronuclNOE_v3_1


class HeteronuclNOESaveframe_v3_2(HeteronuclNOESaveframe_v3_1):
    """The v3.2 Heteronuclear NOE data saveframe class."""

    def add(self, frq=None, res_nums=None, res_names=None, atom_names=None, isotope=None, data=None, errors=None, temp_calibration=None, temp_control=None):
        """Add relaxation data to the data nodes.

        @keyword frq:               The spectrometer proton frequency, in Hz.
        @type frq:                  float
        @keyword res_nums:          The residue number list.
        @type res_nums:             list of int
        @keyword res_names:         The residue name list.
        @type res_names:            list of str
        @keyword atom_names:        The atom name list.
        @type atom_names:           list of str
        @keyword isotope:           The isotope type list, ie 15 for '15N'.
        @type isotope:              list of int
        @keyword data:              The relaxation data.
        @type data:                 list of float
        @keyword errors:            The errors associated with the relaxation data.
        @type errors:               list of float
        @keyword temp_calibration:  The temperature calibration method.
        @type temp_calibration:     str
        @keyword temp_control:      The temperature control method.
        @type temp_control:         str
        """

        # Check the args.
        if not temp_calibration:
            raise NameError("The temperature calibration method has not been specified.")
        if not temp_control:
            raise NameError("The temperature control method has not been specified.")

        # Place the args into the namespace.
        self.temp_calibration = translate(temp_calibration)
        self.temp_control = translate(temp_control)

        # Execute the v3.1 add method.
        HeteronuclNOESaveframe_v3_1.add(self, frq=frq, res_nums=res_nums, res_names=res_names, atom_names=atom_names, isotope=isotope, data=data, errors=errors)


    def add_tag_categories(self):
        """Create the v3.2 tag categories."""

        # The tag category objects.
        self.heteronuclRxlist = HeteronuclNOEList_v3_1(self)
        self.heteronuclRxexperiment = HeteronuclNOEExperiment_v3_1(self)
        self.heteronuclRxsoftware = HeteronuclNOESoftware_v3_1(self)
        self.Rx = HeteronuclNOE_v3_1(self)
