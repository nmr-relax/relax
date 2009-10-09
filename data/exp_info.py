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
"""Module holding the experimental information data container."""

# relax module imports.
from data_classes import ContainerList, Element


class ExpInfo(Element):
    """The experimental information data container."""

    def __init__(self):
        """Initialise the data container."""

        # The name of the container.
        self.element_name = 'exp_info'

        # The description of the container.
        self.element_desc = 'Experimental information'

        # Blacklisted objects.
        self.blacklist = ['software']


    def software_setup(self, name, url=None, version=None):
        """Set up the software information."""

        # Initialise the container if needed.
        if not hasattr(self, 'software'):
            self.software = SoftwareList()

        # Append a container.
        self.software.append(Software())

        # Set the attributes.
        self.software[-1].name = name
        if url:
            self.software[-1].url = url
        if version:
            self.software[-1].version = version



class SoftwareList(ContainerList):
    """The software data container list."""

    def __init__(self):
        """Initialise the data container."""

        # The name of the container.
        self.container_name = 'software_list'

        # The description of the container.
        self.container_desc = 'List of software programs used in the analysis'



class Software(Element):
    """The individual software data container."""

    def __init__(self):
        """Initialise the data container."""

        # The name of the container.
        self.element_name = 'software'

        # The description of the container.
        self.element_desc = 'Software program used in the analysis'



