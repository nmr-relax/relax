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
"""The v3.1 Heteronuclear NOE data saveframe category.

See http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_NOEs.
"""

# relax module imports.
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOESaveframe as HeteronuclNOESaveframeBase
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOEList as HeteronuclNOEListBase
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOEExperiment as HeteronuclNOEExperimentBase
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOESoftware as HeteronuclNOESoftwareBase
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOE as HeteronuclNOEBase


class HeteronuclNOESaveframe(HeteronuclNOESaveframeBase):
    """The v3.1 Heteronuclear NOE data saveframe class."""


class HeteronuclNOEList(HeteronuclNOEListBase):
    """v3.1 HeteronuclNOEList tag category."""

    # Tag names for the relaxation data.
    SfCategory = 'Sf_category'
    SampleConditionListLabel = 'Sample_condition_list_label'
    SpectrometerFrequency1H = 'Spectrometer_frequency_1H'


    def __init__(self, sf):
        """Initialise the v3.1 specific tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Execute the base class __init__() method.
        TagCategory.__init__(self, sf, tag_category_label='_Heteronucl_T2_list')


class HeteronuclNOEExperiment(HeteronuclNOEExperimentBase):
    """v3.1 HeteronuclNOEExperiment tag category."""

    # Tag names for experiment setup.
    SampleLabel = 'Sample_label'


class HeteronuclNOESoftware(HeteronuclNOESoftwareBase):
    """v3.1 HeteronuclNOESoftware tag category."""


class HeteronuclNOE(HeteronuclNOEBase):
    """v3.1 HeteronuclNOE tag category."""

