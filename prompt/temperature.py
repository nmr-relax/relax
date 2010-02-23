###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
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
"""Module containing the 'temperature' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import Basic_class
import arg_check
from generic_fns import temperature


class Temp(Basic_class):
    """Class containing the function for setting the experimental temperature."""

    def set(self, id=None, temp=None):
        """Specify the temperature of an experiment.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        id:  The experiment identification string.

        temp:  The temperature of the experiment.


        Description
        ~~~~~~~~~~~

        This function allows the temperature of an experiment to be set.  In certain analyses, for
        example those which use pseudocontact shift data, knowledge of the temperature is essential.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "temperature("
            text = text + "id=" + repr(id)
            text = text + ", temp=" + repr(temp) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(id, 'experiment identification string')
        arg_check.is_num(temp, 'experiment temparture')

        # Execute the functional code.
        temperature.set(id=id, temp=temp)
