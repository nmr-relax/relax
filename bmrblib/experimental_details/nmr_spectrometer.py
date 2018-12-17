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
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class NMRSpectrometerSaveframe(BaseSaveframe):
    """The NMR spectrometer saveframe class."""

    # Class variables.
    sf_label = 'spectrometer'

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(NMRSpectrometer(self))



class NMRSpectrometer(TagCategoryFree):
    """Base class for the NMRSpectrometer tag category."""

    def __init__(self, sf):
        """Setup the NMRSpectrometer tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(NMRSpectrometer, self).__init__(sf)

        # Add the tag info.
        self.add(key='NMRSpectrometerID',   tag_name='ID',              var_name='count_str')
        self.add(key='Details',             tag_name='Details',         var_name='details')
        self.add(key='Manufacturer',        tag_name='Manufacturer',    var_name='manufacturer')
        self.add(key='Model',               tag_name='Model',           var_name='model')
        self.add(key='SerialNumber',        tag_name='Serial_number',   var_name='serial_number')
        self.add(key='Field_strength',      tag_name='Field_strength',  var_name='frq')
