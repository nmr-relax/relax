#############################################################################
#                                                                           #
# The BMRB library.                                                         #
#                                                                           #
# Copyright (C) 2009-2013 Edward d'Auvergne                                 #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Module docstring.
"""The method saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#method
"""

# relax module imports.
from bmrblib.experimental_details.nmr_spectrometer import NMRSpectrometerSaveframe, NMRSpectrometer


class NMRSpectrometerSaveframe_v3_1(NMRSpectrometerSaveframe):
    """The NMR spectrometer saveframe class."""

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(NMRSpectrometer_v3_1(self))



class NMRSpectrometer_v3_1(NMRSpectrometer):
    """Base class for the NMRSpectrometer tag category."""

    def __init__(self, sf):
        """Setup the NMRSpectrometer tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(NMRSpectrometer_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'NMR_spectrometer'

        # Change tag names.
        self['SfCategory'].tag_name = 'Sf_category'
        self['SfFramecode'].tag_name = 'Sf_framecode'

        # Change the variable name.
        self['SfFramecode'].var_name = 'name'
